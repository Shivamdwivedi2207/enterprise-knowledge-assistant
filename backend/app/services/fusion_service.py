class FusionService:
    """
    Combine semantic and keyword search rankings using
    Reciprocal Rank Fusion.
    """

    @staticmethod
    def reciprocal_rank_fusion(
        semantic_results: list[dict],
        keyword_results: list[dict],
        top_k: int = 10,
        rank_constant: int = 60,
    ) -> list[dict]:
        """
        Merge two ranked result lists.

        Formula:
            score = 1 / (rank_constant + rank)

        A chunk appearing in both result lists receives
        scores from both rankings.
        """

        fused_results: dict[str, dict] = {}

        result_lists = [
            ("semantic", semantic_results),
            ("keyword", keyword_results),
        ]

        for source_name, results in result_lists:
            for rank, result in enumerate(
                results,
                start=1,
            ):
                chunk_id = FusionService._get_chunk_id(
                    result
                )

                if not chunk_id:
                    continue

                if chunk_id not in fused_results:
                    fused_results[chunk_id] = {
                        **result,
                        "rrf_score": 0.0,
                        "retrieval_sources": [],
                    }

                fused_results[chunk_id]["rrf_score"] += (
                    1 / (rank_constant + rank)
                )

                fused_results[chunk_id][
                    "retrieval_sources"
                ].append(source_name)

                # Preserve useful scores from each retriever
                if "distance" in result:
                    fused_results[chunk_id][
                        "distance"
                    ] = result["distance"]

                if "bm25_score" in result:
                    fused_results[chunk_id][
                        "bm25_score"
                    ] = result["bm25_score"]

        ranked_results = sorted(
            fused_results.values(),
            key=lambda item: item["rrf_score"],
            reverse=True,
        )

        return ranked_results[:top_k]

    @staticmethod
    def _get_chunk_id(
        result: dict,
    ) -> str | None:
        """
        Return a stable ID for result deduplication.
        """

        if result.get("id"):
            return str(result["id"])

        document_id = result.get("document_id")
        chunk_index = result.get("chunk_index")

        if document_id is None or chunk_index is None:
            return None

        return f"{document_id}:{chunk_index}"