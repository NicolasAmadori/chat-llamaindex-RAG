import logging
import torch
from app.utils.interface import _Bot, _LLMConfig, _Message, _availableModels
from app.utils.config import get_wrapper_prompt, get_quantization_config
from llama_index import ServiceContext, PromptHelper
import dotenv
from llama_index.llms import HuggingFaceLLM, MessageRole
from llama_index.prompts import PromptTemplate
import json
from fastapi import HTTPException
from time import time
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from llama_index.llms import LlamaCPP
from model_and_nodes_module import (
    get_acts_nodes,
    get_speeches_nodes, 
    get_embed_model,
    get_llm_model,
)

from project_config import (
    MAX_INPUT_SIZE, 
    MAX_NEW_TOKENS, 
    MAX_CHUNK_OVERLAP,
)

dotenv.load_dotenv()

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
logger = logging.getLogger("uvicorn")

CHUNK_SIZE = 1024
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
				prompt += f"<s>[INST] {message.content} [/INST]"
			else:
				system_flag = False
				prompt += f"{message.content} [/INST]"
		elif message.role == 'assistant':
			prompt += f" {message.content}</s>\n"

	print(prompt)
	return prompt

def messages_to_prompt_vicuna(messages):
	prompt = ""
	for message in messages:
		if message.role == 'system':
			prompt += f"{message.content} "
		elif message.role == 'user':
			prompt += f"USER: {message.content} "
		elif message.role == 'assistant':
			prompt += f"ASSISTANT: {message.content} "
		
	print(prompt)
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

	#print(prompt.split("--------------------")[1])
	if len(prompt.split("--------------------")) > 1:
		context = prompt.split("--------------------")[1]

		# substitute all the \n with spaces
		context = context.replace("\n", " ")
		
		# split on "page_label:"
		context_splits = context.split("page_label:")[1:]

		# write context splits on a log file. each on a different line
		with open("context.txt", "w") as f:
			for context_split in context_splits:
				f.write("page_label:" + context_split + "\n\n")

	return prompt

def messages_to_prompt_ita(messages):
	prompt = ""
	for message in messages:
		if message.role == 'system':
			prompt += f"[|Sistema|] {message.content}\n"
		if message.role == 'user':
			prompt += f"[|Umano|] {message.content}\n"
		elif message.role == 'assistant':
			prompt += f"[|Assistente|] {message.content}\n"

	# # add final assistant prompt
	# if not prompt.startswith("<|Sistema|>\n"):
	# 	prompt = "<|Sistema|>\n</s>\n" + prompt

	# prompt = prompt + "[|Assistente|]"
	
	print(prompt)
	return prompt

# messages_to_prompt=messages_to_prompt_ita,

def create_HFLLM(bot: _Bot):
	llm, _ = get_llm_model()
	return llm


def create_service_context(bot: _Bot):
    llm = create_HFLLM(bot)
    embeddings = get_embed_model()
	prompt_helper = PromptHelper(MAX_INPUT_SIZE, MAX_NEW_TOKENS, MAX_CHUNK_OVERLAP)
	service_context = ServiceContext.from_defaults(
		llm=llm,
		embed_model=embeddings,
		prompt_helper=prompt_helper,
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