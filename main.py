import torch
import logging

import pipeline
import utils.mongo as mongo

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Startup
logger.info("CUDA version used is : " + torch.version.cuda)
logger.info("Total GPU memory is : " + str(torch.cuda.get_device_properties(0).total_memory / 1024**3) + " GB")
logger.info("Total GPU memory used is : " + str(torch.cuda.memory_allocated(0) / 1024**3) + " GB")
logger.info("Total GPU memory cached is : " + str(torch.cuda.memory_reserved(0) / 1024**3) + " GB")
logger.info("Total GPU memory free is : " + str((torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024**3) + " GB\n")

if __name__ == "__main__":
    mongo.clear_convo("1234")
    while True:
        user_input = input("User: ")
        response = pipeline.educhat("1234", user_input)
        print("Bot: " + response)