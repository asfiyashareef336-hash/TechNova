import json

files = [
    "data/corpus.jsonl",
    "data/eval_public.jsonl",
    "data/eval_hidden.jsonl"
]

for file in files:
    print("\nFILE:", file)

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print("Number of lines:", len(lines))

    first = json.loads(lines[0])

    print("Fields:", list(first.keys()))
    print("First object:")
    print(first)