import logging
import torch
from app.utils.interface import _Bot, _LLMConfig, _Message
from app.utils.config import get_wrapper_prompt, get_quantization_config
from llama_index import ServiceContext
import dotenv
from llama_index.llms import HuggingFaceLLM, MessageRole
from llama_index.prompts import PromptTemplate
import json
from fastapi import HTTPException
from time import time

dotenv.load_dotenv()

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
logger = logging.getLogger("uvicorn")

CHUNK_SIZE = 512
BOT_STORE_FILE = "./bot_store.json"



def messages_to_prompt_lama(messages):
	prompt = ""
	system_flag = False
	for message in messages:
		if message.role == 'system':
			prompt += f"<s>[INST] <<SYS>>\n{message.content}\n<</SYS>>\n\n"
			system_flag = True
		elif message.role == 'user':
			if not system_flag:
				system_flag = False
				prompt += f"<s>[INST] {message.content} [/INST]"
			else:
				prompt += f"{message.content} [/INST]"
		elif message.role == 'assistant':
			prompt += f" {message.content}</s>"
	return prompt



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

def messages_to_prompt_ita(messages):
	prompt = ""
	for message in messages:
		if message.role == 'system':
			prompt += f"[|Sistema| {message.content}\n"
		if message.role == 'user':
			prompt += f"[|Umano|] {message.content}\n"
		elif message.role == 'assistant':
			prompt += f"[|Assistente|] {message.content}\n"

	# # add final assistant prompt
	# if not prompt.startswith("<|Sistema|>\n"):
	# 	prompt = "<|Sistema|>\n</s>\n" + prompt

	# prompt = prompt + "[|Assistente|]"

	return prompt

#messages_to_prompt=messages_to_prompt_ita,

messages_template = [
	{
		"role": "user",
		"content": "Domanda",
	},
	{
		"role": "assistant",
		"content": "Risposta",
	},
	{
		"role": "user",
		"content": "Domanda",
	},
	{
		"role": "assistant",
		"content": "Risposta",
	}
]


def create_HFLLM(bot: _Bot):
	config: _LLMConfig = bot.modelConfig
	wrapper_prompt = get_wrapper_prompt(bot.model_name.value)
	quantization_config = get_quantization_config(bot.model_name.value)

	if bot.model_name.value == "galatolo/cerbero-7b":
		jinja_string = """ {% if message['role'] == 'user' %}[|Umano|] {{ message['content'] }} \n{% else %} [|Assistente|] {{ message['content'] }} \n{% endif %}"""
		t_kwargs = {"torch_dtype": "auto", "chat_template": jinja_string, "skip_special_tokens": True}
		m_kwargs = {"do_sample":True,"revision":"float16","torch_dtype": "auto", "quantization_config": quantization_config, "trust_remote_code": True}
		mtp = messages_to_prompt_ita
	else:
		t_kwargs = {"torch_dtype": "auto"}
		m_kwargs= {"trust_remote_code": True, "torch_dtype": "auto"}
		mtp = messages_to_prompt
	if bot.model_name.value == "meta-llama/Llama-2-7b-chat-hf":
		print("LLama2")
		mtp = messages_to_prompt_lama

	llm = HuggingFaceLLM(
			model_name=bot.model_name.value,
			tokenizer_name=bot.tokenizer_name,
			query_wrapper_prompt=PromptTemplate(wrapper_prompt),
			context_window=config.maxHistory,
			max_new_tokens=config.maxTokens,
			tokenizer_kwargs=t_kwargs,
			model_kwargs=m_kwargs,
			generate_kwargs={"temperature": config.temperature, "top_k": 50, "top_p": config.topP},
			messages_to_prompt=mtp,
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

def store_bot(bot_original: _Bot):
	# create a copy of bot to not override the original
	bot = _Bot(**bot_original.dict())
	with open(BOT_STORE_FILE, 'r') as f:
		bots = json.load(f)
		if bot.bot_id in bots:
			logger.error(f"Bot with id {bot.bot_id} already exists")
			raise HTTPException(status_code=400, detail=f"Bot with id {bot.bot_id} already exists")
		bot.model_name = bot.model_name.value
		bot.modelConfig.model_name = bot.modelConfig.model_name.value
		bots[bot.bot_id] = bot.dict()
		logger.info(f'Bot: {bot.dict()}')
		pass
	with open(BOT_STORE_FILE, 'w') as f:
		json.dump(bots, f)


def remove_bot_from_store(bot_id: str):
	with open(BOT_STORE_FILE, 'r') as f:
		bots = json.load(f)
		if bot_id not in bots:
			logger.error(f"Bot with id {bot_id} does not exist")
			raise HTTPException(status_code=400, detail=f"Bot with id {bot_id} does not exist")
		del bots[bot_id]
	with open(BOT_STORE_FILE, 'w') as f:
		json.dump(bots, f)

def add_message_to_store(bot_id: str, message: _Message):
	with open(BOT_STORE_FILE, 'r') as f:
		bots = json.load(f)
		if bot_id not in bots:
			logger.error(f"Bot with id {bot_id} does not exist")
			raise HTTPException(status_code=400, detail=f"Bot with id {bot_id} does not exist")
		bots[bot_id]['context'].append({
			'role': message.role,
			'content': message.content,
			'date': message.date
		})
	with open(BOT_STORE_FILE, 'w') as f:
		json.dump(bots, f)

def add_response_to_store(bot_id: str, response: str):
	with open(BOT_STORE_FILE, 'r') as f:
		bots = json.load(f)
		if bot_id not in bots:
			logger.error(f"Bot with id {bot_id} does not exist")
			raise HTTPException(status_code=400, detail=f"Bot with id {bot_id} does not exist")
		bots[bot_id]['context'].append({
			'role': 'assistant',
			'content': str(response),
			'date': round(time()*1000)
		})
	with open(BOT_STORE_FILE, 'w') as f:
		json.dump(bots, f)

def get_role(role: str):
	if role == 'user':
		return MessageRole.USER
	elif role == 'assistant':
		return MessageRole.ASSISTANT
	elif role == 'system':
		return MessageRole.SYSTEM
	elif role == 'function':
		return MessageRole.FUNCTION
	elif role == 'tool':
		return MessageRole.TOOL
	else:
		raise HTTPException(status_code=400, detail=f"Invalid role {role}")