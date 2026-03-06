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

from app.ai.step2_query.rag_chain import run_rag

def generate_node(state):
    result = run_rag(state["query"])
    return {
        "answer": result["answer"],
        "verification": result["verification"],
        "confidence": result["confidence"]
    }

def regenerate_node(state):
    # For now, same pipeline (later we tweak prompt / k / retriever)
    result = run_rag_cached(state["query"])
    return {
        "answer": result["answer"],
        "verification": result["verification"],
        "confidence": result["confidence"]
    }
