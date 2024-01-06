prompts_dict = {
    "microsoft/phi-1_5": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
    "microsoft/phi-2": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
    "mistralai/Mistral-7B-Instruct-v0.1": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
    "meta-llama/Llama-2-7b": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
    "TheBloke/Llama-2-7b-Chat-GPTQ:gptq-4bit-64g-actorder_True": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
    "google/flan-t5-xxl": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
    "deepset/tinyroberta-squad2": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n",
    "HuggingFaceH4/zephyr-7b-beta": "<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n"
}

def get_wrapper_prompt(model_name):
    return prompts_dict[model_name]