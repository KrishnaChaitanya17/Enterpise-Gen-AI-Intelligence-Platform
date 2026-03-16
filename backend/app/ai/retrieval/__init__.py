class HybridMMRRetriever:

    def __init__(self, k=4):

        self.k = k

        from app.core.embeddings import get_embedding_model

        self.embeddings = get_embedding_model()