import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

with open("data/embeddings.pkl", "rb") as f:
    data = pickle.load(f)

chunks = data["chunks"]
embeddings = np.array(data["embeddings"])

model = SentenceTransformer("all-MiniLM-L6-v2")


def search(query, top_k=5):
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )[0]

    scores = embeddings @ query_embedding
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in top_indices:
        results.append({
            "score": float(scores[index]),
            "doc_id": chunks[index]["doc_id"],
            "title": chunks[index]["title"],
            "text": chunks[index]["text"]
        })

    return results


if __name__ == "__main__":
    query = input("Enter your question: ")

    results = search(query)

    for result in results:
        print("\nScore:", result["score"])
        print("Title:", result["title"])
        print("Doc ID:", result["doc_id"])
        print("Text:", result["text"][:500])