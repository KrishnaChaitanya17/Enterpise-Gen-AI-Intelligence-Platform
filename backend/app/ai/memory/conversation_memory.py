from collections import deque

class ConversationMemory:
    def __init__(self, max_turns=5):
        self.history = deque(maxlen=max_turns)

    def add(self, user_query: str, answer: str):
        self.history.append({
            "question": user_query,
            "answer": answer
        })

    def get_context(self) -> str:
        context = ""
        for turn in self.history:
            context += f"User: {turn['question']}\n"
            context += f"Assistant: {turn['answer']}\n"
        return context
