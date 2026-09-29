from agent_state import AgentState


def decide_next_action(state: AgentState):
    question = state.question.lower()

    if "vector_search" not in state.actions:
        state.add_trace(
            action="vector_search",
            details="Starting investigation with semantic vector search."
        )

        return "vector_search"

    if "graph_search" not in state.actions:
        complex_words = [
            "who",
            "which",
            "when",
            "where",
            "how many",
            "compare",
            "difference",
            "related",
            "represent",
            "defeat",
            "before",
            "after",
            "more than",
            "less than"
        ]

        if any(word in question for word in complex_words):
            state.add_trace(
                action="graph_search",
                details=(
                    "The question requires additional relationships "
                    "or multi-hop evidence."
                )
            )

            return "graph_search"

        if len(state.evidence) < 3:
            state.add_trace(
                action="graph_search",
                details=(
                    "Insufficient evidence found, so graph exploration "
                    "is required."
                )
            )

            return "graph_search"

        state.add_trace(
            action="evaluate_evidence",
            details="Enough evidence is available for evaluation."
        )

        return "evaluate_evidence"

    if "evaluate_evidence" not in state.actions:
        state.add_trace(
            action="evaluate_evidence",
            details=(
                "Evaluating retrieved evidence for relevance "
                "and completeness."
            )
        )

        return "evaluate_evidence"

    state.is_complete = True
    state.stop_reason = (
        "Investigation completed after evidence evaluation."
    )

    state.add_trace(
        action="stop",
        details=state.stop_reason
    )

    return "stop"