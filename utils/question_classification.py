from transformers import pipeline
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.info("Loading classification model...")
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
logging.info("Classification model loaded.\n")

# Classes
candidate_labels = ["recherche établissements", "informations établissement", "question ouverte"]

def classify(question : str):
    result = classifier(question, candidate_labels)["labels"][0]
    if result == "recherche établissements":
        return "search_schools"
    elif result == "informations établissement":
        return "school_info"
    else:
        return "other"

if __name__ == "__main__":
    question = input("Question: ")
    print(classify(question))