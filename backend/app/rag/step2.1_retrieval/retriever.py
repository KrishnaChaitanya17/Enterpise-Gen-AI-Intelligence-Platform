from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app.config.settings import OPENAI_API_KEY

VECTOR_PATH = "vectorstore/internal_docs"

def get_retriever(k=4, score_threshold=0.7):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=OPENAI_API_KEY
    )

    vector_db = FAISS.load_local(
        VECTOR_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vector_db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": k,
            "score_threshold": score_threshold
        }
    )

    return retriever
