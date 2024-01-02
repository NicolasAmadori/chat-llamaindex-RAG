from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread
from typing import Any
import logging
import torch
import gc
from llama_index.llms.base import llm_completion_callback
from app.utils.interface import _Bot, _availableModels, _LLMConfig
from llama_index import ServiceContext
from llama_index.callbacks.base import CallbackManager, BaseCallbackHandler

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
logger = logging.getLogger("uvicorn")

from llama_index.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)

CHUNK_SIZE = 512


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
        self.max_new_tokens = 500

        do_sample = self.temperature != 0.0 or self.topP != 1.0

        model_params = {
            "torch_dtype": "auto",
            "trust_remote_code": True,
            "revision": revision,
            "temperature": self.temperature,
            "top_p": self.topP,
            "do_sample": do_sample,
        }
        try:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **model_params, use_cache = True)
        except TypeError:
            # Model like phi 2 and 1.5 crash if we set use_cache
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **model_params)    

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
        # with open('log', 'w') as f:
        #     f.write('[complete] prompt: '+prompt+'\n')
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to(self.device)
        outputs = self.model.generate(**inputs, max_length=self.max_length, max_new_tokens=self.max_new_tokens)
        text = self.tokenizer.batch_decode(outputs)[0]

        return CompletionResponse(text=text)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs
    ) -> CompletionResponseGen: 
        with open('log_stream', 'w') as f:
            f.write('[stream_complete] prompt: '+prompt+'\n')
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=True).to(self.device)
        outputs = self.model.generate(**inputs, max_length=self.max_length, max_new_tokens=self.max_new_tokens)
        text = self.tokenizer.batch_decode(outputs)[0]

        with open('log_stream', 'w') as f:
            f.write('[stream-finished] text: '+text+'\n')    

        yield CompletionResponse(text=text, delta=text)   
        """
        Code for streaming the ouput of the model, i leave it commented because 
        it works really, really slowly and i don't know why.
        It is based on https://huggingface.co/docs/transformers/v4.36.1/en/internal/generation_utils#transformers.TextStreamer

        with torch.no_grad():
            inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to(self.device)
            streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True)

            generation_kwargs = dict(inputs, max_length=self.max_length, max_new_tokens=self.max_new_tokens, streamer=streamer)
            generation_thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
            generation_thread.start()

            accumulated_text = ""
            for text in streamer:
                accumulated_text += text
                print(f"Streamed text: {text}")
                yield CompletionResponse(text=accumulated_text, delta=text)

        """
 
class CallbackHandler(BaseCallbackHandler):
    """Base callback handler that can be used to track event starts and ends."""

    def on_event_start(
        self,
        event_type,
        payload= None,
        event_id: str = "",
        **kwargs: Any,
    ) -> str:
        """Run when an event starts and return id of event."""
        with open('log_event', 'w') as f:
            f.write(f"event: {event_id}, EVENT TYPE: {event_type}, PAYLOAD: {payload} \n\n\n\n")

        print("start", event_type)

    def on_event_end(
        self,
        event_type,
        payload= None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """Run when an event ends."""
        with open('log_event', 'w') as f:
            f.write(f"event: {event_id}, EVENT TYPE: {event_type}, PAYLOAD: {payload}  \n\n\n\n")
        print("end", event_type)

    def start_trace(self, trace_id = None) -> None:
        """Run when an overall trace is launched."""
        with open('log_trace', 'w') as f:
            f.write(f"trace: {trace_id}  \n")

    def end_trace(
        self,
        trace_id=None,
        trace_map= None,
    ) -> None:
        """Run when an overall trace is exited."""
        import json

        with open('log_trace_end', 'w') as f:
            f.write(f"trace: {json.dumps(trace_map, indent=4)}  \n")

        print('trace: ', json.dumps(trace_map, indent=4))


def create_service_context(bot: _Bot):
    config = bot.modelConfig
    # delete llm variable if it exists to free memory
    gc.collect()
    torch.cuda.empty_cache()
    torch.distributed.destroy_process_group()

    llm = OurLLM(bot.model_name.value, config.temperature, config.topP, config.maxTokens, device)
    service_context = ServiceContext.from_defaults(
        chunk_size=CHUNK_SIZE,
        embed_model="local:BAAI/bge-base-en-v1.5",
        llm=llm, 
        callback_manager=CallbackManager([CallbackHandler([], [])]),
    )
    
    return service_context