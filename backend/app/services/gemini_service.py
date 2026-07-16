import time

from google import genai

from app.core.config import settings


class GeminiService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GOOGLE_API_KEY
        )

    def generate(self, prompt: str):

        models = [
            settings.GEMINI_PRIMARY_MODEL,
            settings.GEMINI_FALLBACK_MODEL,
        ]

        last_exception = None

        for model in models:

            for attempt in range(3):

                try:

                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                    )

                    return response.text

                except Exception as e:

                    last_exception = e

                    print(
                        f"{model} failed "
                        f"(Attempt {attempt+1}/3)"
                    )

                    time.sleep(2 * (attempt + 1))

        raise last_exception