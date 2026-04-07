from datetime import datetime

cost_store = []

COST_LOG = cost_store


MODEL_PRICES = {
    "openai/gpt-4o-mini": 0.00015,
    "openai/gpt-4o": 0.002,
    "deepseek/deepseek-coder": 0.0008
}


def estimate_tokens(text):
    return len(text.split()) * 1.3


def track_cost(model, prompt, response):

    input_tokens = estimate_tokens(prompt)
    output_tokens = estimate_tokens(response)

    total_tokens = input_tokens + output_tokens

    price = MODEL_PRICES.get(model, 0.0001)

    cost = total_tokens * price / 1000

    record = {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cost": cost,
        "timestamp": datetime.utcnow()
    }

    cost_store.append(record)

    return record

def get_total_tokens():
    return sum(r["total_tokens"] for r in cost_store)