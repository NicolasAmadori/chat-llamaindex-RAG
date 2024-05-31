
# file_readers-module global variables
SPEECHES_FILE_NAME = "./data/dataset_interventi.json"
ACTS_FILE_NAME = "./data/dataset_atti.json"

EVAL_DATASETS_FOLDER = "./data/eval_queries-answers/"

# model_and_nodes_module global variables
HUGGINFACE_ACCESS_TOKEN = "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"


# LLM_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
# LLM_CACHE_DIR = './data/models/model-llama3-instruct/'

LLM_ID = "CamerAI/ItalianLegalExpert-CuriaParlaMentis-ORPO-final"
LLM_CACHE_DIR = './data/models/ItalianLegalExpert-CuriaParlaMentis-ORPO-final/'

# LLM_ID = "CamerAI/ItalianLegalExpert-Llama3-8B"
# LLM_CACHE_DIR = './data/models/ItalianLegalExpert-Llama3-8B/'


EMBED_MODEL_ID = "BAAI/bge-m3"
EMBED_MODEL_CACHE_DIR = "./data/models/embedding_model-bge-m3"

MAX_NEW_TOKENS = 32
MAX_INPUT_SIZE = 4096
MAX_CHUNK_OVERLAP = 0

# eval_module global variables
MULTIPLECHOICE_EVAL_OUTPUT_FILE = "./data/multiplechoice_eval_results.txt"
GENERATIVE_EVAL_OUTPUT_FILE = "./data/generative_eval_results.txt"
