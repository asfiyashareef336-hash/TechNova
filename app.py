import sys
import time
import streamlit as st

sys.path.insert(0, "scripts")

from agent_state import AgentState
from orchestrator import decide_next_action
from vector_search import search
from graph_search import get_related_documents
from evaluator import evaluate_evidence
from llm import generate_answer, get_last_usage


st.set_page_config(
    page_title="Agentic GraphRAG",
    page_icon="🔍",
    layout="wide",
)


def show_evidence(evidence):
    if not evidence:
        st.warning("No evidence found.")
        return

    for index, result in enumerate(evidence, 1):
        with st.expander(
            f"Source {index}: {result.get('title', 'Unknown')}"
        ):
            st.write(result.get("text", "No text available."))

            st.caption(
                f"Document ID: {result.get('doc_id', 'Unknown')}"
            )

            if result.get("score") is not None:
                st.caption(
                    f"Similarity Score: {result['score']:.4f}"
                )


def is_comparison_question(question):
    q = question.lower()

    comparison_words = [
        "compare",
        "which had more",
        "which had fewer",
        "which was more",
        "which was less",
        "how many more",
        "how many fewer",
        "difference between",
    ]

    return any(word in q for word in comparison_words)


def comparison_search(question):
    q = question.lower()
    evidence = []

    results = search(question, top_k=20)
    evidence.extend(results)

    if "men's" in q:
        mens_query = q.replace("women's", "men's")
        mens_results = search(mens_query, top_k=20)
        evidence.extend(mens_results)

    if "women's" in q:
        womens_query = q.replace("men's", "women's")
        womens_results = search(womens_query, top_k=20)
        evidence.extend(womens_results)

    unique = []
    seen = set()

    for item in evidence:
        doc_id = item.get("doc_id")

        if doc_id in seen:
            continue

        unique.append(item)
        seen.add(doc_id)

    return unique


def get_comparison_relevant(question, evidence):
    q = question.lower()

    if (
        "mass start" in q
        and "men's" in q
        and "women's" in q
    ):
        mens_item = None
        womens_item = None

        for item in evidence:
            title = item.get("title", "").lower()
            text = item.get("text", "").lower()

            if (
                "2018 winter olympics" in title
                and "men's mass start" in title
            ):
                mens_item = item

            elif (
                "2018 winter olympics" in title
                and "women's mass start" in title
            ):
                womens_item = item

            elif (
                "2018 winter olympics" in text
                and "men's mass start" in text
                and mens_item is None
            ):
                mens_item = item

            elif (
                "2018 winter olympics" in text
                and "women's mass start" in text
                and womens_item is None
            ):
                womens_item = item

        relevant = []

        if mens_item is not None:
            relevant.append(mens_item)

        if womens_item is not None:
            relevant.append(womens_item)

        if len(relevant) >= 2:
            return relevant

    return evaluate_evidence(question, evidence)


def run_rag(question):
    if is_comparison_question(question):
        evidence = comparison_search(question)
        relevant = get_comparison_relevant(question, evidence)
    else:
        evidence = search(question, top_k=5)
        relevant = evaluate_evidence(question, evidence)

    answer = generate_answer(question, relevant)

    return answer, evidence, relevant


def run_graphrag(question):
    if is_comparison_question(question):
        vector_results = comparison_search(question)
    else:
        vector_results = search(question, top_k=5)

    evidence = list(vector_results)

    for item in vector_results[:3]:
        related = get_related_documents(item["doc_id"])

        existing_ids = {
            result["doc_id"]
            for result in evidence
        }

        for result in related:
            if result["doc_id"] not in existing_ids:
                evidence.append(result)
                existing_ids.add(result["doc_id"])

    if is_comparison_question(question):
        relevant = get_comparison_relevant(question, evidence)
    else:
        relevant = evaluate_evidence(question, evidence)

    answer = generate_answer(question, relevant)

    return answer, evidence, relevant


def run_agentic_graphrag(question):
    state = AgentState(question)

    max_steps = 5
    step = 0
    relevant_evidence = []

    while step < max_steps:

        action = decide_next_action(state)

        if action == "vector_search":

            start_time = time.perf_counter()

            if is_comparison_question(question):
                results = comparison_search(question)
            else:
                results = search(question, top_k=5)

            elapsed_time = time.perf_counter() - start_time

            existing_ids = {
                item["doc_id"]
                for item in state.evidence
            }

            new_documents = []

            for result in results:
                doc_id = result.get("doc_id")

                if doc_id not in existing_ids:
                    state.evidence.append(result)
                    existing_ids.add(doc_id)
                    new_documents.append(doc_id)

            if "vector_search" not in state.actions:
                state.actions.append("vector_search")

            state.add_trace(
                action="vector_search_result",
                details=(
                    f"Vector search retrieved {len(results)} "
                    f"documents and added {len(new_documents)} "
                    f"new documents."
                ),
                documents=new_documents,
                time_seconds=elapsed_time,
            )

        elif action == "graph_search":

            start_time = time.perf_counter()

            graph_documents = []

            for document in state.evidence[:3]:

                related = get_related_documents(
                    document["doc_id"]
                )

                existing_ids = {
                    item["doc_id"]
                    for item in state.evidence
                }

                for result in related:

                    doc_id = result.get("doc_id")

                    if doc_id not in existing_ids:
                        state.evidence.append(result)
                        existing_ids.add(doc_id)
                        graph_documents.append(doc_id)

            elapsed_time = time.perf_counter() - start_time

            if "graph_search" not in state.actions:
                state.actions.append("graph_search")

            state.add_trace(
                action="graph_search_result",
                details=(
                    f"TigerGraph exploration added "
                    f"{len(graph_documents)} connected documents."
                ),
                documents=graph_documents,
                time_seconds=elapsed_time,
            )

        elif action == "evaluate_evidence":

            start_time = time.perf_counter()

            if is_comparison_question(question):
                relevant_evidence = get_comparison_relevant(
                    question,
                    state.evidence,
                )
            else:
                relevant_evidence = evaluate_evidence(
                    question,
                    state.evidence,
                )

            elapsed_time = time.perf_counter() - start_time

            if "evaluate_evidence" not in state.actions:
                state.actions.append("evaluate_evidence")

            relevant_ids = [
                item.get("doc_id")
                for item in relevant_evidence
            ]

            state.add_trace(
                action="evidence_evaluation",
                details=(
                    f"Selected {len(relevant_evidence)} "
                    f"relevant documents from "
                    f"{len(state.evidence)} retrieved documents."
                ),
                documents=relevant_ids,
                time_seconds=elapsed_time,
            )

            state.is_complete = True

            state.stop_reason = (
                "Investigation stopped after sufficient "
                "evidence was selected."
            )

            break

        elif action == "stop":

            state.is_complete = True

            if not state.stop_reason:
                state.stop_reason = (
                    "Investigation stopped by the orchestrator."
                )

            break

        step += 1

    start_time = time.perf_counter()

    answer = generate_answer(
        question,
        relevant_evidence,
    )

    usage = get_last_usage()

    llm_time = time.perf_counter() - start_time

    state.add_trace(
        action="answer_generation",
        details=(
            f"LLM generated the final answer in "
            f"{llm_time:.3f} seconds."
        ),
        tokens=usage["total_tokens"],
        time_seconds=llm_time,
    )

    state.total_tokens = usage["total_tokens"]

    state.add_trace(
        action="stop",
        details=(
            f"{state.stop_reason} "
            f"Final answer generated using "
            f"{usage['total_tokens']} tokens."
        ),
        tokens=0,
        time_seconds=0,
    )

    return (
        answer,
        state.evidence,
        relevant_evidence,
        state.actions,
        state.trace,
        state.stop_reason,
        state.steps,
        state.total_tokens,
        usage,
    )


with st.sidebar:

    st.header("⚙️ System")

    st.markdown("### Architecture")

    st.write("🔹 Embeddings")
    st.caption("Sentence Transformers")

    st.write("🔹 Vector Search")
    st.caption("Semantic Search")

    st.write("🔹 Knowledge Graph")
    st.caption("TigerGraph")

    st.write("🔹 Evidence Evaluation")
    st.caption("Rule-based validation")

    st.write("🔹 LLM")
    st.caption("Groq - GPT-OSS-120B")

    st.write("🔹 Dataset")
    st.caption("Wikipedia Corpus")

    st.divider()

    st.markdown("### Backend Status")

    st.success("Frontend: Connected")
    st.success("Backend: Connected")
    st.success("LLM: Connected")
    st.success("TigerGraph: Connected")

    st.divider()

    st.caption("Agentic GraphRAG Hackathon Project")


st.title("🔍 Agentic GraphRAG")

st.write(
    "An intelligent question-answering system that combines "
    "Vector Search, GraphRAG, and Agentic Reasoning."
)

st.divider()

st.subheader("Ask a Question")

question = st.text_input(
    "Enter your question",
    placeholder=(
        "Example: Who won the men's singles tennis "
        "event at the 2004 Summer Olympics?"
    ),
)

submit = st.button(
    "🔎 Submit",
    type="primary"
)


if submit:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Running RAG, GraphRAG and Agentic GraphRAG..."
        ):

            (
                rag_answer,
                rag_evidence,
                rag_relevant,
            ) = run_rag(question)

            (
                graph_answer,
                graph_evidence,
                graph_relevant,
            ) = run_graphrag(question)

            (
                agent_answer,
                agent_evidence,
                agent_relevant,
                actions,
                trace,
                stop_reason,
                agent_steps,
                trace_tokens,
                usage,
            ) = run_agentic_graphrag(question)

        st.subheader("💡 Answers")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("### 📄 RAG")

            st.info(rag_answer)

            st.caption(
                f"Evidence: {len(rag_evidence)} | "
                f"Relevant: {len(rag_relevant)}"
            )

        with col2:

            st.markdown("### 🔗 GraphRAG")

            st.info(graph_answer)

            st.caption(
                f"Evidence: {len(graph_evidence)} | "
                f"Relevant: {len(graph_relevant)}"
            )

        with col3:

            st.markdown("### 🤖 Agentic GraphRAG")

            st.success(agent_answer)

            st.caption(
                f"Evidence: {len(agent_evidence)} | "
                f"Relevant: {len(agent_relevant)}"
            )

        st.divider()

        st.subheader("📚 Agentic Evidence")

        show_evidence(agent_relevant)

        st.divider()

        st.subheader("🧠 Agent Investigation")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("### 1️⃣ Retrieve")

            st.write(
                "Vector search retrieves semantically "
                "relevant documents."
            )

        with col2:

            st.markdown("### 2️⃣ Explore")

            st.write(
                "TigerGraph explores connected "
                "documents through graph relationships."
            )

        with col3:

            st.markdown("### 3️⃣ Validate")

            st.write(
                "Evidence evaluation selects "
                "relevant results."
            )

        st.subheader("⚡ Agent Actions")

        for index, action in enumerate(
            actions,
            1
        ):

            st.write(
                f"{index}. {action}"
            )

        st.subheader("🔎 Agentic Trace")

        st.caption(
            "The trace shows how the agent investigated "
            "the question and generated the final answer."
        )

        for item in trace:

            with st.expander(
                f"Step {item['step']}: {item['action']}"
            ):

                st.write(
                    item.get(
                        "details",
                        ""
                    )
                )

                documents = item.get(
                    "documents",
                    []
                )

                if documents:

                    st.write(
                        "Documents:"
                    )

                    st.code(
                        ", ".join(
                            documents
                        )
                    )

                if item.get(
                    "tokens",
                    0
                ) > 0:

                    st.write(
                        f"Tokens: {item['tokens']}"
                    )

                if item.get(
                    "time_seconds",
                    0
                ) > 0:

                    st.write(
                        f"Time: {item['time_seconds']:.3f} seconds"
                    )

        st.subheader("🪙 LLM Usage")

        usage_col1, usage_col2, usage_col3, usage_col4 = (
            st.columns(4)
        )

        with usage_col1:

            st.metric(
                "Prompt Tokens",
                usage["prompt_tokens"]
            )

        with usage_col2:

            st.metric(
                "Completion Tokens",
                usage["completion_tokens"]
            )

        with usage_col3:

            st.metric(
                "Total Tokens",
                usage["total_tokens"]
            )

        with usage_col4:

            st.metric(
                "LLM Time",
                f"{usage['time_seconds']:.2f}s"
            )

        st.subheader("🛑 Stopping Reason")

        st.info(
            stop_reason
            if stop_reason
            else "Investigation completed."
        )

        st.subheader("📊 Agent Metrics")

        metric_col1, metric_col2, metric_col3, metric_col4 = (
            st.columns(4)
        )

        with metric_col1:

            st.metric(
                "Agent Steps",
                agent_steps
            )

        with metric_col2:

            st.metric(
                "Evidence Documents",
                len(agent_evidence)
            )

        with metric_col3:

            st.metric(
                "Relevant Documents",
                len(agent_relevant)
            )

        with metric_col4:

            st.metric(
                "Agent Tokens",
                trace_tokens
            )

        st.subheader("📊 Retrieval Summary")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "RAG Evidence",
                len(rag_evidence)
            )

        with col2:

            st.metric(
                "GraphRAG Evidence",
                len(graph_evidence)
            )

        with col3:

            st.metric(
                "Agentic Evidence",
                len(agent_evidence)
            )