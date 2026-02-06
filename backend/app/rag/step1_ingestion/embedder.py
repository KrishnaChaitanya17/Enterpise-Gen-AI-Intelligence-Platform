# from app.core.env import *
# import os
# from langchain_openai import OpenAIEmbeddings

# def get_embeddings():
#     return OpenAIEmbeddings(
#         model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
#     )

from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
