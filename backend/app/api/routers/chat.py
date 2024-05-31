from fastapi.responses import Response
from app.utils.json import json_to_model
from app.utils.index import get_index
from app.api.routers.bot import get_bot_by_id
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index import VectorStoreIndex
from llama_index.llms import MessageRole, ChatMessage
from llama_index.response.notebook_utils import display_response

from app.utils.interface import _ChatData
from app.utils.model import add_message_to_store, add_response_to_store, get_role

from llama_index.memory import ChatMemoryBuffer

from typing import Any
import re, asyncio

import os

import logging

DATA_DIR = "./data"  # directory containing the documents to index

logger = logging.getLogger("uvicorn")

chat_router = r = APIRouter()

def create_engine(index: VectorStoreIndex, bot_id: str):
    memory = ChatMemoryBuffer.from_defaults(token_limit=5000)
    
    chat_mode = "simple"

    if len(os.listdir(f'{DATA_DIR}/{bot_id}')) > 1:
        chat_mode = "context"

    print("chat mode: ", chat_mode)

    chat_engine = index.as_chat_engine(chat_mode=chat_mode, memory=memory, similarity_top_k=3)
    return chat_engine


@r.post("")
async def chat(
    request: Request,
    # Note: To support clients sending a JSON object using content-type "text/plain",
    # we need to use Depends(json_to_model(_ChatData)) here
    data: _ChatData = Depends(json_to_model(_ChatData)),
    index: Any = None
):    
    
    # check preconditions and get last message
    if len(data.messages) == 0 or data.bot_id == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided" if len(data.messages) == 0 else "No bot id provided",
        )
    
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )
    # convert messages coming from the request to type ChatMessage
    bot = get_bot_by_id(data.bot_id)
    chat_engine = get_index(bot)

    # retrieve history
    messages = [
        ChatMessage(
            role=get_role(m.role),
            content=(m.content),
        )
        for m in data.messages
    ]

    bot.context = messages
    response, retrieved_tools = asyncio.run(chat_engine(lastMessage.content, chat_history=messages))

    res = response.response

    # if context.txt exists
    try:
        if os.path.isfile(f'./context.txt') and bot.hideContext == False:
            with open(f'./context.txt', 'r') as f:
                context_retrieved = f.read().splitlines()

            # get context used from context.txt
            with open(f'./context.txt', 'r') as f:
                context_retrieved = f.read().splitlines()
            

            res = res+"\n\n\n Context used:\n\n"
            
            #print("context retrieved: ", context_retrieved)
            for c in context_retrieved:
                res += c+"\n\n"

            regex = '(page_label: \d+ file_path: \S+)'  
            split_message = re.split(regex, res)
            split_message = [x for x in split_message if x != '' or x != '\n']
            
            to_remove = 'file_path: data\/\w+\/'
            split_message = [re.sub(to_remove, 'file: ', x) for x in split_message]
            
            res = "\n".join(split_message)

            os.remove(f'./context.txt')
    except:
        print("Exception retrieving context")

    add_message_to_store(data.bot_id, lastMessage)
    add_response_to_store(data.bot_id, response)

    return Response(res, media_type="text/plain")