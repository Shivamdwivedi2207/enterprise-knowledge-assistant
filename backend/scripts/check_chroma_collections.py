import chromadb

from app.core.config import settings


client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_PATH
)

collections = client.list_collections()

print("=" * 60)
print("CHROMA DATABASE PATH")
print("=" * 60)
print(settings.CHROMA_DB_PATH)

print("\n" + "=" * 60)
print("AVAILABLE COLLECTIONS")
print("=" * 60)

if not collections:
    print("No collections found.")
else:
    for collection in collections:
        print(f"Name: {collection.name}")
        print(f"Count: {collection.count()}")
        print("-" * 60)