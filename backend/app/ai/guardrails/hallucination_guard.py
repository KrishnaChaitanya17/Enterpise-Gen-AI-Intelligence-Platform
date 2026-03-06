import os
import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


async def hallucination_guard(query: str, answer: str, sources: list):

    prompt = f"""
You are a hallucination detection system.

User Question:
{query}

Model Answer:
{answer}

Sources:
{sources}

Determine if the answer is grounded in the sources.

Respond ONLY with:
SAFE
or
HALLUCINATION
"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

    result = response.json()["choices"][0]["message"]["content"]

    return "HALLUCINATION" not in result.upper()