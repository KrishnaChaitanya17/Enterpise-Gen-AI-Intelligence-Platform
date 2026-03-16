from app.ai.agents.router_agent import route_query
from app.ai.agents.retrieval_agent import retrieval_agent
from app.ai.agents.reasoning_agent import reasoning_agent
from app.ai.agents.tool_agent import tool_agent
from app.ai.agents.verifier_agent import verify_answer
from app.ai.agents.planner_agent import planner_agent

from app.ai.memory.conversation_memory import add_message


async def run_agent_system(query: str, session_id: str = "default"):
    
    #Router decides task type
    route = route_query(query)

    # Planning
    plan = await planner_agent(query)

    docs = None
    reasoning = None
    tool_result = None

    # Step 1 — Retrieval
    if route in ["retrieval", "reasoning"]:
        retrieval = await retrieval_agent(query)
        docs = retrieval["answer"]

    # Step 2 — Reasoning
    if route == "reasoning":

        reasoning_result = await reasoning_agent(
            f"Question: {query}\n\nDocuments:\n{docs}"
        )

        reasoning = reasoning_result["answer"]

    # Step 3 — Tool (math etc)
    if route == "tool":

        tool_result = await tool_agent(query)
        reasoning = tool_result["answer"]

    # Step 4 — Final Answer
    answer = reasoning if reasoning else docs

    # Step 5 — Verification
    verification = verify_answer(answer)

    # Store conversation
    add_message(session_id, {
        "query": query,
        "answer": answer
    })

    return {
        "answer": answer,
        "route": route,
        "plan": plan,
        "confidence": verification["confidence"]
    }