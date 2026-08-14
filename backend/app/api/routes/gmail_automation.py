import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.database.models.user import User
from app.schemas.gmail_automation_schema import (
    SendEmailRequest,
    SendEmailResponse,
)
from app.services.gmail_automation_service import (
    GmailAutomationService,
)


router = APIRouter(
    prefix="/automations/gmail",
    tags=["Gmail Automation"],
)


@router.post(
    "/send",
    response_model=SendEmailResponse,
    status_code=status.HTTP_200_OK,
)
async def send_email(
    request: SendEmailRequest,
    current_user: User = Depends(get_current_user),
) -> SendEmailResponse:
    service = GmailAutomationService()

    try:
        result = await service.send_email(
            to=str(request.to),
            subject=request.subject,
            message=request.message,
        )

        return SendEmailResponse(
            success=True,
            message=result.get(
                "message",
                "Email sent successfully.",
            ),
        )

    except httpx.ConnectError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Could not connect to n8n. "
                "Make sure n8n is running."
            ),
        ) from error

    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The Gmail workflow timed out.",
        ) from error

    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The n8n Gmail workflow failed with status "
                f"{error.response.status_code}."
            ),
        ) from error

    except httpx.RequestError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to communicate with n8n.",
        ) from error