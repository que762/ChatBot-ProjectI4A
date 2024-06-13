from transformers import pipeline

import logging
import yaml

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.info("Loading classification model...")
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
logger.info("Classification model loaded.\n")

# Classes
candidate_labels = ["recherche établissements", "lister écoles", "précisions", "détails", "débouchés",
                    "question ouverte"]


def classify(question: str):
    result = classifier(question, candidate_labels)
    print("Classification result: " + str(result))
    result = result['labels'][0]
    if result == "recherche établissements" or result == "lister écoles":
        return "search_schools"
    elif result == "précisions" or result == "détails" or result == "débouchés":
        return "school_info"
    else:
        return "other"


if __name__ == "__main__":
    while True:
        question = input("Question: ")
        print(classify(question))
