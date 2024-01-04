from typing import List, Any, Dict
import os
import shutil
import psutil
import json

import random
from time import time
from fastapi.responses import StreamingResponse

from app.utils.json import json_to_model
from app.utils.index import get_index
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index import VectorStoreIndex
from llama_index.llms import MessageRole, ChatMessage
from pydantic import BaseModel

from app.utils.interface import _Bot, _Message, _availableModels, _LLMConfig

bot_router = r = APIRouter()

STORAGE_DIR = "./storage"  # directory to cache the generated index
DATA_DIR = "./data"  # directory containing the documents to index
BOT_PARAMS = ['bot_name', 'model_name', 'hide_context', 'context', 'model_config', 'bot_hello', 'data_source']

bots_list: Dict[str, _Bot] = {}

@r.on_event("startup")
async def startup_event():
    # Clear the storage dir on startup
    if os.path.exists(STORAGE_DIR):
        print("Clearing storage dir")
        shutil.rmtree(STORAGE_DIR)

    os.mkdir(STORAGE_DIR)

    data_folder = "./data"
    if os.path.exists(data_folder):
       print("Clearing data dir")
       shutil.rmtree(data_folder)
    
    os.mkdir(data_folder)


@r.get("")
async def bots():
    return [{'id':bot.bot_id,'name': bot.bot_name, 'model':bot.model_name, "config": bot.modelConfig} for bot in bots_list.values()]

@r.get("/available_models")
async def available_models():
    return [{"name": model.name, "modelcard": model.value} for model in _availableModels]

@r.post("")
async def create_bot(request: Request):
    try:
        data = await request.json()
        bot = data['bot']
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong body format, error {e}",
        )
    # if bot is None or None in [bot['bot_name'], bot['model_name'], bot['hide_context'], bot['context'], bot['model_config'], bot['bot_hello'], bot['data_source']]:
    if bot is None or (set(BOT_PARAMS) & set(bot.keys()) != set(BOT_PARAMS)): 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No bot data provided",
        )
        
    if bot['model_name'] not in [model.value for model in _availableModels]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model {bot['model_name']} not available",
        )

    bot_id = bot["bot_id"]

    if bot_id in bots_list.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bot id {bot_id} already exists",
        )

    try:
        config = bot['model_config']
        model_config: _LLMConfig = _LLMConfig(**config)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong model config format, error {e}",
        )

    params = {
        'bot_id' : bot_id,
        'bot_name' : bot['bot_name'],
        'model_name' : bot['model_name'],
        'tokenizer_name' : bot['model_name'], # check in the future
        'hideContext': bot['hide_context'],
        'context': bot['context'],
        'modelConfig': model_config,
        'botHello': bot['bot_hello'],
        'dataSource': bot['data_source'],
        'createdAt' : round(time()*1000)
    }
    
    

    bot = _Bot(**params)

    bots_list[bot_id] = bot

    # Create the data folder for the bot
    if not os.path.exists(DATA_DIR+"/"+bot_id):
        os.makedirs(DATA_DIR+"/"+bot_id)

    with open(f'{DATA_DIR}/{bot_id}/empty.txt', 'w') as f:
        f.write("")
        for message in bot.context:
            f.write(str(message)+'\n')
    
    #index = get_index(bot)

    return {"message": "Bot created", "bot": bot}

@r.delete("")
async def delete_bot(request: Request):
    try:
        data = await request.json()
        bot_id = data['bot_id']
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong body format, error {e}",
        )
    # check preconditions and get last message
    if bot_id == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid bot id provided"
        )

    try:
        del bots_list[bot_id]
        
        if os.path.exists(STORAGE_DIR+"/"+bot_id):
            shutil.rmtree(STORAGE_DIR+"/"+bot_id)

        return {"message": "Bot deleted"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bot not found, error {e}",
        )
    

def get_bot_by_id(bot_id: str) -> _Bot:
    for id, bot in bots_list.items():
        if id == bot_id:
            return bot
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Bot not found",
    )