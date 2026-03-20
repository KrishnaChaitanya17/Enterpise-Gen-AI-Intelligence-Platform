# from app.ai.agents.router_agent import route_query
# from app.ai.agents.retrieval_agent import retrieval_agent
# from app.ai.agents.reasoning_agent import reasoning_agent
# from app.ai.agents.tool_agent import tool_agent
# from app.ai.agents.verifier_agent import verify_answer
# from app.ai.agents.planner_agent import planner_agent

# from app.ai.memory.conversation_memory import add_message
# from app.core.logging import logger


# async def run_agent_system(query: str, session_id: str = "default"):

#     try:
#         # -----------------------------
#         # 1️⃣ ROUTER
#         # -----------------------------
#         route = route_query(query)

#         # -----------------------------
#         # 2️⃣ PLANNER (SAFE)
#         # -----------------------------
#         try:
#             plan = await planner_agent(query)
#         except Exception as e:
#             logger.exception(f"PLANNER FAILED: {e}")
#             plan = "default_plan"

#         docs = []
#         answer = ""
#         reasoning = None

#         # -----------------------------
#         # 3️⃣ RETRIEVAL (SAFE)
#         # -----------------------------
#         if route in ["retrieval", "reasoning"]:
#             try:
#                 retrieval = await retrieval_agent(query)

#                 docs = retrieval.get("sources",[])
#                 answer = retrieval.get("answer", "")

#             except Exception as e:
#                 logger.exception(f"RETRIEVAL FAILED: {e}")
#                 docs = []
#                 answer = ""

#         # -----------------------------
#         # 4️⃣ REASONING (SAFE)
#         # -----------------------------
#         if route == "reasoning":
#             try:
#                 reasoning_result = await reasoning_agent(
#                     f"Question: {query}\n\nDocuments:\n{docs}"
#                 )
#                 reasoning = reasoning_result.get("answer", "")

#             except Exception as e:
#                 logger.exception(f"REASONING FAILED: {e}")
#                 reasoning = None

#         # -----------------------------
#         # 5️⃣ TOOL (SAFE)
#         # -----------------------------
#         if route == "tool":
#             try:
#                 tool_result = await tool_agent(query)
#                 reasoning = tool_result.get("answer", "")

#             except Exception as e:
#                 logger.exception(f"TOOL FAILED: {e}")
#                 reasoning = None

#         # -----------------------------
#         # 6️⃣ FINAL ANSWER
#         # -----------------------------
#         final_answer = reasoning if reasoning else answer

#         if not final_answer:
#             final_answer = "I couldn't find a reliable answer."

#         # -----------------------------
#         # 7️⃣ VERIFICATION (SAFE)
#         # -----------------------------
#         try:
#             verification = verify_answer(final_answer)
#         except Exception as e:
#             logger.exception(f"VERIFICATION FAILED: {e}")
#             verification = {}

#         verification_result = {
#             "verdict": verification.get("verdict", "UNKNOWN"),
#             "confidence": verification.get("confidence", "medium"),
#             "checks": verification.get("checks", [])
#         }

#         # -----------------------------
#         # 8️⃣ MEMORY (SAFE)
#         # -----------------------------
#         try:
#             add_message(session_id, {
#                 "query": query,
#                 "answer": final_answer
#             })
#         except Exception as e:
#             logger.warning(f"MEMORY FAILED: {e}")

#         # -----------------------------
#         # ✅ FINAL RESPONSE
#         # -----------------------------
#         return {
#             "answer": final_answer,
#             "sources": docs,
#             "route": route,
#             "plan": plan,
#             "verification": verification_result,
#             "confidence": verification_result["confidence"]
#         }

#     except Exception as e:
#         logger.exception(f"AGENT SYSTEM TOTAL FAILURE: {e}")

#         # 🚨 NEVER BREAK PIPELINE
#         return {
#             "answer": "Agent system failed. Using fallback.",
#             "sources": [],
#             "route": "fallback",
#             "plan": None,
#             "verification": {
#                 "verdict": "ERROR",
#                 "confidence": "low",
#                 "checks": []
#             },
#             "confidence": "low"
#         }


from app.ai.agents.langgraph.graph_builder import run_agent_graph
from app.ai.memory.conversation_memory import add_message
from app.core.logging import logger


async def run_agent_system(query: str, session_id: str = "default"):

    try:
        # -----------------------------
        # 1️⃣ LANGGRAPH EXECUTION
        # -----------------------------
        result = run_agent_graph(query)

        final_answer = result.get("final_answer", "")
        steps = result.get("steps", [])

        if not final_answer:
            final_answer = "I couldn't find a reliable answer."

        # -----------------------------
        # 2️⃣ VERIFICATION
        # -----------------------------
        verification_result = {
            "verdict": "AGENT_FLOW",
            "confidence": "medium",
            "checks": steps
        }

        # -----------------------------
        # 3️⃣ MEMORY
        # -----------------------------
        try:
            add_message(session_id, {
                "query": query,
                "answer": final_answer
            })
        except Exception as e:
            logger.warning(f"MEMORY FAILED: {e}")

        # -----------------------------
        # ✅ FINAL OUTPUT (IMPORTANT)
        # -----------------------------
        return {
            "answer": final_answer,
            "sources": [],
            "route": "langgraph",
            "plan": steps,
            "verification": verification_result,
            "confidence": "medium"
        }

    except Exception as e:
        logger.exception(f"AGENT SYSTEM FAILURE: {e}")

        return {
            "answer": "Agent system failed. Using fallback.",
            "sources": [],
            "route": "fallback",
            "plan": None,
            "verification": {
                "verdict": "ERROR",
                "confidence": "low",
                "checks": []
            },
            "confidence": "low"
        }