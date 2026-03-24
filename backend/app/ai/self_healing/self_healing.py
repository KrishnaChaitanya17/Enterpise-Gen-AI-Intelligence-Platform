async def self_heal_rag(query: str, rag_output: dict, run_rag):

    answer = rag_output.get("answer")

    # 🔥 condition for retry
    if not answer or len(answer) < 30:

        improved_query = f"Provide a detailed and accurate answer: {query}"

        retry_output = await run_rag(improved_query)

        return retry_output

    return rag_output