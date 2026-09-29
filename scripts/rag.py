from vector_search import search

question = input("Enter your question: ")

results = search(question, top_k=5)

context = ""

for result in results:
    context += result["text"] + "\n\n"

print("\nRetrieved Context:\n")
print(context[:5000])