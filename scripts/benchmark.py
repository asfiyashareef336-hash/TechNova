import json
import sys
import time

sys.path.insert(0, "scripts")

from vector_search import search
from graph_search import get_related_documents
from evaluator import evaluate_evidence
from agent_state import AgentState
from orchestrator import decide_next_action


INPUT_FILE = "data/eval_public.jsonl"


def load_questions():
    questions = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))

    return questions


def estimate_tokens(text):
    return max(1, len(text) // 4)


def get_graph_evidence(question):
    vector_results = search(question, top_k=5)

    evidence = list(vector_results)

    if vector_results:
        doc_id = vector_results[0]["doc_id"]

        related = get_related_documents(
            doc_id,
            max_results=5
        )

        existing_ids = {
            item["doc_id"]
            for item in evidence
        }

        for item in related:
            if item["doc_id"] not in existing_ids:
                evidence.append(item)
                existing_ids.add(item["doc_id"])

    return evidence


def get_agentic_evidence(question):
    state = AgentState(question)

    max_steps = 5
    step = 0

    while step < max_steps:

        action = decide_next_action(state)

        if action == "vector_search":

            results = search(
                question,
                top_k=5
            )

            existing_ids = {
                item["doc_id"]
                for item in state.evidence
            }

            for result in results:

                if result["doc_id"] not in existing_ids:
                    state.evidence.append(result)
                    existing_ids.add(result["doc_id"])

            state.actions.append("vector_search")

        elif action == "graph_search":

            selected_documents = state.evidence[:3]

            for document in selected_documents:

                related = get_related_documents(
                    document["doc_id"],
                    max_results=5
                )

                existing_ids = {
                    item["doc_id"]
                    for item in state.evidence
                }

                for result in related:

                    if result["doc_id"] not in existing_ids:
                        state.evidence.append(result)
                        existing_ids.add(result["doc_id"])

            state.actions.append("graph_search")

        elif action == "evaluate_evidence":

            relevant = evaluate_evidence(
                question,
                state.evidence
            )

            state.actions.append(
                "evaluate_evidence"
            )

            return state.evidence, relevant

        elif action == "stop":

            break

        step += 1

    relevant = evaluate_evidence(
        question,
        state.evidence
    )

    return state.evidence, relevant


def calculate_metrics(name, results):

    total = len(results)

    if total == 0:
        return {
            "pipeline": name,
            "questions": 0,
            "accuracy": 0,
            "completeness": 0,
            "tokens": 0
        }

    correct = 0
    completeness_scores = []
    total_tokens = 0

    for result in results:

        gold_ids = set(
            result["gold_doc_ids"]
        )

        retrieved_ids = set(
            result["retrieved_doc_ids"]
        )

        overlap = gold_ids.intersection(
            retrieved_ids
        )

        if overlap:
            correct += 1

        if gold_ids:
            completeness = (
                len(overlap) /
                len(gold_ids)
            )
        else:
            completeness = 0

        completeness_scores.append(
            completeness
        )

        total_tokens += result["tokens"]

    accuracy = (
        correct / total
    ) * 100

    completeness = (
        sum(completeness_scores) /
        total
    ) * 100

    average_tokens = (
        total_tokens / total
    )

    return {
        "pipeline": name,
        "questions": total,
        "accuracy": round(
            accuracy,
            2
        ),
        "completeness": round(
            completeness,
            2
        ),
        "tokens": round(
            average_tokens,
            0
        )
    }


def run_benchmark():

    questions = load_questions()

    print()
    print("=" * 60)
    print(
        "AGENTIC GRAPHRAG ROUND 1 BENCHMARK"
    )
    print("=" * 60)
    print()

    print(
        "Questions:",
        len(questions)
    )

    print()

    rag_results = []
    graph_results = []
    agent_results = []

    start_time = time.time()

    for index, item in enumerate(
        questions,
        1
    ):

        question = item["question"]
        gold_ids = item["gold_doc_ids"]

        print(
            f"[{index}/{len(questions)}] "
            f"{question[:80]}"
        )

        # -------------------------
        # RAG
        # -------------------------

        vector_results = search(
            question,
            top_k=5
        )

        rag_relevant = evaluate_evidence(
            question,
            vector_results
        )

        rag_ids = [
            x["doc_id"]
            for x in rag_relevant
        ]

        rag_text = " ".join(
            x.get("text", "")
            for x in rag_relevant
        )

        rag_results.append({
            "qid": item["qid"],
            "gold_doc_ids": gold_ids,
            "retrieved_doc_ids": rag_ids,
            "tokens": estimate_tokens(
                rag_text
            )
        })

        # -------------------------
        # GraphRAG
        # -------------------------

        graph_evidence = get_graph_evidence(
            question
        )

        graph_relevant = evaluate_evidence(
            question,
            graph_evidence
        )

        graph_ids = [
            x["doc_id"]
            for x in graph_relevant
        ]

        graph_text = " ".join(
            x.get("text", "")
            for x in graph_relevant
        )

        graph_results.append({
            "qid": item["qid"],
            "gold_doc_ids": gold_ids,
            "retrieved_doc_ids": graph_ids,
            "tokens": estimate_tokens(
                graph_text
            )
        })

        # -------------------------
        # Agentic GraphRAG
        # -------------------------

        agent_evidence, agent_relevant = (
            get_agentic_evidence(
                question
            )
        )

        agent_ids = [
            x["doc_id"]
            for x in agent_relevant
        ]

        agent_text = " ".join(
            x.get("text", "")
            for x in agent_relevant
        )

        agent_results.append({
            "qid": item["qid"],
            "gold_doc_ids": gold_ids,
            "retrieved_doc_ids": agent_ids,
            "tokens": estimate_tokens(
                agent_text
            )
        })

    elapsed = time.time() - start_time

    rag_metrics = calculate_metrics(
        "RAG",
        rag_results
    )

    graph_metrics = calculate_metrics(
        "GraphRAG",
        graph_results
    )

    agent_metrics = calculate_metrics(
        "Agentic GraphRAG",
        agent_results
    )

    metrics = {
        "questions": len(questions),
        "time_seconds": round(
            elapsed,
            2
        ),
        "pipelines": [
            rag_metrics,
            graph_metrics,
            agent_metrics
        ]
    }

    with open(
        "data/benchmark_results.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metrics,
            f,
            indent=4
        )

    print()
    print("=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)

    for result in metrics["pipelines"]:

        print()
        print(
            result["pipeline"]
        )

        print(
            "Accuracy:",
            result["accuracy"],
            "%"
        )

        print(
            "Completeness:",
            result["completeness"],
            "%"
        )

        print(
            "Average Tokens:",
            result["tokens"]
        )

    print()
    print(
        "Saved to: "
        "data/benchmark_results.json"
    )

    print(
        "Time:",
        round(elapsed, 2),
        "seconds"
    )


if __name__ == "__main__":
    run_benchmark()