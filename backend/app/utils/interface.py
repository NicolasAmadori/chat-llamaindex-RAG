from pydantic import BaseModel
from typing import List, Any
from enum import Enum
from llama_index.llms import MessageRole, ChatMessage

class _availableModels(Enum):
    phi_1_5 = "microsoft/phi-1_5"
    phi_2 = "microsoft/phi-2"
    mistral = "mistralai/Mistral-7B-Instruct-v0.1"
    llama = "meta-llama/Llama-2-7b"
    mixtral = "TheBloke/Llama-2-7b-Chat-GPTQ:gptq-4bit-64g-actorder_True"

class _Message(BaseModel):
    role: MessageRole
    date: int
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]
    bot_name: str

class _LLMConfig(BaseModel):
    model_name: _availableModels
    temperature: float
    topP: int
    sendMemory: bool
    maxTokens: int
    maxHistory: int

class _Bot(BaseModel):
    id: str
    bot_name: str
    model_name: _availableModels
    tokenizer_name: str
    hideContext: bool
    context: List[_Message]
    modelConfig: _LLMConfig
    botHello: str
    dataSource: str
    createdAt: int