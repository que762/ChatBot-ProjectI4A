import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import gc
import torch
from transformers import BitsAndBytesConfig
import yaml

import utils.formation_dataset as fd

print("CUDA version used is : " + torch.version.cuda)
print("Total GPU memory is : " + str(torch.cuda.get_device_properties(0).total_memory / 1024**3) + " GB")
print("Total GPU memory used is : " + str(torch.cuda.memory_allocated(0) / 1024**3) + " GB")
print("Total GPU memory cached is : " + str(torch.cuda.memory_reserved(0) / 1024**3) + " GB")
print("Total GPU memory free is : " + str((torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024**3) + " GB")

config = yaml.safe_load(open("config.yaml"))

def load_model():
    # Conf
    access_token = config["access_token"]
    model_id = "mistralai/Mistral-7B-Instruct-v0.3"
    cache_dir = ("./models")
    os.makedirs(cache_dir, exist_ok=True)

    # Clear memory
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