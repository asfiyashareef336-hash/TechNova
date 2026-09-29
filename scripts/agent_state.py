class AgentState:
    def __init__(self, question):
        self.question = question
        self.evidence = []
        self.actions = []
        self.missing_information = []
        self.is_complete = False

        self.trace = []
        self.total_tokens = 0
        self.steps = 0
        self.stop_reason = ""

    def add_trace(
        self,
        action,
        details="",
        documents=None,
        tokens=0,
        time_seconds=0.0
    ):
        if documents is None:
            documents = []

        self.trace.append({
            "step": self.steps + 1,
            "action": action,
            "details": details,
            "documents": documents,
            "tokens": tokens,
            "time_seconds": round(time_seconds, 3)
        })

        self.steps += 1
        self.total_tokens += tokens