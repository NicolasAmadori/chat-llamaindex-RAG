import logging
import os
from typing import Any
from app.utils.model import *
import json
import gc

from llama_index.vector_stores import MilvusVectorStore
from llama_index import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    ServiceContext,
)
from llama_index.prompts import PromptTemplate

STORAGE_DIR = "./storage"  # directory to cache the generated index
DATA_DIR = "./data"  # directory containing the documents to index



vector_store = None # MilvusVectorStore(dim=768, overwrite=True)

def initialize_vector_store():
    global vector_store
    vector_store = MilvusVectorStore(dim=768, overwrite=True)


# one service context object for each bot_name
# service_contexts = {}

def get_index(bot): # TODO - decide if use the name or the index
    """
     Return a llamaindex index storage 
    """
    gc.collect()
    torch.cuda.empty_cache()
    logger = logging.getLogger("uvicorn")
    # check if storag   e already exists



    # TO fix
    service_context = create_service_context(bot)
    if not os.path.exists(STORAGE_DIR+"/"+bot.bot_name):
        logger.info("Creating new index")
        
        if not os.path.exists(DATA_DIR+"/"+bot.bot_name):
            os.makedirs(DATA_DIR+"/"+bot.bot_name)
        
        try:
            directory = SimpleDirectoryReader(DATA_DIR+"/"+bot.bot_name)
            logger.info(f"Loading data from {DATA_DIR+'/'+bot.bot_name}...")
            logger.info(f'[DIRECTORY]: {directory}')
            documents = directory.load_data()
            logger.info(f'[DOCUMENTS]: {documents}')
        except ValueError:
            logger.info(f"Empty data dir for bot {bot.bot_name}")
            documents = set()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, service_context=service_context)
        index.storage_context.persist(STORAGE_DIR+"/"+bot.bot_name)
        logger.info(f"Finished creating new index. Stored in {STORAGE_DIR+'/'+bot.bot_name}")
    else:
        #service_context = service_contexts[bot.bot_name]
        logger.info(f"Loading index from {STORAGE_DIR+'/'+bot.bot_name}...")
        storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=STORAGE_DIR+"/"+bot.bot_name)
        index = load_index_from_storage(storage_context,service_context=service_context)
        logger.info(f"Finished loading index from {STORAGE_DIR+'/'+bot.bot_name}")
    return index

