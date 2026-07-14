from google import genai

from app.core.config import settings
from app.services.retrieval_service import RetrievalService


class ChatService:
    def __init__(self):
        self.retriever = RetrievalService()
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    def ask(
        self,
        question: str,
        owner_id: str,
    ) -> str:

        chunks = self.retriever.retrieve(
            query=question,
            owner_id=owner_id,
        )

        if not chunks:
            return (
                "I couldn't find any relevant information "
                "in your uploaded documents."
            )

        context = "\n\n".join(chunks)

        prompt = f"""
You are an Enterprise Knowledge Assistant.

Answer ONLY from the context below.

If the answer is not present in the context, reply exactly:

"I couldn't find that information in the uploaded documents."

Context:
----------------
{context}
----------------

Question:
{question}
"""

        response = self.client.models.generate_content(
            model=settings.CHAT_MODEL,
            contents=prompt,
        )

        return response.text