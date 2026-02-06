from app.rag.step1_ingestion.ingest import ingest_documents
from app.rag.step2_1_retrieval.retriever import get_retriever

print("Starting Step 1 test...")

# Ingest documents
vector_db = ingest_documents("data/internal_docs")
print("Ingestion completed.")

# Create retriever (TEMP: lower threshold)
retriever = get_retriever(k=5, score_threshold=0.3)

query = "How do we handle service outages?"
print(f"Query: {query}")

docs = retriever.invoke(query)

print(f"\nNumber of docs retrieved: {len(docs)}\n")

if not docs:
    print("❌ No documents retrieved")
else:
    print("✅ Documents retrieved:\n")

for i, d in enumerate(docs, 1):
    print(f"[Doc {i}]")
    print(d.page_content)
    print("------")
