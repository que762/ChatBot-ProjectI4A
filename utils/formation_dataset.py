import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

formations_dataset = pd.read_csv('datasets/formations_description.csv')
formations_dataset.drop_duplicates(subset=['description'], inplace=True)
print("Loading dataset model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("Dataset model loaded")
print("Loading embeddings...")
embeddings = pd.read_csv('datasets/formations_embeddings.csv').values
print("Embeddings loaded")

def compare_to_each_row(sentence):
    """Compare a sentence to each sentence in the dataset and return the similarities."""
    sentence_embedding = model.encode(sentence)
    similarities = cosine_similarity([sentence_embedding], embeddings)
    return similarities


def sort_by_most_similar(similarities):
    """Sort the dataset by the most similar formations."""
    # add the similarity column
    formations_dataset['similarity'] = similarities[0]
    if max(similarities[0]) < 0.3: # if not similar enough
        return None
    return formations_dataset.sort_values(by='similarity', ascending=False)