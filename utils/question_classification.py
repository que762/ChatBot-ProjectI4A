import logging
import os
import yaml

from transformers import pipeline

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# Set cache dir
config = yaml.safe_load(open("config.yaml"))
os.environ["TRANSFORMERS_CACHE"] = config["directories"]["models"]

logger.info("Loading classification model...")
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
logger.info("Classification model loaded.\n")

# Classes
candidate_labels = ["recherche établissements", "lister écoles", "précisions", "détails", "débouchés",
                    "question ouverte"]


def classify(question: str):
    """Classify a question into one of the following classes: \n
    - search_schools: The user is searching for schools. \n
    - school_info: The user is asking for information about a specific school. \n
    - other: The question is not related to schools. \n
    :param question: The question to classify.
    :return: The class of the question."""

    # Classify the question
    result = classifier(question, candidate_labels)
    logging.debug(result)
    result = result['labels'][0]

    # Return the corresponding class
    if result == "recherche établissements" or result == "lister écoles":
        return "search_schools"
    elif result == "précisions" or result == "détails" or result == "débouchés":
        return "school_info"
    else:
        return "other"


# Test
if __name__ == "__main__":
    while True:
        test_question = input("Question: ")
        print(classify(test_question))
