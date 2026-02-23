# app/services/enterprise_wrapper.py
import uuid

from app.rag.step2_query.rag_chain import run_rag
from app.rag.step6_evaluation.evaluator import evaluate_response
from app.rag.step9_moderation_langgraph.graph import build_moderation_graph
from app.rag.step14_enterprise.pipeline import run_enterprise_pipeline


class EnterprisePipelineWrapper:

    async def run(self, query: str):

        trace_id = str(uuid.uuid4())  # Generate a unique trace ID for this interaction

        # -----------------------------
        # STEP 1-4 → RAG + Verification
        # -----------------------------
        rag_result = run_rag(query)

        answer = rag_result["answer"]
        verification = rag_result["verification"]
        confidence = rag_result.get("confidence", "low")

        # -----------------------------
        # STEP 6 → Evaluation
        # -----------------------------
        evaluation = evaluate_response(
            query=query,
            answer=answer,
            verification=verification,
            confidence=confidence,
            sources=rag_result["sources"],
        )

        # -----------------------------
        # STEP 7-9 → Moderation
        # -----------------------------
        moderation_graph = build_moderation_graph()

        moderation_state = {
            "query": query,
            "answer": answer,
            "agent_decisions": [],
            "final_verdict": "",
            "redacted_answer": "",
            "audit_trail": [],
        }

        moderation_result = moderation_graph.invoke(moderation_state)

        moderation = {
            "final_verdict": moderation_result["final_verdict"]
        }

        # -----------------------------
        # STEP 14 → Enterprise
        # -----------------------------
        enterprise_result = run_enterprise_pipeline(
            verification,
            evaluation.__dict__,  # 👈 IMPORTANT
            moderation
        )

        return {
            "trace_id": trace_id,  # ✅ ADD THIS
            "query": query,
            "answer": answer,
            "sources": rag_result["sources"],
            "enterprise": enterprise_result
        }
