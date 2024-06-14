# wsgi.py
from server_handle import server, socketio
import torch
import logging
import yaml

# Logging
config = yaml.safe_load(open("config.yaml"))
logger = logging.getLogger("wsgi")
logger.setLevel(config["log_level"])
logging.basicConfig(level=config["log_level"])


if __name__ == "__main__":
    logger.info("CUDA version used is : " + torch.version.cuda)
    logger.info("Total GPU memory is : " + str(torch.cuda.get_device_properties(0).total_memory / 1024 ** 3) + " GB")
    logger.info("Total GPU memory used is : " + str(torch.cuda.memory_allocated(0) / 1024 ** 3) + " GB")
    logger.info("Total GPU memory cached is : " + str(torch.cuda.memory_reserved(0) / 1024 ** 3) + " GB")
    logger.info("Total GPU memory free is : " + str(
        (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024 ** 3) + " GB\n")

    socketio.run(server)
