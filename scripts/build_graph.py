import json
import pickle
import networkx as nx
import numpy as np
import faiss

with open("data/embeddings.pkl", "rb") as f:
    data = pickle.load(f)

chunks = data["chunks"]
embeddings = np.array(data["embeddings"]).astype("float32")

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

G = nx.Graph()

for i, chunk in enumerate(chunks):
    doc_id = chunk["doc_id"]

    G.add_node(
        doc_id,
        title=chunk["title"],
        text=chunk["text"],
        url=chunk["url"]
    )

scores, indices = index.search(embeddings, 4)

for i in range(len(chunks)):
    source = chunks[i]["doc_id"]

    for j in range(1, 4):
        target = chunks[indices[i][j]]["doc_id"]

        if source != target:
            G.add_edge(source, target, weight=float(scores[i][j]))

with open("data/graph.json", "w", encoding="utf-8") as f:
    json.dump(nx.node_link_data(G), f)

print("Graph created successfully.")
print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())