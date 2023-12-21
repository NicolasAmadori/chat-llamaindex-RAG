import logging
import os
from typing import Any
from app.utils.model import *
import json

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



# one service context object for each bot_name
service_contexts = {}

def get_index(bot): # TODO - decide if use the name or the index
    """
     Return a llamaindex index storage 
    """
    vector_store = MilvusVectorStore(dim=1536, overwrite=True)
    logger = logging.getLogger("uvicorn")
    # check if storage already exists

    # TO fix
    if not os.path.exists(STORAGE_DIR+"/"+bot.bot_name):
        
        if not os.path.exists(DATA_DIR+"/"+bot.bot_name):
            os.makedirs(DATA_DIR+"/"+bot.bot_name)

        logger.info("Creating new index")
        service_context = create_service_context(bot)
        service_contexts[bot.bot_name] = service_context
        
        if len(os.listdir(DATA_DIR+"/"+bot.bot_name)) > 0:
            documents = SimpleDirectoryReader(DATA_DIR+"/"+bot.bot_name).load_data() 
        else:
            documents = []
               
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, service_context=service_context)
        index.storage_context.persist(STORAGE_DIR+"/"+bot.bot_name)
        logger.info(f"Finished creating new index. Stored in {STORAGE_DIR+'/'+bot.bot_name}")
    else:
        service_context = service_contexts[bot.bot_name]
        logger.info(f"Loading index from {STORAGE_DIR+'/'+bot.bot_name}...")
        storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=STORAGE_DIR+"/"+bot.bot_name)
        index = load_index_from_storage(storage_context,service_context=service_context)
        logger.info(f"Finished loading index from {STORAGE_DIR+'/'+bot.bot_name}")
    return index
