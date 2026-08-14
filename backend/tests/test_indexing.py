from app.services.vector_store_service import VectorStoreService

vector_store = VectorStoreService()

print("Total Chunks:", vector_store.collection.count())