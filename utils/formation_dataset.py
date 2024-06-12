import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load the dataset
formations_dataset = pd.read_csv('datasets/formations_description.csv')
formations_dataset.drop_duplicates(subset=['description'], inplace=True)
formations_dataset.reset_index(drop=True, inplace=True)

# Load the model
logger.info("Loading dataset model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
logger.info("Dataset model loaded\n")

# Load the embeddings
logger.info("Loading embeddings...")
embeddings = pd.read_csv('datasets/formations_embeddings.csv').values
logger.info("Embeddings loaded\n")


def find_index_by_description(description, formations_dataset=formations_dataset):
    """Find the index of a formation in the dataset by its description."""
    return formations_dataset[formations_dataset['description'] == description].index[0]

def get_row_embedding(index):
    """Get the embedding of a row in the dataset."""
    return embeddings[index]

def compare_to_each_row(sentence, embeddings=embeddings):
    """Compare a sentence to each sentence in the dataset and return the similarities."""
    sentence_embedding = model.encode(sentence)
    similarities = cosine_similarity([sentence_embedding], embeddings)
    return similarities

def sort_by_most_similar(similarities, formations_dataset=formations_dataset):
    """Sort the dataset by the most similar formations."""
    # add the similarity column
    formations_dataset['similarity'] = similarities[0]
    if max(similarities[0]) < 0.3: # if not similar enough
        return None
    return formations_dataset.sort_values(by='similarity', ascending=False)

if __name__ == "__main__":
    similarities = compare_to_each_row("CPGE Doubs")
    sorted_formations = sort_by_most_similar(similarities)
    # five most similar formation descriptions
    for i in range(5):
        print(sorted_formations.iloc[i]['description'])