from typing import Dict
import os
import shutil
import json

from time import time

from fastapi import APIRouter, HTTPException, Request, status

from app.utils.interface import _Bot, _availableModels, _LLMConfig
from app.utils.model import store_bot, remove_bot_from_store

import logging
logger = logging.getLogger('uvicorn')

bot_router = r = APIRouter()

STORAGE_DIR = "./storage"
DATA_DIR = "./data"
BOT_STORE_FILE = './bot_store.json'
BOT_PARAMS = ['bot_name', 'model_name', 'hide_context', 'context', 'model_config', 'bot_hello', 'data_source']

bots_list: Dict[str, _Bot] = {}

@r.on_event("startup")
async def startup_event():
    # Create bot store file if it does not exist
    if not os.path.exists(BOT_STORE_FILE):
        print("Creating bot store")
        with open(BOT_STORE_FILE, 'w') as f:
            f.write("{}")
    else:
        # Check if the bot store file is corrupted
        try:
            with open(BOT_STORE_FILE, 'r') as f:
                _ = json.load(f)
        except Exception as e:
            print("Bot store file corrupted, creating new one")
            with open(BOT_STORE_FILE, 'w') as f:
                f.write("{}")

    # Create bot store if file does not exist
    if not os.path.exists(BOT_STORE_FILE):
        with open(BOT_STORE_FILE, 'w') as f:
            f.write("{}")

    # Clear the storage dir on startup
    if os.path.exists(STORAGE_DIR):
        print("Clearing storage dir")
        shutil.rmtree(STORAGE_DIR)

    os.mkdir(STORAGE_DIR)

    # TODO: for loop to create the bots from the bot_store file
    with open(BOT_STORE_FILE, 'r') as f:
        bots = json.load(f)
        for bot_id, bot in bots.items():
            config = bot['modelConfig']
            model_config: _LLMConfig = _LLMConfig(**config)
            params = {
                'bot_id' : bot_id,
                'bot_name' : bot['bot_name'],
                'model_name' : bot['model_name'],
                'tokenizer_name' : bot['model_name'], # check in the future
                'hideContext': bot['hideContext'],
                'context': bot['context'],
                'modelConfig': model_config,
                'botHello': bot['botHello'],
                'dataSource': bot['dataSource'],
                'createdAt' : round(time()*1000)
            }
            # logger.info(f'bot context: {bot["context"][:2]}')
            bot = _Bot(**params)
            bots_list[bot_id] = bot
    
    available_bosts_ids = list(bots_list.keys())
    if not os.path.exists(DATA_DIR):
        print("Creating data dir")
        os.mkdir(DATA_DIR)
    
    # scan of data dir to check if there are bots that are not in the bot store
    for bot_id in os.listdir(DATA_DIR):
        if bot_id not in available_bosts_ids:
            print(f"Found bot {bot_id} not in bot store, deleting")
            shutil.rmtree(DATA_DIR+"/"+bot_id)



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
        'tokenizer_name' : bot['model_name'],
        'hideContext': bot['hide_context'],
        'context': bot['context'],
        'modelConfig': model_config,
        'botHello': bot['bot_hello'],
        'dataSource': bot['data_source'],
        'createdAt' : round(time()*1000)
    }
    
    bot = _Bot(**params)

    bots_list[bot_id] = bot
    store_bot(bot)

    # Create the data folder for the bot
    if not os.path.exists(DATA_DIR+"/"+bot_id):
        os.makedirs(DATA_DIR+"/"+bot_id)

    # Store a file with the context of the bot
    with open(f'{DATA_DIR}/{bot_id}/empty.txt', 'w') as f:
        f.write("")
        for message in bot.context:
            f.write(str(message)+'\n')
    
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
        remove_bot_from_store(bot_id)
        
        if os.path.exists(STORAGE_DIR+"/"+bot_id):
            shutil.rmtree(STORAGE_DIR+"/"+bot_id)
        if os.path.exists(DATA_DIR+"/"+bot_id):
            shutil.rmtree(DATA_DIR+"/"+bot_id)
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