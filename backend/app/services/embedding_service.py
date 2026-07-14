from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.GOOGLE_API_KEY,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple text chunks.
        """
        return self.embedding_model.embed_documents(texts)

    def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a user query.
        """
        return self.embedding_model.embed_query(query)