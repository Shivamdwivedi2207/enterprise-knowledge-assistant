from collections import defaultdict
from hashlib import sha256

from app.services.bm25_service import BM25Service
from app.services.embedding_service import EmbeddingService
from app.services.fusion_service import FusionService
from app.services.reranker_service import RerankerService
from app.services.vector_store_service import VectorStoreService


class RetrievalService:
    """
    Enterprise hybrid retrieval and reranking service.

    Pipeline
    --------
    1. Semantic vector search
    2. BM25 keyword search
    3. Reciprocal Rank Fusion
    4. Duplicate-content removal
    5. Cross-encoder reranking
    6. Multi-document balancing
    7. Final top-k selection
    """

    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()
        self.bm25_service = BM25Service()
        self.reranker_service = RerankerService()

    def retrieve(
        self,
        query: str,
        owner_id: str,
        top_k: int = 5,
        initial_fetch: int = 20,
        rerank_candidates: int = 12,
        max_chunks_per_document: int = 3,
        max_semantic_distance: float | None = 1.0,
    ) -> list[dict]:
        """
        Retrieve and rerank relevant document chunks.

        Args:
            query:
                User question.

            owner_id:
                Authenticated user's ID.

            top_k:
                Final number of chunks returned.

            initial_fetch:
                Number of candidates fetched independently
                from semantic search and BM25 search.

            rerank_candidates:
                Maximum number of fused candidates sent to
                the cross-encoder reranker.

            max_chunks_per_document:
                Maximum chunks selected from one document.

            max_semantic_distance:
                Optional ChromaDB distance threshold.
                Lower distance means better similarity.

        Returns:
            Final ranked and balanced document chunks.
        """

        normalized_query = query.strip()

        if not normalized_query:
            return []

        if not owner_id:
            return []

        if top_k <= 0:
            return []

        initial_fetch = max(
            initial_fetch,
            top_k,
        )

        rerank_candidates = max(
            rerank_candidates,
            top_k,
        )

        # ------------------------------------
        # Semantic retrieval
        # ------------------------------------

        semantic_results = self._semantic_search(
            query=normalized_query,
            owner_id=owner_id,
            initial_fetch=initial_fetch,
            max_semantic_distance=max_semantic_distance,
        )

        # ------------------------------------
        # Keyword retrieval
        # ------------------------------------

        keyword_results = self.bm25_service.search(
            query=normalized_query,
            owner_id=owner_id,
            top_k=initial_fetch,
        )

        # ------------------------------------
        # Reciprocal Rank Fusion
        # ------------------------------------

        fused_results = FusionService.reciprocal_rank_fusion(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            top_k=initial_fetch * 2,
        )

        if not fused_results:
            return []

        # ------------------------------------
        # Duplicate-content removal
        # ------------------------------------

        unique_results = self._remove_duplicate_content(
            results=fused_results,
        )

        if not unique_results:
            return []

        # ------------------------------------
        # Candidate selection for reranking
        # ------------------------------------

        candidates_for_reranking = unique_results[
            :rerank_candidates
        ]

        # ------------------------------------
        # Cross-encoder reranking
        # ------------------------------------

        reranked_results = self.reranker_service.rerank(
            query=normalized_query,
            candidates=candidates_for_reranking,
            top_k=rerank_candidates,
        )

        if not reranked_results:
            return []

        # ------------------------------------
        # Multi-document balancing
        # ------------------------------------

        balanced_results = self._balance_documents(
            results=reranked_results,
            max_chunks_per_document=max_chunks_per_document,
        )

        # ------------------------------------
        # Final ranking
        # ------------------------------------

        balanced_results.sort(
            key=self._final_sort_key,
            reverse=True,
        )

        return balanced_results[:top_k]

    def _semantic_search(
        self,
        query: str,
        owner_id: str,
        initial_fetch: int,
        max_semantic_distance: float | None,
    ) -> list[dict]:
        """
        Perform semantic similarity search restricted
        to the authenticated user's documents.
        """

        query_embedding = self.embedding_service.embed_query(
            query
        )

        if not query_embedding:
            return []

        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            owner_id=owner_id,
            n_results=initial_fetch,
        )

        ids = self._first_result_list(
            results.get("ids")
        )

        documents = self._first_result_list(
            results.get("documents")
        )

        metadatas = self._first_result_list(
            results.get("metadatas")
        )

        distances = self._first_result_list(
            results.get("distances")
        )

        semantic_results: list[dict] = []

        for chunk_id, document, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):
            metadata = metadata or {}

            if distance is None:
                continue

            numeric_distance = float(distance)

            if (
                max_semantic_distance is not None
                and numeric_distance > max_semantic_distance
            ):
                continue

            semantic_results.append(
                {
                    "id": str(chunk_id),
                    "text": document or "",
                    "filename": metadata.get(
                        "filename",
                        "Unknown",
                    ),
                    "chunk_index": metadata.get(
                        "chunk_index",
                        -1,
                    ),
                    "document_id": metadata.get(
                        "document_id",
                    ),
                    "owner_id": metadata.get(
                        "owner_id",
                    ),
                    "distance": numeric_distance,
                }
            )

        return semantic_results

    @staticmethod
    def _remove_duplicate_content(
        results: list[dict],
    ) -> list[dict]:
        """
        Remove chunks with identical normalized content.

        This prevents duplicate files or repeated chunks
        from appearing multiple times in the final context.
        """

        unique_results: list[dict] = []
        seen_hashes: set[str] = set()

        for result in results:
            raw_text = result.get(
                "text",
                "",
            )

            normalized_text = " ".join(
                raw_text.lower().split()
            )

            if not normalized_text:
                continue

            content_hash = sha256(
                normalized_text.encode(
                    "utf-8"
                )
            ).hexdigest()

            if content_hash in seen_hashes:
                continue

            seen_hashes.add(
                content_hash
            )

            unique_results.append(
                result
            )

        return unique_results

    @staticmethod
    def _balance_documents(
        results: list[dict],
        max_chunks_per_document: int,
    ) -> list[dict]:
        """
        Limit how many chunks a single document can
        contribute to the final retrieved context.
        """

        if max_chunks_per_document <= 0:
            return []

        grouped_results: dict[
            str,
            list[dict],
        ] = defaultdict(list)

        document_order: list[str] = []

        for result in results:
            document_id = result.get(
                "document_id"
            )

            if document_id is None:
                document_key = (
                    f"unknown:"
                    f"{result.get('filename', 'Unknown')}:"
                    f"{result.get('chunk_index', -1)}"
                )
            else:
                document_key = str(
                    document_id
                )

            if document_key not in grouped_results:
                document_order.append(
                    document_key
                )

            grouped_results[
                document_key
            ].append(
                result
            )

        selected_results: list[dict] = []

        for document_key in document_order:
            document_chunks = grouped_results[
                document_key
            ]

            document_chunks.sort(
                key=RetrievalService._final_sort_key,
                reverse=True,
            )

            selected_results.extend(
                document_chunks[
                    :max_chunks_per_document
                ]
            )

        return selected_results

    @staticmethod
    def _final_sort_key(
        result: dict,
    ) -> tuple:
        """
        Final ranking priority:

        1. Higher cross-encoder score
        2. Result found by both semantic and keyword search
        3. Higher Reciprocal Rank Fusion score
        4. Higher BM25 score
        5. Lower semantic distance
        """

        raw_reranker_score = result.get(
            "reranker_score"
        )

        reranker_score = (
            float(raw_reranker_score)
            if raw_reranker_score is not None
            else float("-inf")
        )

        retrieval_sources = result.get(
            "retrieval_sources",
            [],
        ) or []

        found_by_both = int(
            "semantic" in retrieval_sources
            and "keyword" in retrieval_sources
        )

        raw_rrf_score = result.get(
            "rrf_score"
        )

        rrf_score = (
            float(raw_rrf_score)
            if raw_rrf_score is not None
            else 0.0
        )

        raw_bm25_score = result.get(
            "bm25_score"
        )

        bm25_score = (
            float(raw_bm25_score)
            if raw_bm25_score is not None
            else 0.0
        )

        distance = result.get(
            "distance"
        )

        semantic_quality = (
            -float(distance)
            if distance is not None
            else float("-inf")
        )

        return (
            reranker_score,
            found_by_both,
            rrf_score,
            bm25_score,
            semantic_quality,
        )

    @staticmethod
    def _first_result_list(
        value: list | None,
    ) -> list:
        """
        Safely extract the first nested result list
        returned by ChromaDB query operations.
        """

        if not value:
            return []

        first_value = value[0]

        if first_value is None:
            return []

        return first_value