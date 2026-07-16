from google import genai

from app.core.config import settings
from app.graph.prompts import RAG_PROMPT
from app.graph.state import GraphState
from app.services.retrieval_service import RetrievalService


retriever = RetrievalService()

client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)


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
        context=state["context"],
        question=state["question"],
    )

    response = client.models.generate_content(
        model=settings.CHAT_MODEL,
        contents=prompt,
    )

    state["answer"] = response.text

    return state