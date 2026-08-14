import logging
from typing import Any

import httpx


logger = logging.getLogger(__name__)


class N8NService:
    """
    Shared HTTP client for communicating with n8n workflows.

    This service only handles HTTP communication.
    Business-specific logic belongs in GmailService,
    CalendarService, NotionService, etc.
    """

    def __init__(
        self,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.timeout_seconds = timeout_seconds

    async def trigger_workflow(
        self,
        webhook_url: str,
        payload: dict[str, Any],
    ) -> dict[str, Any] | list[Any] | str:
        """
        Send a JSON payload to an n8n webhook.
        """

        if not webhook_url:
            raise ValueError(
                "n8n webhook URL is not configured."
            )

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
            ) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                )

                response.raise_for_status()

                return self._parse_response(
                    response
                )

        except httpx.HTTPStatusError as error:
            logger.exception(
                "n8n workflow failed. "
                "Status code: %s",
                error.response.status_code,
            )

            raise

        except httpx.RequestError:
            logger.exception(
                "Could not communicate with n8n."
            )

            raise

    @staticmethod
    def _parse_response(
        response: httpx.Response,
    ) -> dict[str, Any] | list[Any] | str:
        """
        Parse n8n response safely.

        Supports:
        - valid JSON
        - plain text
        - empty 200 response
        """

        response_text = (
            response.text
            or ""
        ).strip()

        content_type = (
            response.headers.get(
                "content-type",
                "",
            )
            .lower()
        )

        # =============================================
        # Empty successful response
        # =============================================

        if not response_text:
            return {
                "success": True,
                "message": (
                    "n8n workflow executed successfully."
                ),
            }

        # =============================================
        # JSON response
        # =============================================

        if (
            "application/json"
            in content_type
        ):
            try:
                return response.json()

            except ValueError:
                logger.warning(
                    "n8n returned invalid JSON "
                    "despite JSON content type."
                )

        # =============================================
        # Try JSON anyway
        # =============================================

        try:
            return response.json()

        except ValueError:
            pass

        # =============================================
        # Plain text fallback
        # =============================================

        return response_text