import logging
import torch
from app.utils.interface import _Bot, _availableModels, _LLMConfig
from app.utils.prompt import get_wrapper_prompt
from llama_index import ServiceContext
import dotenv
from llama_index.llms import HuggingFaceLLM
from llama_index.prompts import PromptTemplate

dotenv.load_dotenv()

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
logger = logging.getLogger("uvicorn")

CHUNK_SIZE = 512

def messages_to_prompt(messages):
  prompt = ""
  for message in messages:
    if message.role == 'system':
      prompt += f"<|system|>\n{message.content}</s>\n"
    elif message.role == 'user':
      prompt += f"<|user|>\n{message.content}</s>\n"
    elif message.role == 'assistant':
      prompt += f"<|assistant|>\n{message.content}</s>\n"

  # ensure we start with a system prompt, insert blank if needed
  if not prompt.startswith("<|system|>\n"):
    prompt = "<|system|>\n</s>\n" + prompt

  # add final assistant prompt
  prompt = prompt + "<|assistant|>\n"

  return prompt

def create_HFLLM(bot: _Bot):
  config: _LLMConfig = bot.modelConfig
  wrapper_prompt = get_wrapper_prompt(bot.model_name.value)
  llm = HuggingFaceLLM(
      model_name=bot.model_name.value,
      tokenizer_name=bot.tokenizer_name,
      query_wrapper_prompt=PromptTemplate(wrapper_prompt),
      context_window=config.maxHistory,
      max_new_tokens=config.maxTokens,
      tokenizer_kwargs={"torch_dtype": "auto"},
      model_kwargs={"torch_dtype": "auto", "trust_remote_code": True},
      generate_kwargs={"temperature": config.temperature, "top_k": 50, "top_p": config.topP},
      messages_to_prompt=messages_to_prompt,
      device_map=device,
  )
  return llm


def create_service_context(bot: _Bot):
    llm = create_HFLLM(bot)
    service_context = ServiceContext.from_defaults(
        chunk_size=CHUNK_SIZE,
        embed_model="local:BAAI/bge-base-en-v1.5",
        llm=llm
    )

    return service_context