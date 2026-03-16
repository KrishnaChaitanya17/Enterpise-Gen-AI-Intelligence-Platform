from app.ai.agents.router_agent import route_query
from app.ai.agents.retrieval_agent import retrieval_agent
from app.ai.agents.reasoning_agent import reasoning_agent
from app.ai.agents.tool_agent import tool_agent
from app.ai.agents.verifier_agent import verify_answer


async def run_agent_system(query: str):

    route = route_query(query)

    if route == "retrieval":
        result = await retrieval_agent(query)

    elif route == "reasoning":
        result = await reasoning_agent(query)

    elif route == "tool":
        result = await tool_agent(query)

    else:
        result = {"answer": "Unknown route"}

    verification = verify_answer(result["answer"])

    return {
        "answer": result["answer"],
        "route": route,
        "confidence": verification["confidence"]
    }