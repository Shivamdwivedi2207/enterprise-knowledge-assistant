from app.services.vector_store_service import VectorStoreService

store = VectorStoreService()

results = store.collection.query(
    query_texts=["Artificial Intelligence"],
    where={"owner_id": "296c8dd6-adca-4c29-83cf-f6a5951b9e21"},
    n_results=5,
)

print(results)