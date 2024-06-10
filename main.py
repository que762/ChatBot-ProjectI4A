import torch
import chatbot

print("CUDA version used is : " + torch.version.cuda)
print("Total GPU memory is : " + str(torch.cuda.get_device_properties(0).total_memory / 1024**3) + " GB")
print("Total GPU memory used is : " + str(torch.cuda.memory_allocated(0) / 1024**3) + " GB")
print("Total GPU memory cached is : " + str(torch.cuda.memory_reserved(0) / 1024**3) + " GB")
print("Total GPU memory free is : " + str((torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024**3) + " GB")

if __name__ == "__main__":
    input_text = input("> ")
    response, _ = chatbot.find_best_schools(input_text)
    print("Response:")
    print(response)