from transformers import BitsAndBytesConfig
import torch

config_dict = {
    "galatolo/cerbero-7b": 
        {
            "prompt": "Rispondi alle domande dell'umano solo in italiano e senza identificare chi sta parlando. [|Umano|] \n {query_str} </s>\n [|Assistente|] \n <s> ",
            "quantization": BitsAndBytesConfig(
                load_in_8bit=True
            )
        },
    "mistralai/Mistral-7B-Instruct-v0.1": 
        {
            "prompt": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
            "quantization": BitsAndBytesConfig(
                load_in_8bit=False,
            )        
        },
    "HuggingFaceH4/zephyr-7b-beta": 
        {
            "prompt": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
            "quantization": BitsAndBytesConfig(
                load_in_8bit=False,
            )            
        },
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0":
        {
            "prompt": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
            "quantization": BitsAndBytesConfig(
                load_in_8bit=False,
            )            
        },
    "cognitivecomputations/dolphin-2.6-mistral-7b-dpo":
        {
            "prompt": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
            "quantization": BitsAndBytesConfig(
                load_in_8bit=False,
            )            
        },
    "meta-llama/Llama-2-7b-chat-hf":
        {
            "prompt": "<s> [INST] {query_str} [/INST]",
            "quantization": BitsAndBytesConfig(
                load_in_8bit=False,
            )            
        }
}

def get_wrapper_prompt(model_name):
    return config_dict[model_name]["prompt"]

def get_quantization_config(model_name):
    return config_dict[model_name]["quantization"]