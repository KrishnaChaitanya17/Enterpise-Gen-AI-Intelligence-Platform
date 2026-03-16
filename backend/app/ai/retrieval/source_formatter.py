def format_sources(docs):

    sources = []

    for i, doc in enumerate(docs):
        source = {
            "id": i + 1,
            "text": doc.page_content[:200],
            "metadata": doc.metadata
        }
        sources.append(source)

    return sources