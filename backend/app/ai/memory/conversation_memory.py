from collections import deque

# ---------------------------------
# GLOBAL MEMORY STORE (session-based)
# ---------------------------------
conversation_store = {}


# ---------------------------------
# CLASS-BASED MEMORY (used in pipeline)
# ---------------------------------
class ConversationMemory:

    def __init__(self, max_turns=5):
        self.history = deque(maxlen=max_turns)

    def add(self, query: str, answer: str):
        self.history.append({
            "query": query,
            "answer": answer
        })

    def get_context(self) -> str:
        if not self.history:
            return ""

        context = ""
        for turn in self.history:
            context += f"User: {turn['query']}\n"
            context += f"Assistant: {turn['answer']}\n"

        return context.strip()


# ---------------------------------
# FUNCTION-BASED MEMORY (used in agents)
# ---------------------------------
def get_conversation(session_id: str):
    return conversation_store.get(session_id, [])


def add_message(session_id: str, message: dict):
    if session_id not in conversation_store:
        conversation_store[session_id] = []

    conversation_store[session_id].append(message)