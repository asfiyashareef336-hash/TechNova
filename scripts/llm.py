import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found in .env file"
    )

client = Groq(api_key=api_key)

MODEL_NAME = "openai/gpt-oss-120b"

LAST_USAGE = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "time_seconds": 0.0
}


def get_last_usage():
    return LAST_USAGE.copy()


def generate_answer(question, evidence):

    global LAST_USAGE

    LAST_USAGE = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "time_seconds": 0.0
    }

    if not evidence:
        return "The evidence is insufficient to answer this question."

    unique_evidence = []
    seen = set()

    for item in evidence:

        doc_id = item.get("doc_id", "")

        if not doc_id:
            continue

        if doc_id in seen:
            continue

        seen.add(doc_id)
        unique_evidence.append(item)

    if not unique_evidence:
        return "The evidence is insufficient to answer this question."

    context_parts = []

    MAX_CONTEXT_CHARS = 8000
    current_chars = 0

    for item in unique_evidence:

        doc_id = item.get("doc_id", "")
        title = item.get("title", "")
        text = item.get("text", "")

        text = text[:800]

        source_text = (
            f"\nSource: {doc_id}\n"
            f"Title: {title}\n"
            f"Text: {text}\n"
        )

        if current_chars + len(source_text) > MAX_CONTEXT_CHARS:
            break

        context_parts.append(source_text)
        current_chars += len(source_text)

    context = "".join(context_parts)

    prompt = f"""
You are an answer-generation component of an Agentic GraphRAG system.

Answer the question using ONLY the retrieved evidence.

Rules:
- Use only the supplied evidence.
- Do not use outside knowledge.
- Do not invent facts.
- If the evidence is insufficient, say:
  The evidence is insufficient to answer this question.
- Answer all parts of the question.
- For counting questions, count only records supported by the evidence.
- For comparison questions, use only numbers found in the evidence.
- Keep the answer concise.
- Mention the source document IDs used.

Question:
{question}

Retrieved Evidence:
{context}

Give only the final answer.
"""

    start_time = time.perf_counter()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        reasoning_effort="low",
        max_completion_tokens=1024
    )

    elapsed_time = time.perf_counter() - start_time

    usage = getattr(response, "usage", None)

    if usage is not None:

        LAST_USAGE["prompt_tokens"] = getattr(
            usage,
            "prompt_tokens",
            0
        )

        LAST_USAGE["completion_tokens"] = getattr(
            usage,
            "completion_tokens",
            0
        )

        LAST_USAGE["total_tokens"] = getattr(
            usage,
            "total_tokens",
            0
        )

    LAST_USAGE["time_seconds"] = round(
        elapsed_time,
        3
    )

    message = response.choices[0].message

    content = message.content

    if content is None:
        return "The model returned an empty answer."

    content = content.strip()

    if not content:
        return "The model returned an empty answer."

    return content