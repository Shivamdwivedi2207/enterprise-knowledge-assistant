from app.services.chat_service import ChatService

chat = ChatService()

answer = chat.ask(
    question="What is Artificial Intelligence?",
    owner_id="296c8dd6-adca-4c29-83cf-f6a5951b9e21",
)

print()

print("=" * 80)
print("ANSWER")
print("=" * 80)

print(answer)