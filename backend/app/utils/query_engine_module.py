import asyncio
import os, pickle
from tqdm.notebook import tqdm
from pathlib import Path

# >> Llama-Index
from llama_index import (
    VectorStoreIndex, 
    load_index_from_storage, 
    StorageContext, 
    SummaryIndex,
)
from llama_index.objects import (
    ObjectIndex,
    SimpleToolNodeMapping,
    ObjectRetriever,
)
from llama_index.agent import ReActAgent
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.node_parser import SentenceSplitter
from llama_index.query_engine import SubQuestionQueryEngine
from llama_index.postprocessor import PrevNextNodePostprocessor
from llama_index.indices.query.query_transform.base import HyDEQueryTransform
from llama_index.query_engine.transform_query_engine import TransformQueryEngine



class CustomObjectRetriever(ObjectRetriever):
    def __init__(
            self, 
            retriever, 
            object_node_mapping, 
            llm, 
            service_context,
    ):
        self._retriever = retriever
        self._object_node_mapping = object_node_mapping
        self._llm = llm
        self._service_context = service_context
        self.retrieved_nodes = []

    def retrieve(self, query_bundle):
        nodes = self._retriever.retrieve(query_bundle)
        tools = [self._object_node_mapping.from_node(n.node) for n in nodes]
        self.retrieved_nodes = nodes

        sub_question_engine = SubQuestionQueryEngine.from_defaults(
            query_engine_tools=tools, service_context=self._service_context
        )
        sub_question_description = f"""\
Useful for any queries that involve comparing multiple documents. ALWAYS use this tool for comparison queries - make sure to call this \
tool with the original query. Do NOT use the other tools for any queries involving multiple documents.
"""

        sub_question_tool = QueryEngineTool(
            query_engine=sub_question_engine,
            metadata=ToolMetadata(
                name="compare_tool", description=sub_question_description
            ),
        )
        return tools + [sub_question_tool]
    


async def build_agent_per_doc(nodes, file_base, service_context, summary=False):
    vi_out_path = f"./data/llamaindex_docs/{file_base}"
    summary_out_path = f"./data/llamaindex_docs/{file_base}_summary.pkl"

    if not os.path.exists(vi_out_path):
        Path("./data/llamaindex_docs/").mkdir(parents=True, exist_ok=True)
        # build vector index
        vector_index = VectorStoreIndex(nodes, service_context=service_context)
        vector_index.storage_context.persist(persist_dir=vi_out_path)
    else:
        vector_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=vi_out_path),
            service_context=service_context
        )

    summary_index = SummaryIndex(nodes, service_context=service_context)
    
    # define query engines
    vector_query_engine = vector_index.as_query_engine(
        node_postprocessors=[
            PrevNextNodePostprocessor(
                docstore=vector_index.docstore,
                mode="both",
                num_nodes=4,
            ),
        ],
    )
    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize", 
        use_async=True, 
    )

    # extract a summary
    if not os.path.exists(summary_out_path):
        Path(summary_out_path).parent.mkdir(parents=True, exist_ok=True)
        if not summary:
            print("\nQUERING DOCUMENT SUMMARY...")
            summary = str(
                await summary_query_engine.aquery(
                    "Extract from the first/second page of the document the name (consist of date and number) of the inner law."
                    "\nYou have to specify also the general purpose of this parliamentary act. You have to be concise."
                    "\nDo not add your own explanations or comments to the answer."
                )
            )
        pickle.dump(summary, open(summary_out_path, "wb"))
    else:
        print("\nLoading document summary.")
        summary = pickle.load(open(summary_out_path, "rb"))

    # define tools
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name=f"vector_tool_{file_base}",
                description=f"Useful for questions related to specific facts",
            ),
        ),
        QueryEngineTool(
            query_engine=summary_query_engine,
            metadata=ToolMetadata(
                name=f"summary_tool_{file_base}",
                description=f"Useful for summarization questions",
            ),
        ),
    ]

    # build agent
    agent = ReActAgent.from_tools(
        query_engine_tools,
        llm=service_context.llm,
        verbose=True,
        max_iterations=80,
        system_prompt=f"""\
You are a specialized agent designed to answer queries about the `{file_base}` part of the LlamaIndex docs.
You must ALWAYS use at least one of the tools provided when answering a question; do NOT rely on prior knowledge.
\nNote: when you work on a Chamber's documents you should read all the act's pages that are related to the user question.
Within the pages of the documents the character "|" is the column separator. If a page contain the actual text of the law with the respective articles, and that page is written in two columns, you should consider the two columns as separeted mirrored text.
The left collumn ALWAYS contains ONLY the originally proposed text of the law, while the right collumn ALWAYS contains ONLY the equivalent of the left column but in the finally modified and approved version of the law.\
""",
    )
    return agent, summary


async def build_agents(docs, service_context):
    node_parser = SentenceSplitter(
        chunk_size=1024,
        chunk_overlap=100,
    )

    agents_dict = {}
    extra_info_dict = {}
    for idx, doc in enumerate(tqdm(docs)):
        nodes = node_parser.get_nodes_from_documents([doc])

        file_path = Path(doc.metadata["id"])
        file_base = str(file_path.parent.stem) + str(file_path.stem)

        print(f"ACT DOCUMENT n.{idx+1}: {file_base}\n")
        agent, summary = await build_agent_per_doc(
            nodes, file_base, service_context,
        )
        print("-"*50)

        agents_dict[file_base] = agent
        extra_info_dict[file_base] = {"summary": summary, "nodes": nodes}

    return agents_dict, extra_info_dict


async def build_speeches_agent(nodes, service_context):
    description = """\
The Italian Parliament discusses various topics.   Context information from multiple sources is below.  --  The document apppears to be a collection of transcript of speeches and statements made by Italian politicians in the Chamber of Deputies regarding all chamber activities and sessions.\
  --  The document is a transcript of every session in the Italian Chamber of Deputies, where several politicians discuss.  --  This is the only part of LlamaIndex docs related to parliamentary speeches. You DO NOT NEED any other documents retrieve informations about speeches\
  --  The document apppears to be a collection of transcript of speeches and statements made by Italian politicians in the Chamber of Deputies regarding all chamber activities and sessions.\
  --  The document is a transcript of every session in the Italian Chamber of Deputies, where several politicians discuss.  --  This is the only part of LlamaIndex docs related to parliamentary speeches. You DO NOT NEED any other documents retrieve informations about speeches\
  --  The document apppears to be a collection of transcript of speeches and statements made by Italian politicians in the Chamber of Deputies regarding all chamber activities and sessions.\
  --  The document is a transcript of every session in the Italian Chamber of Deputies, where several politicians discuss.  --  This is the only part of LlamaIndex docs related to parliamentary speeches. You DO NOT NEED any other documents retrieve informations about speeches."""
    
    file_path = Path("speeches")
    file_base = str(file_path.parent.stem) + str(file_path.stem)

    node_parser = SentenceSplitter(
        chunk_size=1024,
        chunk_overlap=100,
    )
    nodes = node_parser.get_nodes_from_documents(nodes)

    print("\nSpeeches\n")
    agent, summary = await build_agent_per_doc(
        nodes, file_base, service_context, summary=description,
    )
    print("-"*50)

    return agent, summary


async def get_query_engine(all_tools, service_context):
    tool_mapping = SimpleToolNodeMapping.from_objects(all_tools)
    obj_index = ObjectIndex.from_objects(
        all_tools,
        tool_mapping,
        VectorStoreIndex,
        service_context=service_context,
    )

    custom_obj_retriever = CustomObjectRetriever(
        retriever=obj_index.as_node_retriever(similarity_top_k=15), 
        object_node_mapping=tool_mapping, 
        llm=service_context.llm, 
        service_context=service_context,
    )

    top_agent = ReActAgent.from_tools(
        tool_retriever=custom_obj_retriever,
        system_prompt=""" \
You are an agent designed to answer queries about the documentation, using the italian language.
You are a helpful, respectful and honest, helping the parlamentarians of the italian Chamber of Deputies. Your role is to support the work of preparing legislative proposals, and guidance and control acts.
Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
Always answer as helpfully as possible, while being safe. Make sure you always use the italian language.\

""",
        llm=service_context.llm,
        verbose=True,
        max_iterations=80,
    )
    async def query_wrapper(message, chat_history):
        response = await top_agent.achat(message, chat_history=chat_history)
        retrieved_nodes = custom_obj_retriever.retrieved_nodes

        return response, retrieved_nodes

    return query_wrapper

async def run_query(query_engine, query):
    response, retrieved_tools = await query_engine(query)
    return response, retrieved_tools


def get_tools(acts_nodes, speeches_nodes, service_context):
    acts_agents_dict, acts_extra_info_dict = asyncio.run(
        build_agents(acts_nodes, service_context)
    )
    speeches_agent, speeches_summary = asyncio.run(
        build_speeches_agent(speeches_nodes, service_context)
    )

    hyde = HyDEQueryTransform(include_original=True, llm=service_context.llm)
    all_tools = []
        
    for file_base, agent in acts_agents_dict.items():
        summary = acts_extra_info_dict[file_base]["summary"]
        agent = TransformQueryEngine(agent, query_transform=hyde)
        doc_tool = QueryEngineTool(
            query_engine=agent,
            metadata=ToolMetadata(
                name=f"tool_{file_base}",
                description=summary,
            ),
        )
        all_tools.append(doc_tool)

    speeches_tool = QueryEngineTool(
        query_engine=TransformQueryEngine(speeches_agent, query_transform=hyde),
        metadata=ToolMetadata(
            name=f"tool_speeches",
            description=speeches_summary,
        ),
    )
    all_tools.append(speeches_tool)

    return all_tools
