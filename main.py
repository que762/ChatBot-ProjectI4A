import torch
import logging
import yaml

import chatbot
import vigogne
import utils.question_classification as classif
import utils.formation_dataset as formation_dataset
import server_handle

# Logging
config = yaml.safe_load(open("config.yaml"))
logger = logging.getLogger(__name__)
logger.setLevel(config["log_level"])

# Startup
logger.info("CUDA version used is : " + torch.version.cuda)
logger.info("Total GPU memory is : " + str(torch.cuda.get_device_properties(0).total_memory / 1024**3) + " GB")
logger.info("Total GPU memory used is : " + str(torch.cuda.memory_allocated(0) / 1024**3) + " GB")
logger.info("Total GPU memory cached is : " + str(torch.cuda.memory_reserved(0) / 1024**3) + " GB")
logger.info("Total GPU memory free is : " + str((torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024**3) + " GB\n")

if __name__ == "__main__":
    server_handle.start_server()