# step 5 baseline flow
# from app.rag.step2_query.retriever import retrieve_docs
# from app.rag.step2_query.generator import generate_answer
# from app.rag.step4_verification.verifier_agent import verify_answer
# from app.rag.step4_verification.decision_engine import finalize_response


# def retrieve_node(state):
#     docs = retrieve_docs(state["query"])
#     state["docs"] = docs
#     return state


# def generate_node(state):
#     answer = generate_answer(state["query"], state["docs"])
#     state["answer"] = answer
#     return state


# def verify_node(state):
#     verification = verify_answer(state["answer"], state["docs"])
#     state["verification"] = verification
#     return state


# def finalize_node(state):
#     final = finalize_response(
#         state["answer"],
#         state["verification"]
#     )
#     state["final_answer"] = final
#     return state

#step 5.2

from app.ai.retrieval.rag_chain import run_rag


async def generate_node(state):

    result = await run_rag(state["query"])

    return {
        "query": state["query"],
        "answer": result["answer"],
        "verification": result["verification"],
        "confidence": result["confidence"]
    }


async def regenerate_node(state):

    result = await run_rag(state["query"])

    return {
        "query": state["query"],
        "answer": result["answer"],
        "verification": result["verification"],
        "confidence": result["confidence"]
    }