import uuid
import time
from datetime import datetime
from typing import Optional

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
from app.domain.repositories.interaction_repository import InteractionRepository
from app.core.llm_client import get_llm


# --------------------------------------------------
# Helper: detect bad / weak answers
# --------------------------------------------------

def is_bad_answer(answer: str) -> bool:

    if not answer:
        return True

    text = answer.lower().strip()

    bad_patterns = [
        "i don't know",
        "i dont know",
        "unknown",
        "no idea",
        "not sure",
        "cannot answer",
        "can't answer"
    ]

    if len(text) < 20:
        return True

    for pattern in bad_patterns:
        if pattern in text:
            return True

    return False


class AIPipeline:

    async def run(self, query: str, user_id: str, organization_id: Optional[str]):

        trace_id = str(uuid.uuid4())
        start_time = time.time()
        conversation_id = str(uuid.uuid4())

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
                    organization_id=organization_id,
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
            # 1️⃣ RAG
            # ---------------------------------

            rag_result = await run_rag(query)

            answer = rag_result.get("answer") or ""
            sources = rag_result.get("sources") or []
            verification_result = rag_result.get("verification") or {}

            # ---------------------------------
            # 2️⃣ LLM Fallback
            # ---------------------------------

            if not sources or is_bad_answer(answer):

                logger.info(
                    f"TRACE_ID={trace_id} | Using LLM fallback"
                )

                llm = get_llm()

                prompt = f"""
You are a knowledgeable AI assistant.

Provide a clear and helpful explanation.

Do NOT say "I don't know".

Explain the concept clearly.

User question:
{query}

Answer:
"""

                fallback = await llm.ainvoke(prompt)

                answer = getattr(fallback, "content", str(fallback)).strip()

                verification_result = {
                    "verdict": "UNVERIFIED",
                    "confidence": "medium",
                    "checks": []
                }

                # regenerate if still weak
                if is_bad_answer(answer):

                    logger.warning(
                        f"TRACE_ID={trace_id} | Regenerating weak answer"
                    )

                    retry = await llm.ainvoke(
                        f"Explain clearly with examples:\n{query}"
                    )

                    answer = getattr(retry, "content", str(retry)).strip()

            # ---------------------------------
            # 3️⃣ Hallucination Guard
            # ---------------------------------

            if sources:

                guard_ok = await hallucination_guard(query, answer, sources)

                if not guard_ok:

                    logger.warning(
                        f"TRACE_ID={trace_id} | Hallucination risk detected"
                    )

            # ---------------------------------
            # 4️⃣ Moderation
            # ---------------------------------

            moderation_result = run_multiagent_moderation(query, answer)

            if moderation_result.get("final_verdict") == "BLOCK":

                logger.warning(
                    f"TRACE_ID={trace_id} | Moderation BLOCK"
                )

                answer = "This response was blocked by the moderation system."

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

            final_answer = getattr(reasoning_result, "final_answer", None) or answer

            # ---------------------------------
            # 6️⃣ Evaluation
            # ---------------------------------

            evaluation_result = evaluate_response(
                query=query,
                answer=final_answer,
                verification=verification_result,
                confidence=verification_result.get("confidence", "low"),
                sources=sources
            )

            # ---------------------------------
            # 7️⃣ Enterprise Trust
            # ---------------------------------

            enterprise_result = run_enterprise_pipeline(
                verification_result,
                evaluation_result,
                moderation_result
            )

            logger.info(
                f"TRACE_ID={trace_id} | Enterprise decision: {enterprise_result}"
            )

            # ---------------------------------
            # 8️⃣ Save Interaction
            # ---------------------------------

            repo = InteractionRepository()

            await repo.save({
                "trace_id": trace_id,
                "conversation_id": conversation_id,
                "organization_id": organization_id,
                "user_id": user_id,
                "query": query,
                "response": final_answer,
                "enterprise": enterprise_result,
                "created_at": datetime.utcnow()
            })

            # ---------------------------------
            # 9️⃣ Cache High Trust
            # ---------------------------------

            if enterprise_result.get("trust_score", 0) > 0.7:
                add_to_cache(query, final_answer)

            latency = time.time() - start_time

            trace = AITrace(
                trace_id=trace_id,
                user_id=user_id,
                organization_id=organization_id,
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
                "answer": "Internal AI pipeline error.",
                "confidence": "low",
                "moderation_status": "ALLOW",
                "enterprise": {
                    "trust_score": 0.0,
                    "decision": "SYSTEM_ERROR"
                }
            }


ai_pipeline = AIPipeline()

# # 1️⃣ RAG → generates answer
# # 2️⃣ Verification → validates it
# # 3️⃣ Moderation → safety check
# # 4️⃣ Reasoning → governance decision
# # 5️⃣ Evaluation → scoring
# # 6️⃣ Enterprise → final trust scoring



# # 14 layers of an advanced AI pipeline:
# # 1 Query API
# # 2 Semantic Cache
# # 3 Vector Retrieval (FAISS)
# # 4 LLM Generation
# # 5 Claim Verification
# # 6 Hallucination Guardrail
# # 7 Multi-Agent Moderation
# # 8 Multi-Agent Reasoning
# # 9 Fallback Recovery
# # 10 Response Evaluation
# # 11 Enterprise Trust Scoring
# # 12 Logging Observability
# # 13 Mongo Trace Storage
# # 14 Semantic Cache Learning

