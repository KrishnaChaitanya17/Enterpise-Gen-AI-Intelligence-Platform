def format_sources(docs):
    sources = []
    for i, doc in enumerate(docs, start=1):
        sources.append(f"[{i}] {doc.metadata.get('source', 'unknown')}")
    return sources
