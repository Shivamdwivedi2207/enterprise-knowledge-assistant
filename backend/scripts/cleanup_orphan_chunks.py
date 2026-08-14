from app.database.models.document import Document
from app.database.session import SessionLocal
from app.services.vector_store_service import VectorStoreService


def main() -> None:
    db = SessionLocal()
    vector_store = VectorStoreService()

    try:
        active_document_ids = {
            str(document_id)
            for document_id in db.query(
                Document.id
            ).all()
        }

        result = vector_store.collection.get(
            include=[
                "metadatas",
            ]
        )

        ids = result.get("ids") or []
        metadatas = result.get("metadatas") or []

        orphan_chunk_ids: list[str] = []

        for chunk_id, metadata in zip(
            ids,
            metadatas,
        ):
            metadata = metadata or {}

            document_id = metadata.get(
                "document_id"
            )

            if not document_id:
                orphan_chunk_ids.append(
                    str(chunk_id)
                )
                continue

            if str(document_id) not in active_document_ids:
                orphan_chunk_ids.append(
                    str(chunk_id)
                )

        print(
            f"Orphan chunks found: "
            f"{len(orphan_chunk_ids)}"
        )

        if orphan_chunk_ids:
            vector_store.collection.delete(
                ids=orphan_chunk_ids
            )

            print(
                "Old orphaned chunks deleted successfully."
            )
        else:
            print(
                "No orphaned chunks were found."
            )

        print(
            "Remaining Chroma chunks:",
            vector_store.collection.count(),
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()