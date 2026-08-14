import logging
from threading import Lock
from typing import ClassVar

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


class RerankerService:
    """
    Production-safe cross-encoder reranking service.

    Features:
    - Lazy model loading
    - Shared model instance
    - Thread-safe initialization
    - Batched prediction
    - Graceful fallback
    """

    MODEL_NAME: ClassVar[str] = (
        "cross-encoder/ms-marco-MiniLM-L6-v2"
    )

    _model: ClassVar[CrossEncoder | None] = None
    _model_lock: ClassVar[Lock] = Lock()

    def __init__(
        self,
        batch_size: int = 16,
    ) -> None:
        self.batch_size = batch_size

    @classmethod
    def _get_model(cls) -> CrossEncoder:
        """
        Load the cross-encoder only on the first request.

        The same model object is reused by every
        RerankerService instance.
        """

        if cls._model is not None:
            return cls._model

        with cls._model_lock:
            if cls._model is None:
                logger.info(
                    "Loading reranker model: %s",
                    cls.MODEL_NAME,
                )

                cls._model = CrossEncoder(
                    cls.MODEL_NAME,
                )

                logger.info(
                    "Reranker model loaded successfully."
                )

        return cls._model

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """
        Rerank hybrid retrieval candidates according
        to their relevance to the user query.

        If model loading or prediction fails, the original
        fused ranking is returned as a fallback.
        """

        normalized_query = query.strip()

        if not normalized_query:
            return []

        if not candidates:
            return []

        if top_k <= 0:
            return []

        valid_candidates = [
            candidate
            for candidate in candidates
            if candidate.get(
                "text",
                "",
            ).strip()
        ]

        if not valid_candidates:
            return []

        query_document_pairs = [
            (
                normalized_query,
                candidate["text"],
            )
            for candidate in valid_candidates
        ]

        try:
            model = self._get_model()

            scores = model.predict(
                query_document_pairs,
                batch_size=self.batch_size,
                show_progress_bar=False,
            )

            reranked_results: list[dict] = []

            for candidate, score in zip(
                valid_candidates,
                scores,
            ):
                reranked_results.append(
                    {
                        **candidate,
                        "reranker_score": float(
                            score
                        ),
                        "reranking_applied": True,
                    }
                )

            reranked_results.sort(
                key=lambda item: item[
                    "reranker_score"
                ],
                reverse=True,
            )

            return reranked_results[:top_k]

        except Exception:
            logger.exception(
                "Cross-encoder reranking failed. "
                "Returning fused retrieval ranking."
            )

            return self._fallback_results(
                candidates=valid_candidates,
                top_k=top_k,
            )

    @staticmethod
    def _fallback_results(
        candidates: list[dict],
        top_k: int,
    ) -> list[dict]:
        """
        Preserve hybrid retrieval order when the
        cross-encoder model is unavailable.
        """

        fallback_results: list[dict] = []

        for candidate in candidates[:top_k]:
            fallback_results.append(
                {
                    **candidate,
                    "reranker_score": None,
                    "reranking_applied": False,
                }
            )

        return fallback_results