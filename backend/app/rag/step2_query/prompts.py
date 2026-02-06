from langchain_core.prompts import ChatPromptTemplate

ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """
You are a precise and factual assistant.

Answer the question using ONLY the provided context.
If the answer is not present in the context, say "I don't know".

Context:
{context}

Question:
{question}

Answer:
"""
)
