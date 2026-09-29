import json

input_file = "data/corpus.jsonl"
output_file = "data/chunks.jsonl"

chunk_size = 500

with open(input_file, "r", encoding="utf-8") as f:
    documents = [json.loads(line) for line in f]

with open(output_file, "w", encoding="utf-8") as f:
    for doc in documents:
        text = doc["text"]

        words = text.split()

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])

            item = {
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "url": doc["url"],
                "text": chunk
            }

            f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("Chunking completed.")