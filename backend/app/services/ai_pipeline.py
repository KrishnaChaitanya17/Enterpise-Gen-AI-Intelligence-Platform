import uuid
import time
from datetime import datetime

from app.ai.retrieval.rag_chain import run_rag
from app.ai.reasoning.reasoning_orchestrator import run_decision_reasoning
from app.ai.evaluation.evaluator import evaluate_response
from app.ai.evaluation.enterprise_pipeline import run_enterprise_pipeline
from app.ai.moderation.multiagent.moderation_orchestrator import run_multiagent_moderation
from app.ai.guardrails.hallucination_guard import hallucination_guard
from app.ai.cache.semantic_cache import search_cache, add_to_cache
from app.ai.observability.trace_schema import AITrace
from app.ai.observability.trace_store import save_trace
from app.core.logging import logger

# Optional fallback LLM
from app.ai.llm.llm_client import ask_llm


class AIPipeline:

    async def run(self, query: str, user_id: str):

        trace_id = str(uuid.uuid4())
        start_time = time.time()

        try:

            logger.info(f"TRACE_ID={trace_id} | Query received: {query}")

            # ---------------------------------
            # 0️⃣ Semantic Cache
            # ---------------------------------

            cached_answer = search_cache(query)

            if cached_answer:

                logger.info(f"TRACE_ID={trace_id} | Cache HIT")

                latency = time.time() - start_time

                enterprise_result = {
                    "trust_score": 0.9,
                    "decision": "CACHE_RESPONSE"
                }

                trace = AITrace(
                    trace_id=trace_id,
                    user_id=user_id,
                    query=query,
                    answer=cached_answer,
                    verification={},
                    moderation={},
                    evaluation={},
                    enterprise=enterprise_result,
                    latency=latency,
                    timestamp=datetime.utcnow()
                )

                save_trace(trace)

                return {
                    "trace_id": trace_id,
                    "user_id": user_id,
                    "answer": cached_answer,
                    "confidence": "high",
                    "moderation_status": "ALLOW",
                    "enterprise": enterprise_result
                }

            logger.info(f"TRACE_ID={trace_id} | Cache MISS")

            # ---------------------------------
            # 1️⃣ RAG Retrieval
            # ---------------------------------

            rag_result = await run_rag(query)

            answer = rag_result.get("answer", "")
            sources = rag_result.get("sources", [])
            verification_result = rag_result.get("verification", {})

            # ---------------------------------
            # 2️⃣ RAG Fallback (NEW)
            # ---------------------------------

            if not sources:

                logger.info(f"TRACE_ID={trace_id} | RAG returned no sources — using LLM fallback")

                answer = await ask_llm(query)

                verification_result = {
                    "verdict": "UNVERIFIED",
                    "confidence": "medium"
                }

            # ---------------------------------
            # 3️⃣ Hallucination Guard
            # ---------------------------------

            guard_ok = await hallucination_guard(query, answer, sources)

            if not guard_ok:
                answer = "The generated answer may contain hallucinations and cannot be verified."

            # ---------------------------------
            # 4️⃣ Moderation
            # ---------------------------------

            moderation_result = run_multiagent_moderation(query, answer)

            # ---------------------------------
            # 5️⃣ Reasoning Agents
            # ---------------------------------

            reasoning_input = {
                "query": query,
                "answer": answer,
                "verification": verification_result,
                "sources": sources,
                "risk_score": moderation_result.get("risk_score", 0.0),
                "moderation_status": moderation_result.get("final_verdict", "ALLOW"),
            }

            reasoning_result = await run_decision_reasoning(reasoning_input)

            # reasoning can override answer
            final_answer = reasoning_result.get("final_answer", answer)

            # ---------------------------------
            # 6️⃣ Fallback Safety Layer
            # ---------------------------------

            final_answer = self._apply_fallback(final_answer, verification_result)

            # ---------------------------------
            # 7️⃣ Evaluation
            # ---------------------------------

            evaluation_result = evaluate_response(
                query=query,
                answer=final_answer,
                verification=verification_result,
                confidence=verification_result.get("confidence", "low"),
                sources=sources
            )

            # ---------------------------------
            # 8️⃣ Enterprise Trust Score
            # ---------------------------------

            enterprise_result = run_enterprise_pipeline(
                verification_result,
                evaluation_result,
                moderation_result
            )

            logger.info(f"TRACE_ID={trace_id} | Enterprise: {enterprise_result}")

            # ---------------------------------
            # 9️⃣ Cache Only High Trust
            # ---------------------------------

            if enterprise_result["trust_score"] > 0.7:
                add_to_cache(query, final_answer)

            # ---------------------------------
            # 🔟 Observability Trace
            # ---------------------------------

            latency = time.time() - start_time

            trace = AITrace(
                trace_id=trace_id,
                user_id=user_id,
                query=query,
                answer=final_answer,
                verification=verification_result,
                moderation=moderation_result,
                evaluation=evaluation_result.__dict__,
                enterprise=enterprise_result,
                latency=latency,
                timestamp=datetime.utcnow()
            )

            save_trace(trace)

            return {
                "trace_id": trace_id,
                "user_id": user_id,
                "answer": final_answer,
                "confidence": verification_result.get("confidence", "low"),
                "moderation_status": moderation_result.get("final_verdict", "ALLOW"),
                "enterprise": enterprise_result
            }

        except Exception:

            logger.exception(f"TRACE_ID={trace_id} | Pipeline failure")

            return {
                "trace_id": trace_id,
                "user_id": user_id,
                "answer": "An internal error occurred. Please try again later.",
                "confidence": "low",
                "moderation_status": "ALLOW",
                "enterprise": {
                    "trust_score": 0.0,
                    "decision": "SYSTEM_ERROR"
                }
            }

    def _apply_fallback(self, answer: str, verification_result: dict):

        confidence = verification_result.get("confidence", "low")

        if not answer or answer.strip() == "":
            return "I couldn't find enough reliable information to answer this."

        if confidence == "low":
            return (
                "I'm not fully confident about this answer. "
                "You may want to verify from trusted sources.\n\n"
                f"Preliminary answer: {answer}"
            )

        return answer


ai_pipeline = AIPipeline()


# 1️⃣ RAG → generates answer
# 2️⃣ Verification → validates it
# 3️⃣ Moderation → safety check
# 4️⃣ Reasoning → governance decision
# 5️⃣ Evaluation → scoring
# 6️⃣ Enterprise → final trust scoring



# 14 layers of an advanced AI pipeline:
# 1 Query API
# 2 Semantic Cache
# 3 Vector Retrieval (FAISS)
# 4 LLM Generation
# 5 Claim Verification
# 6 Hallucination Guardrail
# 7 Multi-Agent Moderation
# 8 Multi-Agent Reasoning
# 9 Fallback Recovery
# 10 Response Evaluation
# 11 Enterprise Trust Scoring
# 12 Logging Observability
# 13 Mongo Trace Storage
# 14 Semantic Cache Learning