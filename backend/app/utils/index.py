import logging
import os
from app.utils.model import *
import gc
import torch

from llama_index.vector_stores import MilvusVectorStore
from llama_index import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
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

    if not os.path.exists(STORAGE_DIR+"/"+bot.bot_id) or bot.bot_id in bots_to_refresh:
        
        if bot.bot_id in bots_to_refresh:
            logger.info(f"Refreshing index for bot {bot.bot_id}")
            # To remove all the occurences in case the bot is in the list more than once
            bots_to_refresh[:] = [bot_id for bot_id in bots_to_refresh if bot_id != bot.bot_id]
        else:
            logger.info("Creating new index")

        directory = SimpleDirectoryReader(DATA_DIR+"/"+bot.bot_id)
        documents = directory.load_data()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, service_context=service_context)
        logger.info(f"Created index")
        index.storage_context.persist(STORAGE_DIR+"/"+bot.bot_id)
        logger.info(f"Finished creating new index. Stored in {STORAGE_DIR+'/'+bot.bot_id}")
    else:
        #service_context = service_contexts[bot.bot_id]
        logger.info(f"Loading index from {STORAGE_DIR+'/'+bot.bot_id}...")
        storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=STORAGE_DIR+"/"+bot.bot_id)
        index = load_index_from_storage(storage_context, service_context=service_context)
        logger.info(f"Finished loading index from {STORAGE_DIR+'/'+bot.bot_id}")
        
    return index

def add_bot_to_refresh(bot_id: str):
    """
    Add a bot to the list of bots to refresh
    """
    bots_to_refresh.append(bot_id)
