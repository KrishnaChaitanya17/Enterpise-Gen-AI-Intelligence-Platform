from pathlib import Path

POLICY_DIR = Path(__file__).parent / "policy_docs"

def load_policies():
    policies = []
    for file in POLICY_DIR.glob("*.txt"):
        policies.append({
            "name": file.name,
            "content": file.read_text(encoding="utf-8")
        })
    return policies
