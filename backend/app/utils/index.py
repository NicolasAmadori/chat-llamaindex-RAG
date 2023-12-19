import logging
import os
import torch
from typing import Any

device = "cuda:0" if torch.cuda.is_available() else "cpu"

# from llama_index.vector_stores import MilvusVectorStore
from llama_index import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    ServiceContext,
)
from llama_index.prompts import PromptTemplate
from llama_index.llms import OpenAI

STORAGE_DIR = "./storage"  # directory to cache the generated index
DATA_DIR = "./data"  # directory containing the documents to index

from llama_index.llms import HuggingFaceLLM


from transformers import AutoModelForCausalLM, AutoTokenizer

from llama_index.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)

from llama_index.llms.base import llm_completion_callback

class OurLLM(CustomLLM):
    model: Any = None
    tokenizer: Any = None
    device: Any = None
    model_name: str = None
    context_window: int = None
    num_output: int = None

    def __init__(self, model_name, device):
      super().__init__()
      self.model_name = model_name
      self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", trust_remote_code=True)
      self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
      self.device = device

      self.context_window = 2048
      self.num_output = 256

      self.model.to(device)


    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to(self.device)
        outputs = self.model.generate(**inputs, max_length=600)
        text = self.tokenizer.batch_decode(outputs)[0]

        return CompletionResponse(text=text)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs
    ) -> CompletionResponseGen:
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to(self.device)
        outputs = self.model.generate(**inputs, max_length=600)
        text = self.tokenizer.batch_decode(outputs)[0]

        yield CompletionResponse(text=text, delta=text)
 
llm = OurLLM("microsoft/phi-1_5", device)

# SYSTEM_PROMPT = """You are an AI assistant that answers questions in a friendly manner, based on the given source documents. Here are some rules you always follow:
# - Generate human readable output, avoid creating output with gibberish text.
# - Generate only the requested output, don't include any other language before or after the requested output.
# - Never say thank you, that you are happy to help, that you are an AI agent, etc. Just answer directly.
# - Generate professional language typically used in business documents in North America.
# - Never generate offensive or foul language.
# """
# query_wrapper_prompt = PromptTemplate(" {query_str}\nAnswer: ")
# HuggingFaceLLM(
#     context_window=2048,
#     max_new_tokens=256,
#     generate_kwargs={"temperature": 0.9, "do_sample": True},
#     system_prompt=SYSTEM_PROMPT,
#     query_wrapper_prompt=query_wrapper_prompt,
#     tokenizer_name="microsoft/phi-1_5",
#     model_name="microsoft/phi-1_5",
#     device_map="cuda:0",
#     #stopping_ids=[50278, 50279, 50277, 1, 0],
#     tokenizer_kwargs={"max_length": 2048},
#     # uncomment this if using CUDA to reduce memory usage
#     model_kwargs={"torch_dtype": torch.float16, "trust_remote_code": True}
# )

service_context = ServiceContext.from_defaults(
    chunk_size=1024,
    embed_model="local:BAAI/bge-base-en-v1.5",
    llm=llm,
)

def get_index(bot):
    logger = logging.getLogger("uvicorn")
    # check if storage already exists
    if not os.path.exists(STORAGE_DIR):
        logger.info("Creating new index")
        # load the documents and create the index
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents, service_context=service_context)
        # store it for later
        index.storage_context.persist(STORAGE_DIR)
        logger.info(f"Finished creating new index. Stored in {STORAGE_DIR}")
    else:
        # load the existing index
        logger.info(f"Loading index from {STORAGE_DIR}...")
        #vector_store = MilvusVectorStore(dim=1536, overwrite=True)
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context,service_context=service_context)
        logger.info(f"Finished loading index from {STORAGE_DIR}")
    return index
