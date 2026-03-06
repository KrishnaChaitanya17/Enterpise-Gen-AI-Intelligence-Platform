from app.ai.step2_query.rag_chain import run_rag

query = "What happens during a service outage?"
# query = "What penalties apply if SLA is breached?" #Hallucination stage


response = run_rag(query)

print("\n🧠 Final Answer:\n")
print(response["answer"])

print("\n🔎 Confidence:", response.get("confidence"))

print("\n📚 Sources:")
for doc in response.get("sources", []):
    print("-", doc.metadata.get("source"))

print("\n🛡️ Verification Details:")
for check in response["verification"]["checks"]:
    print(
        f"• Claim: {check['claim']} | Supported: {check['supported']}"
    )
