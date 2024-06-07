import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

formations_dataset = pd.read_csv('formations_description.csv')
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def compare_to_each_sentence(sentence, embeddings):
    sentence_embedding = model.encode(sentence)
    similarities = cosine_similarity([sentence_embedding], embeddings)
    return similarities

def sort_by_most_similar(similarities, formations_dataset):
    formations_dataset['similarity'] = similarities[0]
    return formations_dataset.sort_values(by='similarity', ascending=False)