from app.rag.prompt import RAG_PROMPT
from backend.app.rag.step3_generation.llm import get_llm

def answer_question(vector_db, question):
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in docs)

    llm = get_llm()
    prompt = RAG_PROMPT.format(
        context=context,
        question=question
    )

    response = llm.invoke(prompt)
    return response.content
