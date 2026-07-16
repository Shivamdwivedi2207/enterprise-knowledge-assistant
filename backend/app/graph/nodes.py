from google import genai

from app.core.config import settings
from app.graph.prompts import RAG_PROMPT
from app.graph.state import GraphState
from app.services.retrieval_service import RetrievalService
from app.database.session import SessionLocal
from app.repositories.chat_history_repository import ChatHistoryRepository


repository = ChatHistoryRepository()
retriever = RetrievalService()


client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)

def history_node(state: GraphState) -> GraphState:
    """
    Load recent chat history.
    """

    db = SessionLocal()

    try:
        chats = repository.get_history(
            db=db,
            owner_id=state["owner_id"],
            limit=10,
        )

        history = []

        for chat in reversed(chats):
            history.append(f"User: {chat.question}")
            history.append(f"Assistant: {chat.answer}")

        state["history"] = "\n".join(history)

    finally:
        db.close()

    return state


def retrieve_node(state: GraphState) -> GraphState:
    """
    Retrieve relevant chunks from ChromaDB.
    """

    chunks = retriever.retrieve(
        query=state["question"],
        owner_id=state["owner_id"],
    )

    state["context"] = "\n\n".join(chunks)

    return state


def generate_node(state: GraphState) -> GraphState:
    """
    Generate answer using Gemini.
    """

    prompt = RAG_PROMPT.format(
        history=state["history"],
        context=state["context"],
        question=state["question"],
    )

    response = client.models.generate_content(
        model=settings.CHAT_MODEL,
        contents=prompt,
    )

    state["answer"] = response.text

    return state