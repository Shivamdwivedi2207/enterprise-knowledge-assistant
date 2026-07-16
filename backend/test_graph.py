from app.graph.graph import graph

state = {
    "question": "What projects have candidate completed?",
    "owner_id": "296c8dd6-adca-4c29-83cf-f6a5951b9e21",
    "context": "",
    "answer": "",
}

result = graph.invoke(state)

print()

print("=" * 80)
print(result["answer"])
print("=" * 80)