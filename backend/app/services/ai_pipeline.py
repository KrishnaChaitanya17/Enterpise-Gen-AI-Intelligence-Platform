import uuid
import time
import asyncio
from datetime import datetime
from typing import Optional

from app.ai.reasoning.reasoning_orchestrator import run_decision_reasoning
from app.ai.evaluation.evaluator import evaluate_response
from app.ai.evaluation.enterprise_pipeline import run_enterprise_pipeline
from app.ai.moderation.multiagent.moderation_orchestrator import run_multiagent_moderation
from app.ai.guardrails.hallucination_guard import hallucination_guard
from app.ai.cache.semantic_cache import search_cache, add_to_cache
from app.ai.observability.trace_schema import AITrace
from app.ai.observability.trace_store import save_trace
from app.ai.observability.cost_tracker import track_cost
from app.core.logging import logger
from app.domain.repositories.interaction_repository import InteractionRepository
from app.core.llm_client import get_llm
from app.ai.memory.conversation_memory import ConversationMemory
from app.ai.observability.tracer import TraceSpan
from app.core.circuit_breaker import llm_breaker

# ✅ AGENT SYSTEM (Phase 2)
from app.ai.agents.langgraph.graph_builder import run_agent_graph


# --------------------------------------------------
# Helper: detect weak answers
# --------------------------------------------------

def is_bad_answer(answer):

    if not isinstance(answer, str):
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

    return any(p in text for p in bad_patterns)


class AIPipeline:

    memory_store = {}

    async def run(
        self,
        query: str,
        user_id: str,
        organization_id: Optional[str],
        conversation_id: Optional[str] = None
    ):

        trace_id = str(uuid.uuid4())
        start_time = time.time()
        conversation_id = conversation_id or str(uuid.uuid4())

        if conversation_id not in self.memory_store:
            self.memory_store[conversation_id] = ConversationMemory()

        memory = self.memory_store[conversation_id]
        conversation_context = memory.get_context()

        try:

            logger.info(f"TRACE_ID={trace_id} | Query received: {query}")

            # ---------------------------------
            # 0️⃣ Semantic Cache
            # ---------------------------------

            with TraceSpan(trace_id, "semantic_cache"):
                cached_answer = search_cache(query)

            if cached_answer:

                latency = time.time() - start_time

                enterprise_result = {
                    "trust_score": 0.9,
                    "decision": "CACHE_RESPONSE"
                }

                save_trace(AITrace(
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
                ))

                return {
                    "trace_id": trace_id,
                    "user_id": user_id,
                    "answer": cached_answer,
                    "confidence": "high",
                    "moderation_status": "ALLOW",
                    "enterprise": enterprise_result
                }

            # ---------------------------------
            # 1️⃣ AGENT SYSTEM (FIXED)
            # ---------------------------------

            augmented_query = f"""
Conversation history:
{conversation_context}

User question:
{query}
"""

            with TraceSpan(trace_id, "agent_execution"):
                agent_result = await run_agent_graph(augmented_query)
                
                # ✅ HANDLE BOTH dict and string
                if isinstance(agent_result, dict):
                    answer = agent_result.get("answer", "")
                    sources = agent_result.get("sources", [])
                    verification_result = agent_result.get("verification", {
                        "confidence": "medium",
                        "verdict": "UNKNOWN",
                        "checks": []
                    })
                else:
                    answer = str(agent_result)
                    sources = []
                    verification_result = {
                        "confidence": "medium",
                        "verdict": "UNKNOWN",
                        "checks": []
                    }

                # ✅ FINAL SAFETY
                if not isinstance(answer, str):
                    answer = str(answer)
                

            # ---------------------------------
            # 2️⃣ LLM FALLBACK (SAFE)
            # ---------------------------------

            if not answer or is_bad_answer(answer):

                logger.info(f"TRACE_ID={trace_id} | LLM fallback triggered")

                with TraceSpan(trace_id, "llm_fallback"):

                    llm = get_llm()

                    try:
                        response = await llm.ainvoke(query)
                    except Exception as e:
                        logger.error(f"LLM failure: {e}")
                        raise

                answer = getattr(response, "content", None)

                if not answer:
                    answer = str(response)

                answer = answer.strip()
            
                verification_result = {
                    "verdict": "UNVERIFIED",
                    "confidence": "medium",
                    "checks": []
                }

                track_cost(
                    model=llm.model_name,
                    prompt=query,
                    response=answer
                )

            # ---------------------------------
            # 3️⃣ PARALLEL AI CHECKS
            # ---------------------------------

            reasoning_input = {
                "query": query,
                "answer": answer,
                "verification": verification_result,
                "sources": sources
            }

            with TraceSpan(trace_id, "parallel_ai_checks"):

                hallucination_task = hallucination_guard(
                    query, answer, sources
                )

                moderation_task = asyncio.to_thread(
                    run_multiagent_moderation,
                    query,
                    answer
                )

                reasoning_task = run_decision_reasoning(reasoning_input)

                guard_ok, moderation_result, reasoning_result = await asyncio.gather(
                    hallucination_task,
                    moderation_task,
                    reasoning_task
                )

            moderation_flag = False

            if moderation_result.get("final_verdict") == "BLOCK":
                moderation_flag = True

                logger.warning(f"TRACE_ID={trace_id} | Moderation flagged content")

            final_answer = getattr(reasoning_result, "final_answer", None) or answer

            if moderation_flag:
                final_answer = (
                    "This topic may involve sensitive or evolving informartion.\n\n"
                    + final_answer
                )

            memory.add(query, final_answer[:1000])

            logger.info(f"Moderation result: {moderation_result}")

            if not isinstance(agent_result.get("verification"), dict):
                agent_result["verification"] = {
                    "verdict": "UNKNOWN",
                    "confidence": "low",
                    "checks": []
                }

            # ---------------------------------
            # 4️⃣ EVALUATION
            # ---------------------------------

            evaluation_result = evaluate_response(
                query=query,
                answer=final_answer,
                verification=verification_result,
                confidence=verification_result.get("confidence", "low"),
                sources=sources
            )

            # ---------------------------------
            # 5️⃣ ENTERPRISE TRUST
            # ---------------------------------

            enterprise_result = run_enterprise_pipeline(
                verification_result,
                evaluation_result,
                moderation_result
            )

            # ---------------------------------
            # 6️⃣ SAVE
            # ---------------------------------

            await InteractionRepository().save({
                "trace_id": trace_id,
                "conversation_id": conversation_id,
                "organization_id": organization_id,
                "user_id": user_id,
                "query": query,
                "response": final_answer,
                "enterprise": enterprise_result,
                "created_at": datetime.utcnow()
            })

            if enterprise_result.get("trust_score", 0) > 0.7 and len(final_answer) < 2000:
                add_to_cache(query, final_answer)

            latency = time.time() - start_time

            save_trace(AITrace(
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
            ))

            return {
                "trace_id": trace_id,
                "user_id": user_id,
                "answer": final_answer,
                "confidence": verification_result.get("confidence", "low"),
                "moderation_status": moderation_result.get("final_verdict", "ALLOW"),
                "enterprise": enterprise_result
            }

        except Exception as e:

            logger.exception(f"TRACE_ID={trace_id} | Pipeline failure: {e}")

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

    # --------------------------------------------------
    # STREAM (FIXED)
    # --------------------------------------------------

    async def stream(self, query: str, user_id: str, organization_id=None):

        trace_id = str(uuid.uuid4())

        try:
            result = await run_agent_system(query)

            if isinstance(result, dict):
                answer = result.get("answer", "")
            else:
                answer = str(result)

            for token in answer.split():
                yield token + " "
                await asyncio.sleep(0.02)

        except Exception as e:
            logger.exception(f"Streaming error: {e}")
            yield "Streaming failed."


ai_pipeline = AIPipeline()

# # 1️⃣ RAG → generates answer
# # 2️⃣ Verification → validates it
# # 3️⃣ Moderation → safety check
# # 4️⃣ Reasoning → governance decision
# # 5️⃣ Evaluation → scoring
# # 6️⃣ Enterprise → final trust scoring


# Flow of pipeline
# User Query
#    │
# Semantic Cache
#    │
# RAG Retrieval
#    │
# LLM Fallback (if needed)
#    │
# Parallel AI Checks
#    ├── Hallucination Guard
#    ├── Moderation
#    └── Reasoning Agent
#    │
# Evaluation
#    │
# Enterprise Trust
#    │
# Save Interaction
#    │
# Cache High Trust

