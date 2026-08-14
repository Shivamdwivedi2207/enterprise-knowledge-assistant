from app.schemas.calendar_automation_schema import (
    CreateCalendarEventRequest,
)
from app.services.calendar_service import CalendarService


calendar_service = CalendarService()


def create_calendar_event(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
):
    """
    Create a Google Calendar event through n8n.
    """

    request = CreateCalendarEventRequest(
        title=title,
        start_time=start_time,
        end_time=end_time,
        description=description,
        location=location,
    )

    return calendar_service.create_event(
        request=request,
    )