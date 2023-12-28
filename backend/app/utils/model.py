from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Any
import logging
import torch
from llama_index.llms.base import llm_completion_callback
from app.utils.interface import _Bot, _availableModels, _LLMConfig
from llama_index import ServiceContext

device = "cuda:0" if torch.cuda.is_available() else "cpu"
logger = logging.getLogger("uvicorn")

from llama_index.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)

CHUNK_SIZE = 1024


class OurLLM(CustomLLM):
    model: Any = None
    tokenizer: Any = None
    device: Any = None
    model_name: str = None
    context_window: int = None
    num_output: int = None
    max_length: int = None
    temperature: float = None
    topP: float = None
    max_new_tokens: int = None

    def __init__(self, model_name, temperature, topP, max_length, device, context_window = 2048, num_output = 256):
        super().__init__()
        if ":" in model_name:
            model_name, revision = model_name.split(":")
        else:
            revision = "main"
            
        self.model_name = model_name
        self.device = device

        self.context_window = context_window
        self.num_output = num_output
        self.max_length = max_length
        self.temperature = temperature
        self.topP = topP
        # TODO: check if this is the right value 
        self.max_new_tokens = 508

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, 
            torch_dtype="auto", 
            trust_remote_code=True, 
            revision = revision,
            temperature = self.temperature,
            top_p = self.topP,
            use_cache = True
            )
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, 
            trust_remote_code=True)

        self.model.to(device)

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to(self.device)
        outputs = self.model.generate(**inputs, max_length=self.max_length, max_new_tokens=self.max_new_tokens)
        text = self.tokenizer.batch_decode(outputs)[0]

        return CompletionResponse(text=text)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs
    ) -> CompletionResponseGen:
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to(self.device)
        outputs = self.model.generate(**inputs, max_length=self.max_length, max_new_tokens=self.max_new_tokens)
        text = self.tokenizer.batch_decode(outputs)[0]

        yield CompletionResponse(text=text, delta=text)
 

def create_service_context(bot: _Bot):
    config = bot.modelConfig
    print(f"Model config: {bot.modelConfig}")
    with open('log', 'w') as f:
        f.write(f'model name: {bot.model_name.value}\n')
    
    llm = OurLLM(bot.model_name.value, config.temperature, config.topP, config.maxTokens, device)
    service_context = ServiceContext.from_defaults(
        chunk_size=CHUNK_SIZE,
        embed_model="local:BAAI/bge-base-en-v1.5",
        llm=llm, 
    )
    return service_context