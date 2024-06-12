from transformers import pipeline

import logging
import yaml

# Logging
conf = yaml.safe_load(open("config.yaml"))
logger = logging.getLogger(__name__)
logger.setLevel(conf["log_level"])

logger.info("Loading classification model...")
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
logger.info("Classification model loaded.\n")

# Classes
candidate_labels = ["recherche établissements", "recherche écoles", "précisions", "détails", "débouchés", "question ouverte"]

def classify(question : str):
    result = classifier(question, candidate_labels)
    logger.debug("Classification result: " + str(result))
    result = result['labels'][0]
    if result == "recherche établissements":
        return "search_schools"
    elif result == "précisions" or result == "détails" or result == "débouchés":
        return "school_info"
    else:
        return "other"

if __name__ == "__main__":
    question = input("Question: ")
    print(classify(question))