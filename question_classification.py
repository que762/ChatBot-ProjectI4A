from transformers import pipeline

print("Loading classification model...")
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
print("Classification model loaded.")

# Classes
candidate_labels = ["recherche établissements", "informations établissement", "question ouverte"]

def classify(question : str):
    result = classifier(question, candidate_labels)
    return result["labels"][0]

if __name__ == "__main__":
    question = input("Question: ")
    print(classify(question))