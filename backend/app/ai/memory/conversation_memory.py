conversation_store = []

def get_conversation(session_id):

    return conversation_store.get(session_id, [])

def add_message(session_id, message):

    if session_id not in conversation_store:
        conversation_store[session_id] = []

    conversation_store[session_id].append(message)