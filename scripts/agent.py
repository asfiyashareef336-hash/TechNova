class AgentState:
    def __init__(self, question):
        self.question = question
        self.evidence = []
        self.actions = []
        self.missing_information = []
        self.is_complete = False