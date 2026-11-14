"""Local sentence-transformers embedding provider."""
from typing import Protocol
from sentence_transformers import SentenceTransformer


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class MyEmbedder:
    """SentenceTransformer local embedding adapter."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)
        # Support both get_embedding_dimension and get_sentence_embedding_dimension
        if hasattr(self.model, "get_embedding_dimension"):
            self.dimensions: int = int(self.model.get_embedding_dimension())
        else:
            self.dimensions: int = int(self.model.get_sentence_embedding_dimension())

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return [vec.tolist() for vec in embeddings]

    def embed_query(self, question: str) -> list[float]:
        embedding = self.model.encode(
            question,
            normalize_embeddings=True
        )
        return embedding.tolist()
