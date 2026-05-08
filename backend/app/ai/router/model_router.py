from app.core.config import settings
from typing import List
import os

DEFAULT_MODEL = settings.DEFAULT_MODEL
FALLBACK_MODELS = settings.FALLBACK_MODELS.split(",")

def deduplicate(models: List[str]) -> List[str]:
    """Remove duplicates while preserving order"""
    seen = set()
    result = []

    for m in models:
        if m not in seen:
            seen.add(m)
            result.append(m)

    return result


def classify_query(query: str) -> str:
    """Lightweight intent classification"""
    q = query.lower()

    code_patterns = [
        "code", "python", "javascript", "react", "api", "algorithm", "sql"
    ]

    reasoning_patterns = [
        "why", "how", "explain", "compare", "difference", "analysis"
    ]

    math_patterns = [
        "calculate", "sum", "multiply", "divide", "equation", "math"
    ]

    if any(p in q for p in code_patterns):
        return "code"

    if any(p in q for p in reasoning_patterns):
        return "reasoning"

    if any(p in q for p in math_patterns):
        return "math"

    return "general"


def route_model(query: str, organization_id: str = None) -> List[str]:
    """
    Returns ordered list of models (best → fallback)
    """

    # 🔹 Org-based override (highest priority)
    if organization_id:
        org_model = os.getenv(f"ORG_{organization_id}_MODEL")
        if org_model:
            return deduplicate([org_model] + FALLBACK_MODELS)

    query_type = classify_query(query)

    # 🔥 Routing Strategy (cost-aware)

    if query_type == "code":
        models = [
            "deepseek/deepseek-chat",        # strong + cheaper
            "openai/gpt-4o-mini",            # reliable fallback
            "openai/gpt-4o"                  # expensive last
        ]

    elif query_type == "reasoning":
        models = [
            "deepseek/deepseek-chat",
            "openai/gpt-4o-mini",
            "openai/gpt-4o"
        ]

    elif query_type == "math":
        models = [
            "mistralai/mistral-7b-instruct",  # cheapest
            "deepseek/deepseek-chat",
            "openai/gpt-4o-mini"
        ]

    else:  # general
        models = [
            DEFAULT_MODEL,
            "mistralai/mistral-7b-instruct",
            "deepseek/deepseek-chat"
        ]

    # 🔹 Append global fallbacks safely
    models = models + FALLBACK_MODELS

    return deduplicate(models)