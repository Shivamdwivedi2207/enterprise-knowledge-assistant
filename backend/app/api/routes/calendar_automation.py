import requests
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.database.models.user import User
from app.schemas.calendar_automation_schema import (
    CreateCalendarEventRequest,
    CreateCalendarEventResponse,
)
from app.services.calendar_service import CalendarService


router = APIRouter(
    prefix="/automations/calendar",
    tags=["Calendar Automation"],
)


@router.post(
    "/create",
    response_model=CreateCalendarEventResponse,
    status_code=status.HTTP_200_OK,
)
def create_calendar_event(
    request: CreateCalendarEventRequest,
    current_user: User = Depends(get_current_user),
) -> CreateCalendarEventResponse:
    """
    Create a Google Calendar event through n8n.
    """

    service = CalendarService()

    try:
        result = service.create_event(
            request=request,
        )

        return CreateCalendarEventResponse(
            success=True,
            message=result.get(
                "message",
                "Calendar event created successfully.",
            ),
            event_id=result.get("event_id"),
            event_link=result.get("event_link"),
        )

    except requests.ConnectTimeout as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The calendar workflow connection timed out.",
        ) from error

    except requests.ReadTimeout as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The calendar workflow took too long to respond.",
        ) from error

    except requests.ConnectionError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Could not connect to n8n. "
                "Make sure n8n is running and the "
                "calendar workflow is active."
            ),
        ) from error

    except requests.HTTPError as error:
        response = error.response

        try:
            workflow_error = response.json()
        except ValueError:
            workflow_error = response.text

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "The n8n calendar workflow failed.",
                "n8n_status": response.status_code,
                "n8n_error": workflow_error,
            },
        ) from error

    except requests.RequestException as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to communicate with n8n.",
        ) from error