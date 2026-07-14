from app.services.retrieval_service import RetrievalService

retriever = RetrievalService()

chunks = retriever.retrieve(
    query="What is Artificial Intelligence?",
    owner_id="03da6bd1-2d92-42ea-9277-250e1db4ba09",
)

print()

print("=" * 80)

print("Retrieved Chunks")

print("=" * 80)

for i, chunk in enumerate(chunks, start=1):
    print(f"\nChunk {i}\n")
    print(chunk[:500])