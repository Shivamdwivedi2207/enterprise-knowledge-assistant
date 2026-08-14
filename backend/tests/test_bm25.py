from app.services.vector_store_service import VectorStoreService
from app.services.bm25_service import BM25Service


vector_store = VectorStoreService()

print("=" * 70)
print("CHROMA DATABASE DEBUG")
print("=" * 70)

collection_count = vector_store.collection.count()

print(f"Total chunks in collection: {collection_count}")

all_data = vector_store.collection.get(
    include=[
        "documents",
        "metadatas",
    ]
)

ids = all_data.get("ids") or []
documents = all_data.get("documents") or []
metadatas = all_data.get("metadatas") or []

if not ids:
    print("\nNo chunks found in this ChromaDB collection.")
    print("The database path may be incorrect.")
    raise SystemExit

print("\nStored chunks:")

for index, metadata in enumerate(metadatas[:10]):
    print("-" * 70)
    print(f"Chunk ID: {ids[index]}")
    print(f"Metadata: {metadata}")
    print(f"Text preview: {documents[index][:150]}")

owner_ids = {
    str(metadata.get("owner_id"))
    for metadata in metadatas
    if metadata.get("owner_id") is not None
}

print("\nDetected owner IDs:")

if owner_ids:
    for owner_id in owner_ids:
        print(owner_id)
else:
    print("No owner_id metadata found.")

if not owner_ids:
    raise SystemExit(
        "\nYour existing ChromaDB chunks do not contain owner_id metadata."
    )

test_owner_id = next(iter(owner_ids))

print(f"\nTesting BM25 with owner_id: {test_owner_id}")

service = BM25Service()

results = service.search(
    query="FastAPI LangGraph",
    owner_id=test_owner_id,
    top_k=5,
)

print(f"\nBM25 results found: {len(results)}")

for result in results:
    print("=" * 70)
    print("File:", result["filename"])
    print("Chunk:", result["chunk_index"])
    print("Score:", result["bm25_score"])
    print("Text:", result["text"][:300])