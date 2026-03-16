from app.ai.retrieval.rag_chain import run_rag


async def retrieval_agent(query: str):

    result = await run_rag(query)

    return {
        "answer": result,
        "source": "retrieval_agent"
    }