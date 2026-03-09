# async def retry_with_reasoning(query,rag_answer,verification):

#     if verification.get("verdict") == "SUPPORTED":
#         return rag_answer
    
#     retry_prompt = f"""
# The original answer may be incorrect orr unsupported.retry_with_reasoning

# Question:
# {query}

# Previous Answer:
# {rag_answer}

# Please regenerate a better answer using general knowledge.
# """
    
#     from app.core.llm_client import get_llm

#     llm = get_llm()
#     improved = await llm.ainvoke(retry_prompt)

#     return improved

from app.core.llm_client import get_llm


async def retry_with_reasoning(query: str, rag_answer: str, verification: dict) -> str:

    if verification.get("verdict") == "SUPPORTED":
        return rag_answer

    retry_prompt = f"""
The original answer may be incorrect or unsupported.

Question:
{query}

Previous Answer:
{rag_answer}

Please regenerate a better answer using your general knowledge.
"""

    llm = get_llm()
    improved = await llm.ainvoke(retry_prompt)