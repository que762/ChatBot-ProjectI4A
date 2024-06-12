from typing import Dict, List, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
import os
import gc
import yaml
import logging

# Define the model
model_name_or_path = "bofenghuang/vigogne-2-7b-chat"
revision = "v2.0"

# Load the config
config = yaml.safe_load(open("config.yaml"))
cache_dir = config["directories"]["models"]
prompt_path = config["directories"]["prompt"]
os.makedirs(cache_dir, exist_ok=True)

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(config["log_level"])

# Clear the cache
torch.cuda.empty_cache()
gc.collect()

logger.info("Loading chatbot model...")
bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, revision=revision, padding_side="right", cache_dir=cache_dir)
model = AutoModelForCausalLM.from_pretrained(model_name_or_path, revision=revision, torch_dtype=torch.float16, device_map="auto", cache_dir=cache_dir, quantization_config=bnb_config)
logger.info("Chatbot model loaded\n")

def chat(
    query: str,
    context: Optional[str] = None,
    history: Optional[List[Dict]] = None,
    temperature: float = 0.3,
    top_p: float = 1.0,
    top_k: float = 0,
    repetition_penalty: float = 1.1,
    max_new_tokens: int = 1024,
    **kwargs,
):
    if history is None:
        history = []

    history.append({"role": "user", "content": query})

    input_text = get_chat_template(query, context, history[:-1])
    print(input_text)
    #print(history)

    logger.debug("Prompt: " + input_text)

    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(model.device)
    input_length = input_ids.shape[1]

    generated_outputs = model.generate(
        input_ids=input_ids,
        generation_config=GenerationConfig(
            temperature=temperature,
            do_sample=temperature > 0.0,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
            **kwargs,
        ),
        return_dict_in_generate=True,
    )

    generated_tokens = generated_outputs.sequences[0, input_length:]
    generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    history.append({"role": "assistant", "content": generated_text})

    return generated_text, history

def get_chat_template(user_prompt, context, history):    
    with open(prompt_path, 'r') as f:
        default_system_prompt = f.read()
    return (f"{default_system_prompt}\n\n"
            f"user : \n"
            f"- History : \n {handle_chat_history(history)}\n"
            f"- Contexte : {context}\n"
            f"- Question : {user_prompt}\n"
            f"assistant : \n"
            )

def handle_chat_history(history):
    return "\n".join([f"{x['role']} : {x['content']}" for x in history])

if __name__ == "__main__":
    history = []
    while True:
        query = input("Query: ")
        result, history = chat(query, history=history)
        print("Result:")
        print(result)