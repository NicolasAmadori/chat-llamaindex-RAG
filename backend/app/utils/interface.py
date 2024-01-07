from pydantic import BaseModel
from typing import List
from enum import Enum
from llama_index.llms import MessageRole
from time import time

class _availableModels(Enum):
    cerbero_chat = "galatolo/cerbero-7b"
    mistral = "mistralai/Mistral-7B-Instruct-v0.1"
    zephir = 'HuggingFaceH4/zephyr-7b-beta'
    tinyllama = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
    dolphin = 'cognitivecomputations/dolphin-2.6-mistral-7b-dpo'
    llama = 'meta-llama/Llama-2-7b-chat-hf'
    

class _Message(BaseModel):
    role: MessageRole
    # date is default as now
    date: int = round(time()*1000)
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]
    bot_id: str

class _LLMConfig(BaseModel):
    model_name: _availableModels
    temperature: float
    topP: int
    sendMemory: bool
    maxTokens: int
    maxHistory: int

class _Bot(BaseModel):
    bot_id: str
    bot_name: str
    model_name: _availableModels
    tokenizer_name: str
    hideContext: bool
    context: List[_Message]
    modelConfig: _LLMConfig
    botHello: str
    dataSource: str
    createdAt: int