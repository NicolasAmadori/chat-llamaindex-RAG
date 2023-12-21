from typing import List, Any
import os
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

bots_list: List[_Bot] = []

@r.get("")
async def bots():
    return [(bot.bot_name, bot.model_name) for bot in bots_list]

@r.get("/available_models")
async def available_models():
    return [{"name": model.name, "modelcard": model.value} for model in _availableModels]

@r.post("")
async def create_bot(request: Request):

    try:
        data = await request.json()
        bot = data['bot']
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong body format",
        )
    
    if bot is None or None in [bot['bot_name'], bot['model_name'], bot['hide_context'], bot['context'], bot['model_config'], bot['bot_hello'], bot['data_source']]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No bot data provided",
        )
    
    id:str = str(random.randint(0, 1000000000))
    bot_name: str = bot['bot_name']
    model_name: str = bot['model_name']
    tokenizer_name: str = bot['model_name'] # check in the future
    hide_context: bool = bot['hide_context']
    context: List[_Message] = bot['context']
    config = bot['model_config']
    bot_hello: str = bot['bot_hello']
    data_source: str = bot['data_source']
    created_at: int = round(time()*1000)

    try:
        model_config: _LLMConfig = _LLMConfig(**config)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong model config format",
        )

    bot = _Bot(
        id=id,
        bot_name=bot_name,
        model_name=model_name,
        tokenizer_name=tokenizer_name,
        hideContext=hide_context,
        context=context,
        modelConfig=model_config,
        botHello=bot_hello,
        dataSource=data_source,
        createdAt=created_at
    )

    bots_list.append(bot)
    
    #index = get_index(bot)

    return {"id": id, "bot_name": bot_name, "model_name": model_name, "tokenizer_name": tokenizer_name, "hideContext": hide_context, "context": context, "modelConfig": model_config, "botHello": bot_hello, "dataSource": data_source, "createdAt": created_at}

@r.delete("")
async def delete_bot(
    request: Request,
    bot: str = None,
    index: Any = None
):
    print(f"[bot]: {bot}")
    # check preconditions and get last message
    if bot.bot_name == None or bot.model_name == None or bot.tokenizer_name == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )

    # convert messages coming from the request to type ChatMessage
    

def get_bot_by_name(bot_name: str) -> _Bot:
    for bot in bots_list:
        if bot.bot_name == bot_name:
            return bot
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Bot not found",
    )