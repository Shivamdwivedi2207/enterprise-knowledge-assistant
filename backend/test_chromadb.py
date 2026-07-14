from app.core.vector_store import VectorStore

db = VectorStore()

print(db.collection.count())