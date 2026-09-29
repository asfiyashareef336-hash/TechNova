from agent_state import AgentState
from orchestrator import decide_next_action
from vector_search import search
from graph_search import get_related_documents
from evaluator import evaluate_evidence
from answer_generator import generate_answer

question = input("Enter your question: ")

state = AgentState(question)

max_steps = 5
step = 0
relevant_evidence = []

while step < max_steps:

    action = decide_next_action(state)

    print("\nNext Action:", action)

    if action == "vector_search":

        results = search(question, top_k=5)

        existing_ids = {
            result["doc_id"]
            for result in state.evidence
        }

        for result in results:
            if result["doc_id"] not in existing_ids:
                state.evidence.append(result)
                existing_ids.add(result["doc_id"])

        state.actions.append("vector_search")

    elif action == "graph_search":

        # Agent explores multiple promising documents
        # instead of only the first document.
        selected_documents = state.evidence[:3]

        for document in selected_documents:

            related = get_related_documents(
                document["doc_id"],
                max_results=5
            )

            existing_ids = {
                result["doc_id"]
                for result in state.evidence
            }

            for result in related:
                if result["doc_id"] not in existing_ids:
                    state.evidence.append(result)
                    existing_ids.add(result["doc_id"])

        state.actions.append("graph_search")

    elif action == "evaluate_evidence":

        relevant_evidence = evaluate_evidence(
            question,
            state.evidence
        )

        state.actions.append("evaluate_evidence")

        break

    elif action == "stop":

        break

    step += 1


print("\nRelevant Evidence:")

for result in relevant_evidence:
    print("-", result["title"])

answer = generate_answer(
    question,
    relevant_evidence
)

print("\nFinal Answer:")
print(answer)

print("\nTotal Evidence:", len(state.evidence))
print("Relevant Evidence:", len(relevant_evidence))
print("Actions Taken:", state.actions)