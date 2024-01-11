from fastapi.responses import Response
from app.utils.json import json_to_model
from app.utils.index import get_index
from app.api.routers.bot import get_bot_by_id
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index import VectorStoreIndex
from llama_index.llms import MessageRole, ChatMessage

from app.utils.interface import _ChatData
from app.utils.model import add_message_to_store, add_response_to_store, get_role

from llama_index.memory import ChatMemoryBuffer

from typing import Any

import logging

DATA_DIR = "./data"  # directory containing the documents to index

logger = logging.getLogger("uvicorn")

chat_router = r = APIRouter()

def create_engine(index: VectorStoreIndex):
    memory = ChatMemoryBuffer.from_defaults(token_limit=5000)
    
    custom_prompt = """
         You are a chatbot, able to have normal interactions, as well as talk. You should also keep trace of all the information provided by the user, and use it to answer to any question.
    """

    chat_engine = index.as_chat_engine(chat_mode='context', system_prompt=custom_prompt, memory=memory) #, )
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
    index = get_index(bot)

    # retrieve history
    messages = [
        ChatMessage(
            role=get_role(m.role),
            content=(m.content),
        )
        for m in data.messages
    ]

    bot.context = messages

    # write messages to ./DATA/bot_id/empty.txt
    # with open(f'{DATA_DIR}/{bot.bot_id}/empty.txt', 'w') as f:
    #     f.write("")
    #     for message in messages:
    #         f.write(str(message)+'\n')

    chat_engine = create_engine(index)
    
    response = chat_engine.chat(lastMessage.content, chat_history=messages)
    
    add_message_to_store(data.bot_id, lastMessage)
    add_response_to_store(data.bot_id, response)

    return Response(response.response, media_type="text/plain")