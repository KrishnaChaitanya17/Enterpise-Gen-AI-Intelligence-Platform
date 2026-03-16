import uuid
import time
import asyncio
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
from app.ai.observability.cost_tracker import track_cost
from app.core.logging import logger
from app.domain.repositories.interaction_repository import InteractionRepository
from app.core.llm_client import get_llm
from app.ai.memory.conversation_memory import ConversationMemory
from app.ai.observability.tracer import TraceSpan

from app.ai.agents.agent_graph import run_agent_system


# --------------------------------------------------
# Helper: detect weak answers
# --------------------------------------------------

def is_bad_answer(answer: str):

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
            # 1️⃣ RAG Retrieval
            # ---------------------------------

            augmented_query = f"""
Conversation history:
{conversation_context}

User question:
{query}
"""

            with TraceSpan(trace_id, "rag_retrieval"):
                rag_result = await run_agent_system(query)

            answer = rag_result.get("answer") or ""
            sources = rag_result.get("sources") or []
            verification_result = rag_result.get("verification") or {}

            # ---------------------------------
            # 2️⃣ LLM Fallback
            # ---------------------------------

            if not sources or is_bad_answer(answer):
                logger.info(f"TRACE_ID={trace_id} | Using LLM fallback")

                with TraceSpan(trace_id, "llm_fallback"):

                    llm = get_llm()

                    prompt = f"""
            You are a knowledgeable AI assistant.

            Provide a clear explanation.

            User question:
            {query}

            Answer clearly:
            """

                    response = await llm.ainvoke(prompt)

                answer = getattr(response, "content", str(response)).strip()

                verification_result = {
                    "verdict": "UNVERIFIED",
                    "confidence": "medium",
                    "checks": []
                }

                # Track LLM cost
                track_cost(
                    model=llm.model_name,
                    prompt=prompt,
                    response=answer
                )

            # ---------------------------------
            # 3️⃣ Parallel AI Checks
            # ---------------------------------

            reasoning_input = {
                "query": query,
                "answer": answer,
                "verification": verification_result,
                "sources": sources
            }

            with TraceSpan(trace_id, "parallel_ai_checks"):

                hallucination_task = hallucination_guard(
                    query,
                    answer,
                    sources
                )

                moderation_task = asyncio.to_thread(
                    run_multiagent_moderation,
                    query,
                    answer
                )

                reasoning_task = run_decision_reasoning(
                    reasoning_input
                )

                guard_ok, moderation_result, reasoning_result = await asyncio.gather(
                    hallucination_task,
                    moderation_task,
                    reasoning_task
                )

            if not guard_ok:
                logger.warning(
                    f"TRACE_ID={trace_id} | Hallucination risk detected"
                )

            if moderation_result.get("final_verdict") == "BLOCK":

                logger.warning(
                    f"TRACE_ID={trace_id} | Moderation BLOCK"
                )

                answer = "This response was blocked by the moderation system."

            final_answer = getattr(reasoning_result, "final_answer", None) or answer

            memory.add(query, final_answer)

            # ---------------------------------
            # 4️⃣ Evaluation
            # ---------------------------------

            with TraceSpan(trace_id, "evaluation"):

                evaluation_result = evaluate_response(
                    query=query,
                    answer=final_answer,
                    verification=verification_result,
                    confidence=verification_result.get("confidence", "low"),
                    sources=sources
                )

            # ---------------------------------
            # 5️⃣ Enterprise Trust
            # ---------------------------------

            with TraceSpan(trace_id, "enterprise_trust"):

                enterprise_result = run_enterprise_pipeline(
                    verification_result,
                    evaluation_result,
                    moderation_result
                )

            logger.info(
                f"TRACE_ID={trace_id} | Enterprise decision: {enterprise_result}"
            )

            # ---------------------------------
            # 6️⃣ Save Interaction
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
            # 7️⃣ Cache High Trust
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

    # --------------------------------------------------
    # Streaming Mode
    # --------------------------------------------------

    async def stream(self, query: str, user_id: str, organization_id=None):

        llm = get_llm(query=query, streaming=True)

        trace_id = str(uuid.uuid4())

        try:

            rag_result = await run_agent_system(query)

            sources = rag_result.get("sources") or []

            context = "\n".join(
                [s.page_content for s in sources]
            )

            prompt = f"""
Use the following context to answer.

Context:
{context}

Question:
{query}

Answer clearly:
"""

            async for chunk in llm.astream(prompt):

                token = getattr(chunk, "content", None)

                if token:
                    yield token

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

