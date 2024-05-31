import logging, asyncio
import os
from app.utils.model import *
import gc
import torch

from llama_index.vector_stores import MilvusVectorStore
from llama_index import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage
)
from query_engine_module import (
    get_tools,
    get_query_engine,
    run_query,
)

from app.utils.model import create_service_context

STORAGE_DIR = "./storage"  # directory to cache the generated index
DATA_DIR = "./data"  # directory containing the documents to index

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

vector_store = None

def initialize_vector_store():
    global vector_store
    vector_store = MilvusVectorStore(dim=768, overwrite=True)

current_bot_id = None
service_context = None
bots_to_refresh = []
    

def get_index(bot): # TODO - decide if use the name or the index
    """
     Return a llamaindex index storage 
    """
    global current_bot_id
    global service_context
    global vector_store
    
    logger = logging.getLogger("uvicorn")


    # If there is no current bot or the current bot is different from the bot passed as parameter
    if current_bot_id is None or current_bot_id != bot.bot_id:
        del service_context
        gc.collect()
        torch.cuda.empty_cache()
        current_bot_id = bot.bot_id
        service_context = create_service_context(bot)

        acts_nodes = get_acts_nodes(bot.df_acts)
        speeches_nodes = get_speeches_nodes(bot.df_speeches)

        all_tools = get_tools(
            acts_nodes=acts_nodes,
            speeches_nodes=speeches_nodes,
            service_context=service_context
        )


        print("\nGetting query engine...\n")
        query_engine = asyncio.run(get_query_engine(all_tools, service_context))
        
    return query_engine

def add_bot_to_refresh(bot_id: str):
    """
    Add a bot to the list of bots to refresh
    """
    bots_to_refresh.append(bot_id)
