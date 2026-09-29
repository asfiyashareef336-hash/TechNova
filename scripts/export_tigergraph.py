import json
import csv

with open("data/graph.json", "r", encoding="utf-8") as f:
    data = json.load(f)

nodes = data["nodes"]
edges = data["edges"]

with open("data/documents.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "doc_id",
        "title",
        "text",
        "url"
    ])

    for node in nodes:
        writer.writerow([
            node.get("id", ""),
            node.get("title", ""),
            node.get("text", ""),
            node.get("url", "")
        ])

with open("data/related_to.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "from",
        "to"
    ])

    for edge in edges:
        writer.writerow([
            edge.get("source", ""),
            edge.get("target", "")
        ])

print("Created data/documents.csv")
print("Created data/related_to.csv")
print("Documents:", len(nodes))
print("Relationships:", len(edges))