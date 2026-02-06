# # app/rag/step2_query/rag_chain.py

# from app.rag.step2_query.retriever import retrieve_docs
# from app.rag.step2_query.prompt import build_prompt
# from app.rag.step2_query.generator import generate_answer

# from app.rag.step4_verification.verifier_agent import verify_answer
# from app.rag.step4_verification.decision_engine import finalize_response

# def run_rag(query: str):
#     docs = retrieve_docs(query)

#     if not docs:
#         return {
#             "answer": "I don’t have enough information to answer this.",
#             "sources": []
#         }

#     prompt = build_prompt(query, docs)
#     answer = generate_answer(prompt)

#     verification = verify_answer(answer, docs)
#     final_response = finalize_response(answer, verification)

#     final_response["sources"] = docs
#     return final_response

# app/rag/step2_query/rag_chain.py

from app.core.llm_config import get_llm
from app.rag.step2_1_retrieval.retriever import get_retrieved_docs
from app.rag.step2_query.prompts import ANSWER_PROMPT
from app.rag.step4_verification.verifier_agent import verify_answer  # ✅ ADD

def run_rag(query: str):
    # 1️⃣ Retrieve documents
    docs = get_retrieved_docs(query)

    # 2️⃣ Prepare context
    context = "\n\n".join(d.page_content for d in docs)

    # 3️⃣ Build prompt
    prompt = ANSWER_PROMPT.format(
        question=query,
        context=context
    )

    # 4️⃣ Generate answer
    llm = get_llm()
    response = llm.invoke(prompt)
    answer = response.content

    # 5️⃣ 🔥 STEP 4 VERIFICATION (THIS WAS MISSING)
    verification = verify_answer(answer, docs)

    # 6️⃣ Return FULL object
    return {
        "query": query,
        "answer": answer,
        "sources": docs,
        "verification": verification,
        "confidence": verification["confidence"],
    }
