from typing import Any

import httpx

from app.core.config import settings


class GmailAutomationService:
    """
    Communicates with the n8n Gmail webhook.

    Provides:
    - async method for FastAPI routes
    - sync method for Gemini automatic function calling
    """

    def __init__(self) -> None:
        self.webhook_url = settings.N8N_GMAIL_WEBHOOK_URL
        self.timeout_seconds = 30.0

    async def send_email(
        self,
        to: str,
        subject: str,
        message: str,
    ) -> dict[str, Any]:
        """
        Asynchronous email method used by FastAPI routes.
        """

        payload = self._build_payload(
            to=to,
            subject=subject,
            message=message,
        )

        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
        ) as client:
            response = await client.post(
                self.webhook_url,
                json=payload,
            )

            response.raise_for_status()

            return self._parse_response(response)

    def send_email_sync(
        self,
        to: str,
        subject: str,
        message: str,
    ) -> dict[str, Any]:
        """
        Synchronous email method used by Gemini tools.

        Gemini automatic function calling expects a normal
        synchronous Python function in this implementation.
        """

        payload = self._build_payload(
            to=to,
            subject=subject,
            message=message,
        )

        with httpx.Client(
            timeout=self.timeout_seconds,
        ) as client:
            response = client.post(
                self.webhook_url,
                json=payload,
            )

            response.raise_for_status()

            return self._parse_response(response)

    @staticmethod
    def _build_payload(
        to: str,
        subject: str,
        message: str,
    ) -> dict[str, str]:
        return {
            "to": to.strip(),
            "subject": subject.strip(),
            "message": message.strip(),
            "sender": "Enterprise Knowledge Assistant",
        }

    @staticmethod
    def _parse_response(
        response: httpx.Response,
    ) -> dict[str, Any]:
        content_type = response.headers.get(
            "content-type",
            "",
        )

        if "application/json" in content_type:
            data = response.json()

            if isinstance(data, dict):
                return data

            return {
                "success": True,
                "data": data,
            }

        return {
            "success": True,
            "message": response.text,
        }