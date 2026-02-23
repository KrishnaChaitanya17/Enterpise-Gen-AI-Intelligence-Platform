# These metrics come directly from your pipeline, no ML magic.

def compute_groundedness(verification: dict) -> float:
    """
    groundedness = supported_claims / total_claims
    """
    checks = verification.get("checks", [])
    if not checks:
        return 0.0  
    
    supported_claims = sum(1 for c in checks if c.get("supported"))
    return supported_claims / len(checks)

def was_regenerated(confidence: str) -> bool:
    """
    Simple signal from LangGraph logic
    """
    return confidence in ["medium", "low"]
    
# Metrics you currently compute (correctly):

# Metric	                   Source	                        Why it matters
# Groundedness score	      Step 4 verification	      Measures hallucination risk
# Regenerated flag	          Step 5 confidence	          Measures answer stability
# Retrieval doc count	        Step 2	                   Measures context sufficiency

import json
from statistics import mean
from collections import Counter
from pathlib import Path

EVAL_LOG = Path(__file__).parent / "evaluation_results.jsonl"

def load_evaluation_logs():
    with open(EVAL_LOG, "r") as f:
        return [json.loads(line) for line in f]

def offline_analysis():
    logs = load_evaluation_logs()

    groundedness_scores = [l["groundedness_score"] for l in logs]
    verdicts = Counter(l["verdict"] for l in logs)
    regenerations = sum(1 for l in logs if l["regenerated"])

    print("\n📊 STEP 6.1 — OFFLINE ANALYSIS")
    print("=" * 40)
    print(f"Total Queries        : {len(logs)}")
    print(f"Avg Groundedness     : {mean(groundedness_scores):.2f}")
    print(f"Regeneration Rate    : {regenerations / len(logs):.2%}")
    print("Verdict Distribution:")
    for v, c in verdicts.items():
        print(f"  - {v}: {c}")

# Provide a system health snapshot (CLI-style dashboard).
def metrics_dashboard():
    logs = load_evaluation_logs()

    dashboard = {
        "total_queries": len(logs),
        "high_confidence": sum(1 for l in logs if l["confidence"] == "high"),
        "low_groundedness": sum(1 for l in logs if l["groundedness_score"] < 0.8),
        "retrieval_failures": sum(1 for l in logs if l["retrieval_doc_count"] == 0),
        "regenerated": sum(1 for l in logs if l["regenerated"]),
    }

    print("\n📈 STEP 6.2 — METRICS DASHBOARD")
    print("=" * 40)
    for k, v in dashboard.items():
        print(f"{k:25}: {v}")
        

# Turn evaluation signals into optimization decisions
# (No auto-changes yet — recommendations only)
def optimization_recommendations():
    logs = load_evaluation_logs()

    low_grounded = sum(1 for l in logs if l["groundedness_score"] < 0.8)
    zero_retrieval = sum(1 for l in logs if l["retrieval_doc_count"] == 0)
    regenerated = sum(1 for l in logs if l["regenerated"])

    print("\n🛠️ STEP 6.3 — OPTIMIZATION RECOMMENDATIONS")
    print("=" * 40)

    if low_grounded > 0:
        print("• Strengthen prompt grounding constraints")
        print("  → Enforce: 'Answer ONLY from retrieved context'")

    if zero_retrieval > 0:
        print("• Improve retrieval quality")
        print("  → Increase k, reduce chunk size, add metadata filters")

    if regenerated > 0:
        print("• High regeneration detected")
        print("  → Tighten verifier confidence threshold")

    if low_grounded == zero_retrieval == regenerated == 0:
        print("• System healthy — no optimization needed")

if __name__ == "__main__":
    offline_analysis()
    metrics_dashboard()
    optimization_recommendations()
