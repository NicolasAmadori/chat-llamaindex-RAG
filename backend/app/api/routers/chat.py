from typing import List
import os

from fastapi.responses import StreamingResponse, Response

from app.utils.json import json_to_model
from app.utils.index import get_index
from app.api.routers.bot import get_bot_by_name
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index import VectorStoreIndex
from llama_index.llms import MessageRole, ChatMessage

from app.utils.interface import _ChatData

from llama_index.memory import ChatMemoryBuffer


from typing import Any

chat_router = r = APIRouter()

@r.post("")
async def chat(
    request: Request,
    # Note: To support clients sending a JSON object using content-type "text/plain",
    # we need to use Depends(json_to_model(_ChatData)) here
    data: _ChatData = Depends(json_to_model(_ChatData)),
    index: Any = None
):
    # check preconditions and get last message
    if len(data.messages) == 0 or data.bot_name == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided" if len(data.messages) == 0 else "No bot name provided",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )
    # convert messages coming from the request to type ChatMessage
    bot = get_bot_by_name(data.bot_name)
    index = get_index(bot)

    messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]
    # query chat engine

    memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

    #chat_engine = index.as_chat_engine(
    #    chat_mode="context",
    #    memory=memory,
    #    system_prompt=("You are a chatbot, able to have normal interactions, as well as answer user question based on the context provided.")
    #)
    #response = chat_engine.chat(lastMessage.content)#,messages)
    query_engine = index.as_query_engine()
    response = query_engine.query(lastMessage.content)
    with open('log_respone', 'w') as f:
        f.write('[Response] text: '+str(response)+'\n')
    response = response.response

    with open('log_respone', 'w') as f:
        f.write('[Response] text: '+response+'\n')   

    return Response(response, media_type="text/plain")
    """
    # stream response
    async def event_generator():    
        for token in response.response_gen:
            #print(token)
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
    """
