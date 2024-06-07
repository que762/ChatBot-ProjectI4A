# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import gc
import torch
from transformers import BitsAndBytesConfig

access_token = "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"

def load_model():
    model_id = "google/gemma-2b-it"

    cache_dir = ("./models")
    os.makedirs(cache_dir, exist_ok=True)

    torch.cuda.empty_cache()
    gc.collect()

    # Configuration for 4-bit quantization
    bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)

    # Load the model with 4-bit quantization
    model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        cache_dir=cache_dir, 
        token=access_token, 
        device_map="auto", 
        torch_dtype=torch.float16,
        quantization_config=bnb_config
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_id, 
        cache_dir=cache_dir, 
        token=access_token
    )
    
    return model, tokenizer