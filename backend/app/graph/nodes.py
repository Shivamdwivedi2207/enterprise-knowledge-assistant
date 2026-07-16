from app.services.gemini_service import GeminiService

from app.core.config import settings
from app.graph.prompts import RAG_PROMPT
from app.graph.state import GraphState
from app.services.retrieval_service import RetrievalService
from app.database.session import SessionLocal
from app.repositories.chat_history_repository import ChatHistoryRepository


# ==========================
# Initialize Services
# ==========================
gemini = GeminiService()
repository = ChatHistoryRepository()
retriever = RetrievalService()


# ==========================
# History Node
# ==========================

def history_node(state: GraphState) -> GraphState:
    """
    Load recent chat history from PostgreSQL.
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


# ==========================
# Retrieval Node
# ==========================

def retrieve_node(state: GraphState) -> GraphState:
    """
    Retrieve relevant chunks from ChromaDB.
    Store both context and citation metadata.
    """

    chunks = retriever.retrieve(
        query=state["question"],
        owner_id=state["owner_id"],
    )

    if not chunks:
        state["context"] = ""
        state["sources"] = []
        return state

    # Context sent to Gemini
    state["context"] = "\n\n".join(
        chunk["text"] for chunk in chunks
    )

    # Metadata for citations
    state["sources"] = [
        {
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "document_id": chunk["document_id"],
        }
        for chunk in chunks
    ]

    return state


# ==========================
# Generate Node
# ==========================

def generate_node(state: GraphState) -> GraphState:
    """
    Generate the final answer using Gemini.
    """

    prompt = RAG_PROMPT.format(
        history=state["history"],
        context=state["context"],
        question=state["question"],
    )

    try:
        state["answer"] = gemini.generate(prompt)

    except Exception as e:
        print(f"Gemini Error: {e}")

        state["answer"] = (
            "Sorry, I'm currently unable to generate a response. "
            "Please try again in a few moments."
        )

    return state