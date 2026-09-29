import os
import re
from dotenv import load_dotenv
from pyTigerGraph import TigerGraphConnection

load_dotenv()

HOST = "https://tg-86328c90-ce61-46c7-a6de-509fcd350ec3.tg-2635877100.i.tgcloud.io"
GRAPH_NAME = "AgenticGraphRAG"

conn = TigerGraphConnection(
    host=HOST,
    graphname=GRAPH_NAME,
    gsqlSecret=os.getenv("TIGERGRAPH_SECRET"),
    tgCloud=True
)

conn.getToken(os.getenv("TIGERGRAPH_SECRET"))


def get_words(text):
    return set(re.findall(r"\b[a-zA-Z0-9]+\b", text.lower()))


def get_related_documents(doc_id, max_results=5):
    edges = conn.getEdges(
        "Document",
        doc_id,
        edgeType="RelatedTo",
        targetVertexType="Document"
    )

    results = []

    for edge in edges:
        target_id = edge["to_id"]

        documents = conn.getVerticesById(
            "Document",
            target_id
        )

        if not documents:
            continue

        document = documents[0]

        attributes = document.get("attributes", {})

        results.append({
            "doc_id": target_id,
            "title": attributes.get("title", ""),
            "text": attributes.get("text", ""),
            "url": attributes.get("url", ""),
            "graph_score": 0
        })

    source_documents = conn.getVerticesById("Document", doc_id)

    if source_documents:
        source_text = source_documents[0].get("attributes", {}).get("text", "")
        source_words = get_words(source_text)

        for result in results:
            target_words = get_words(result["text"])
            result["graph_score"] = len(
                source_words.intersection(target_words)
            )

    results.sort(
        key=lambda result: result["graph_score"],
        reverse=True
    )

    return results[:max_results]