from langchain.prompts import PromptTemplate

RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an internal company assistant.
Answer the question ONLY using the context below.
If the answer is not present, say:
"I don't have enough information."

Context:
{context}

Question:
{question}

Answer:
"""
)
