from typing import List
import os

from fastapi.responses import StreamingResponse, Response
from llama_index.prompts import PromptTemplate
from app.utils.json import json_to_model
from app.utils.index import get_index
from app.api.routers.bot import get_bot_by_id
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index import VectorStoreIndex
from llama_index.llms import MessageRole, ChatMessage

from app.utils.interface import _ChatData

from llama_index.memory import ChatMemoryBuffer


from typing import Any

import logging

logger = logging.getLogger("uvicorn")

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
    
    messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]

    #memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

    memory = ChatMemoryBuffer.from_defaults(token_limit=3900)
    chat_engine = index.as_chat_engine(
        chat_mode="condense_plus_context",
        memory=memory,
        context_prompt=(
            "You are a chatbot, able to have normal interactions, as well as talk"
            # " about an essay discussing Paul Grahams life."
            "Here are the relevant documents for the context:\n"
            "{context_str}"
            "\nInstruction: Use the previous chat history, or the context above, to interact and help the user."
        ),
        verbose=False,
    )

    response = chat_engine.chat(lastMessage.content, messages)

    # New propmpt
    # custom_prompt_str = (
    #    "Context information is below.\n"
    #    "---------------------\n"
    #    "{context_str}\n"
    #    "---------------------\n"
    #    "Given the context information and prior knowledge, answer the following question.\n"
    #    "Query: {query_str}\n"
    #    "Answer: "
    # )
    # custom_prompt = PromptTemplate(custom_prompt_str)
    # query_engine = index.as_query_engine(response_mode="compact")
    # query_engine.update_prompts(
    #     {"response_synthesizer:text_qa_template": custom_prompt}
    # )
    # response = query_engine.query(lastMessage.content, messages)
    
    response = response.response

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
