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
        },
    "TheBloke/Llama-2-13B-chat-GPTQ:main":
        {
            "prompt": "[INST] {query_str} [/INST]",
            "quantization": BitsAndBytesConfig(
                load_in_4bit=False,
            )        
        },
    "TheBloke/Llama-2-13B-chat-GGUF llama-2-13b-chat.Q4_K_M.gguf":
        {
            "prompt": "[INST] {query_str} [/INST]",
            "quantization": BitsAndBytesConfig(
                load_in_4bit=False,
            )        
        },
    "TheBloke/Wizard-Vicuna-30B-Uncensored-GPTQ:gptq-4bit-32g-actorder_True":
        {
            "prompt": "USER: {query_str} ASSISTANT:",
            "quantization": BitsAndBytesConfig(
                load_in_4bit=False,
            )        
        },
    "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGML/resolve/main/llama-2-13b-chat.ggmlv3.q4_0.bin":
        {
            "prompt": "[INST] {query_str} [/INST]",
            "quantization": BitsAndBytesConfig(
                load_in_4bit=False,
            )        
        },
    "TheBloke/Llama-2-13B-chat-GGML":
        {
            "prompt": "[INST] {query_str} [/INST]",
            "quantization": BitsAndBytesConfig(
                load_in_4bit=False,
            )        
        },
    "default":
        {
            "prompt": "[INST] {query_str} [/INST]",
            "quantization": BitsAndBytesConfig(
                load_in_4bit=False,
            )               
        }
}

def get_wrapper_prompt(model_name):
    try:
        return config_dict[model_name]["prompt"]
    except:
        return config_dict["default"]["prompt"]
def get_quantization_config(model_name):
    try:
        return config_dict[model_name]["quantization"]
    except:
        return config_dict["default"]["quantization"]