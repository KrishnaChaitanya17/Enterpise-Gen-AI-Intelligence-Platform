def build_prompt(query, docs, memory_context=""):
    sources = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are an enterprise assistant.
Answer ONLY using the information provided.
If unsure, say you don't know.

Conversation Context:
{memory_context}

Knowledge Base:
{sources}

User Question:
{query}

Answer:
"""
    return prompt
