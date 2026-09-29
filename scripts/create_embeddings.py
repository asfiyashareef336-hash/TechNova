import json
import pickle
from sentence_transformers import SentenceTransformer

input_file = "data/chunks.jsonl"
output_file = "data/embeddings.pkl"

model = SentenceTransformer("all-MiniLM-L6-v2")

chunks = []

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        chunks.append(json.loads(line))

texts = [chunk["text"] for chunk in chunks]

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    normalize_embeddings=True
)

data = {
    "chunks": chunks,
    "embeddings": embeddings
}

with open(output_file, "wb") as f:
    pickle.dump(data, f)

print("Embeddings created successfully.")