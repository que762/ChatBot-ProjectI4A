import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import gc
import torch
from transformers import BitsAndBytesConfig
import yaml

import utils.formation_dataset as formation_dataset

config = yaml.safe_load(open("config.yaml"))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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

def gen_response(input_text, model, tokenizer):
    input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)

    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_length= 256 + len(input_text),
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            no_repeat_ngram_size=2,  # Prevent repetition of 2-grams
            temperature=0.2,         # Control the creativity of the model
            top_k=50,                # Top-k sampling
            top_p=0.9               # Nucleus sampling
        )

    return tokenizer.decode(output[0], skip_special_tokens=True)

def find_best_schools(sentence, model, tokenizer):
    similarities = formation_dataset.compare_to_each_row(sentence)
    sorted_formations = formation_dataset.sort_by_most_similar(similarities)

    if sorted_formations is None:
        print("Aucune formation correspondant à votre demande.")

    else:
        formations = sorted_formations.head(5)
        input_text = "[UTILISATEUR] Donne moi la liste des formations suivantes : \n"
        index_flemme = 1
        for index, formation in formations.iterrows():
            input_text += f" - {index_flemme} : {formation['description']}\n"
            index_flemme += 1

    input_text += "\n[ASSISTANT] : "


    return gen_response(input_text, model, tokenizer)