import re

from rank_bm25 import BM25Okapi

from app.services.vector_store_service import VectorStoreService


class BM25Service:
    def __init__(self):
        self.vector_store = VectorStoreService()

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """
        Normalize and tokenize text for keyword retrieval.
        """

        return re.findall(
            r"\b\w+\b",
            text.lower(),
        )

    def search(
        self,
        query: str,
        owner_id: str,
        top_k: int = 10,
    ) -> list[dict]:
        """
        Build a BM25 index from the user's ChromaDB chunks
        and return the highest-scoring keyword matches.
        """

        chunks = self.vector_store.get_owner_chunks(
            owner_id=owner_id,
        )

        if not chunks:
            return []

        tokenized_corpus = [
            self.tokenize(chunk["text"])
            for chunk in chunks
        ]

        bm25 = BM25Okapi(
            tokenized_corpus,
        )

        query_tokens = self.tokenize(query)

        if not query_tokens:
            return []

        scores = bm25.get_scores(
            query_tokens,
        )

        ranked_results: list[dict] = []

        for chunk, score in zip(
            chunks,
            scores,
        ):
            if score <= 0:
                continue

            ranked_results.append(
                {
                    **chunk,
                    "bm25_score": float(score),
                }
            )

        ranked_results.sort(
            key=lambda item: item["bm25_score"],
            reverse=True,
        )

        return ranked_results[:top_k]