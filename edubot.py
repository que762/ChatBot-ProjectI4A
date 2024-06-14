from typing import Dict, List, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
import os
import gc
import logging
import yaml

from utils.mongo import retrieve_convo, clear_convo, insert_message

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
logging.basicConfig(level=config["log_level"])

# Clear the cache
torch.cuda.empty_cache()
gc.collect()

# Load the model
logger.info("Loading chatbot model...")
bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, revision=revision, padding_side="right",
                                          cache_dir=cache_dir)
model = AutoModelForCausalLM.from_pretrained(model_name_or_path, revision=revision, torch_dtype=torch.float16,
                                             device_map="auto", cache_dir=cache_dir, quantization_config=bnb_config)
logger.info("Chatbot model loaded\n")


def chat(
        query: str,
        context: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        temperature: float = 0.5,
        top_p: float = 1.0,
        top_k: float = 0,
        repetition_penalty: float = 1.1,
        max_new_tokens: int = 1024,
        **kwargs,
):
    """
    Main chat function.
    :param query: The user query.
    :param context: The context of the conversation.
    :param history: The conversation history.
    :param temperature: The temperature for sampling.
    :param top_p: The nucleus sampling parameter. Select tokens with cumulative probability of at most p.
    :param top_k: The top-k sampling parameter. Select the top-k tokens.
    :param repetition_penalty: The repetition penalty.
    :param max_new_tokens: The maximum number of tokens to generate.
    :param kwargs: Additional generation parameters.

    :return: The generated text and the updated conversation history.
    """

    # Prepare history and input text
    if history is None:
        history = []

    history.append({"role": "user", "content": query})

    input_text = get_chat_template(query, context, history[:-1])

    logger.debug(f"Input text: {input_text}")

    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(model.device)
    input_length = input_ids.shape[1]

    # Generate the response
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


def chat_db(user_id, user_prompt, context=None):
    """Function to chat with the model and store the conversation history in the database.
    :param user_id: The user ID.
    :param user_prompt: The user prompt.
    :param context: The context of the conversation."""

    try:
        # Retrieve conversation history
        history = retrieve_convo(user_id)

        # Chat with the model
        result, history = chat(user_prompt, context, history)

        # Hardcoded fix for the model sometimes adding "- Context : None" to the result
        if result.find("- Context : None") != -1:
            result = result.replace("- Context : None", "")

        return result, history
    except Exception as e:
        logger.error(f"Error during chat_db operation: {e}")


def get_chat_template(user_prompt, context, history):
    """Function to generate the chat template for the model input.
    This function exists since the default history doesn't seem to work with the model we are using.
    :param user_prompt: The user prompt.
    :param context: The context of the conversation.
    :param history: The conversation history.
    """

    with open(prompt_path, 'r') as f:
        default_system_prompt = f.read()
    return (f"{default_system_prompt}\n\n"
            f"system : \n"
            f"- History : \n {handle_chat_history(history)}\n"
            f"\n- Context : {context}\n"
            f"\nuser : \n"
            f"- Question : {user_prompt}\n"
            f"\nassistant : \n"
            )


def handle_chat_history(history):
    """Generate the chat history string for the model input.
    :param history: The conversation history.
    :return: The formatted chat history string."""

    return "\n".join([f"{x['role']} : {x['content']}" for x in history])


# Test the chat function
if __name__ == "__main__":
    clear_convo("123")
    while True:
        user_query = input("Query: ")
        chat_result, _ = chat_db("123", user_query)
        print("Result:")
        print(chat_result)
        insert_message(user_query, "123", False)
        insert_message(chat_result, "123", True)
