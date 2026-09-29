from vector_search import search
from graph_search import get_related_documents


def collect_evidence(question, top_k=3):
    vector_results = search(question, top_k)
    evidence = []
    seen = set()

    for result in vector_results:
        if result["doc_id"] not in seen:
            evidence.append(result)
            seen.add(result["doc_id"])

        related_docs = get_related_documents(result["doc_id"])

        for doc in related_docs:
            if doc["doc_id"] not in seen:
                evidence.append(doc)
                seen.add(doc["doc_id"])

    return evidence


if __name__ == "__main__":
    question = input("Enter your question: ")
    results = collect_evidence(question)

    print("\nCollected Evidence:\n")

    for result in results:
        print("Title:", result["title"])
        print("Doc ID:", result["doc_id"])
        print("Text:", result.get("text", "")[:300])
        print("-" * 50)