import requests

from app.core.config import settings
from app.schemas.calendar_automation_schema import (
    CreateCalendarEventRequest,
)


class CalendarService:
    """
    Service responsible for sending calendar
    creation requests to the n8n workflow.
    """

    def create_event(
        self,
        request: CreateCalendarEventRequest,
    ) -> dict:

        payload = {
            "title": request.title,
            "start_time": request.start_time.isoformat(),
            "end_time": request.end_time.isoformat(),
            "description": request.description,
            "location": request.location,
        }

        response = requests.post(
            settings.N8N_CALENDAR_WEBHOOK_URL,
            json=payload,
            timeout=30,
        )

        # Raise exception for 4xx / 5xx responses
        response.raise_for_status()

        # ===============================================
        # Safely handle n8n response
        # ===============================================

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        response_text = response.text.strip()

        # Normal JSON response
        if (
            "application/json" in content_type
            and response_text
        ):
            try:
                data = response.json()

                if isinstance(data, dict):
                    return data

                return {
                    "success": True,
                    "message": (
                        "Calendar event created successfully."
                    ),
                    "data": data,
                }

            except ValueError:
                pass

        # n8n returned plain text
        if response_text:
            return {
                "success": True,
                "message": response_text,
            }

        # n8n returned 200 but empty response body
        return {
            "success": True,
            "message": (
                "Calendar event created successfully."
            ),
        }