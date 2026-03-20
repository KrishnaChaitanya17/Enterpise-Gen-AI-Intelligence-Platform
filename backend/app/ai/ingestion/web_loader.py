from langchain.document_loaders import WebBaseLoader

def load_website(url: str):
    loader = WebBaseLoader(url)
    docs = loader.load()

    for d in docs:
        d.metadata.update({
            "source": url,
            "type": "web" 
        })

    return docs