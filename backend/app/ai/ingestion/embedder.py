# from app.core.env import *
# import os
# from langchain_openai import OpenAIEmbeddings

# def get_embeddings():
#     return OpenAIEmbeddings(
#         model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
#     )

from app.core.embeddings import get_embedding_model

def load_embeddings():
    return get_embedding_model()