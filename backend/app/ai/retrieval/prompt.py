def build_prompt(query, docs, memory_context=""):
    sources = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are an enterprise AI assistant.

Use the context if available.
If context is missing, answer using your general knowledge.

Conversation Context:
{memory_context}

Knowledge Base:
{sources}

User Question:
{query}

Answer:
"""
    return prompt
