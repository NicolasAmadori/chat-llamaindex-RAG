import torch

from llama_index import Document
from llama_index.schema import TextNode
from llama_index.embeddings import LangchainEmbedding
from llama_index.llms import HuggingFaceLLM

from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig,
)

from langchain.embeddings.huggingface import HuggingFaceEmbeddings

# import from configuration module
from project_config import (
    HUGGINFACE_ACCESS_TOKEN,
    LLM_ID,
    LLM_CACHE_DIR,
    EMBED_MODEL_ID,
    EMBED_MODEL_CACHE_DIR,
    MAX_NEW_TOKENS,
)



DEVICE = "cuda" if torch.cuda.device_count() > 0 else "cpu"



def get_llm_model(quantization=False):
    tokenizer = AutoTokenizer.from_pretrained(
        LLM_ID,
        cache_dir=LLM_CACHE_DIR,
        token=HUGGINFACE_ACCESS_TOKEN,
    )

    bnb_config = None
    if quantization:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True, 
            bnb_4bit_use_double_quant=True, 
            bnb_4bit_quant_type="nf4", 
            bnb_4bit_compute_dtype=torch.bfloat16
        )

    model = AutoModelForCausalLM.from_pretrained(
        LLM_ID,
        cache_dir=LLM_CACHE_DIR,
        token=HUGGINFACE_ACCESS_TOKEN,
        torch_dtype=torch.bfloat16,
        device_map=DEVICE,
        quantization_config=bnb_config,
    )

    custom_model_config = {
        'model_kwargs' : {
            'verbose' : True,
            'temperature' : 0,
            'max_new_tokens' : MAX_NEW_TOKENS,
            "n_gpu_layers": 100,
            "device" : DEVICE,
            "stop" : ['[|Umano|]', '[|AI|]', '[end of text]'],
        }
    }
    llm = HuggingFaceLLM(
        model=model,
        tokenizer=tokenizer,
        context_window=8192,
        **custom_model_config,
    )
    return llm, tokenizer


def get_embed_model():
    embed_model_kwargs = {'device': DEVICE}
    encode_kwargs = {'normalize_embeddings': True}
    embeddings = LangchainEmbedding(
        HuggingFaceEmbeddings(
            model_name=EMBED_MODEL_ID,
            cache_folder=EMBED_MODEL_CACHE_DIR,
            model_kwargs=embed_model_kwargs,
            encode_kwargs=encode_kwargs
        )
    )
    return embeddings


def get_speeches_nodes(df):
    nodes = []
    for index, row in df.iterrows():
        node = Document(text=row["formatted_data"], id_=index)
        nodes.append(node)
    return nodes


def get_acts_nodes(df):
    nodes = []
    for act_id, act in df.iterrows():
        node = Document(
                text='\n'.join(act["doc_pages"]),
                id_=f"ACT_{act_id}",
                metadata={
                    "id": f"ACT_{act_id}",
                    "title": act["title"],
                    "number_of_pages": len(act["doc_pages"])
                }
        )
        nodes.append(node)
    return nodes
