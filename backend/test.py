from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread
from typing import Any
import logging
import torch
# SIUM

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model_card = 'HuggingFaceH4/zephyr-7b-beta'

model_params = {
        "torch_dtype": "auto",
        "trust_remote_code": True,
        "temperature": 0.5,
        "top_p": 1,
        "do_sample": True,
}


model = AutoModelForCausalLM.from_pretrained(model_card, **model_params)
tokenizer = AutoTokenizer.from_pretrained(model_card, trust_remote_code=True)

model.to(device)


prompt = """
<|system|>
You are a friendly chatbot who always responds kindly.
You can use othe information provided below, as weel as your own knowledge, to answer questions.
Use only the information below, if you have any prior information about the user query don't use them but you only the information of the context:
Do not mention the provided context but just use it.

CONTEXT: 
The capital of France is Paris 
The capital of Italy is Rome 
The capital of Spain is Madrid 
The capital of UK is London 
The capital of Adhenfd is Ovand 
</s>
<|user|>
What is the capital of Adhenfd?</s>
<|assistant|>
"""

def foo(): 
    with torch.no_grad():
        inputs = tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to(device)
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True)
        generation_kwargs = dict(inputs, max_new_tokens=200, streamer=streamer)
        generation_thread = Thread(target=model.generate, kwargs=generation_kwargs)
        generation_thread.start()
        accumulated_text = ""
        for text in streamer:
            accumulated_text += text

            yield text

if __name__ == "__main__":
    for text in foo():
        print(f"{text} ", end="" )