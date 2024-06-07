import torch

import chatbot
import chatbot_gemma

print("CUDA version used is : " + torch.version.cuda)
print("Total GPU memory is : " + str(torch.cuda.get_device_properties(0).total_memory / 1024**3) + " GB")
print("Total GPU memory used is : " + str(torch.cuda.memory_allocated(0) / 1024**3) + " GB")
print("Total GPU memory cached is : " + str(torch.cuda.memory_reserved(0) / 1024**3) + " GB")
print("Total GPU memory free is : " + str((torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024**3) + " GB")

if __name__ == "__main__":
    llm, tokenizer = chatbot.load_model()
    input_text = input("> ")
    response = chatbot.find_best_schools(input_text, llm, tokenizer)
    print("Response:")
    print(response)