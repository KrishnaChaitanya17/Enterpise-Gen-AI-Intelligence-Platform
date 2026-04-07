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
from app.core.llm_provider import get_llm
from app.core.llm_executor import safe_llm_call
from app.ai.memory.conversation_memory import ConversationMemory
from app.ai.observability.tracer import TraceSpan

from app.ai.guardrails.input_guard import input_guard
from app.ai.guardrails.output_guard import output_guard
from app.ai.guardrails.prompt_injection import detect_prompt_injection
from app.ai.guardrails.pii_guard import detect_pii, mask_pii
from app.ai.moderation.policy.moderation_agent import moderate
from app.ai.moderation.langgraph.audit_logger import log_audit

# ✅ NEW (Phase 1 Fix)
from app.ai.router.model_router import route_model

# ✅ AGENT SYSTEM
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

        # ---------------------------------
        # 🔐 INPUT GUARDRAILS
        # ---------------------------------

        guard = input_guard(query)

        if guard.get("blocked"):
            return {
                "trace_id": trace_id,
                "answer": guard["reason"],
                "confidence": "low",
                "moderation_status": "BLOCKED"
            }

        # 🔥 Prompt Injection Detection
        if detect_prompt_injection(query):
            return {
                "trace_id": trace_id,
                "answer": "Prompt injection detected. Request blocked.",
                "confidence": "low",
                "moderation_status": "BLOCKED"
            }

        # 🔥 PII Detection (input)
        if detect_pii(query):
            query = mask_pii(query)

        # -----------------------------
        # Conversation Memory
        # -----------------------------
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
            # 1️⃣ AGENT SYSTEM
            # ---------------------------------

            augmented_query = f"""
Conversation history:
{conversation_context}

User question:
{query}
"""

            with TraceSpan(trace_id, "agent_execution"):
                agent_result = await run_agent_graph(augmented_query)

            answer = ""
            sources = []
            verification_result = {}

            if isinstance(agent_result, dict):
                answer = agent_result.get("answer", "")
                sources = agent_result.get("sources", [])
                verification_result = agent_result.get("verification", {})

            # ✅ Safety fallback for verification
            if not isinstance(verification_result, dict):
                verification_result = {
                    "verdict": "UNVERIFIED",
                    "confidence": 0.3,
                    "groundedness": 0.0,
                    "truth_score": 0.0,
                    "checks": []
                }

            # ---------------------------------
            # 2️⃣ LLM FALLBACK (WITH ROUTING)
            # ---------------------------------

            if not answer or is_bad_answer(answer):

                logger.info(f"TRACE_ID={trace_id} | LLM fallback triggered")

                models = route_model(query, organization_id)
                llms = get_llm(models)

                with TraceSpan(trace_id, "llm_fallback"):
                    response = await safe_llm_call(llms, query, trace_id)

                content = getattr(response, "content", str(response))

                track_cost(
                            model=models[0],
                            prompt=query,
                            response=content
                        )

                answer = content.strip()

                verification_result = {
                    "verdict": "UNVERIFIED",
                    "confidence": 0.3,
                    "groundedness": 0.0,
                    "truth_score": 0.0,
                    "checks": []
                }

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
                    query, answer, sources, trace_id
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

            moderation_flag = (
                moderation_result.get("final_verdict") == "BLOCK"
            )

            final_answer = getattr(reasoning_result, "final_answer", None) or answer

            # ---------------------------------
            # 🔐 POLICY ENGINE
            # ---------------------------------

            policy_result = moderate(query, final_answer)

            if policy_result.verdict == "BLOCK":
                final_answer = "Response blocked due to policy violation."

            # ---------------------------------
            # 🔐 OUTPUT GUARD
            # ---------------------------------

            final_answer = output_guard(final_answer)

            # ---------------------------------
            # 🔐 PII MASKING (OUTPUT)
            # ---------------------------------

            if detect_pii(final_answer):
                final_answer = mask_pii(final_answer)

            if moderation_flag:
                final_answer = (
                    "This topic may involve sensitive or evolving information.\n\n"
                    + final_answer
                )

            # ---------------------------------
            # Memory Update
            # ---------------------------------

            memory.add(query, final_answer[:1000])

            # ---------------------------------
            # 4️⃣ Evaluation
            # ---------------------------------

            evaluation_result = evaluate_response(
                query=query,
                answer=final_answer,
                verification=verification_result,
                confidence=verification_result.get("confidence", 0.3),
                sources=sources
            )

            # ---------------------------------
            # 5️⃣ Enterprise Trust
            # ---------------------------------

            enterprise_result = run_enterprise_pipeline(
                verification_result,
                evaluation_result,
                moderation_result
            )

            # ---------------------------------
            # 6️⃣ Save Interaction
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

            # ---------------------------------
            # Cache Store
            # ---------------------------------

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

            log_audit({
                "query": query,
                "answer": final_answer,
                "final_verdict": moderation_result.get("final_verdict"),
                "agent_decisions": moderation_result.get("agent_decisions"),
                "audit_trail": {
                    "policy": policy_result.__dict__,
                    "verification": verification_result
                }
            })

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
                "answer": "⚠️ Temporary AI issue. Retrying with fallback models failed. Please try again.",
                "confidence": "low",
                "moderation_status": "ALLOW",
                "enterprise": {
                    "trust_score": 0.0,
                    "decision": "SYSTEM_ERROR"
                }
            }

    # --------------------------------------------------
    # STREAM
    # --------------------------------------------------

    async def stream(self, query: str, user_id: str, organization_id=None):

        try:
            result = await run_agent_graph(query)

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

