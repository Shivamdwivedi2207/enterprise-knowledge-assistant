import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.database.models.user import User
from app.schemas.automation_schema import (
    AutomationRequest,
    AutomationResponse,
)
from app.services.n8n_service import N8NService


router = APIRouter(
    prefix="/automations",
    tags=["Automations"],
)


@router.post(
    "/trigger",
    response_model=AutomationResponse,
    status_code=status.HTTP_200_OK,
)
async def trigger_automation(
    request: AutomationRequest,
    current_user: User = Depends(get_current_user),
) -> AutomationResponse:
    """
    Trigger the configured n8n workflow for the
    authenticated user.
    """

    service = N8NService()

    payload = {
        "action": request.action,
        "message": request.message,
        "data": request.data,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
        },
    }

    try:
        workflow_response = await service.trigger_workflow(
            payload=payload,
        )

        return AutomationResponse(
            success=True,
            message="n8n workflow executed successfully.",
            workflow_response=workflow_response,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    except httpx.ConnectError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "FastAPI could not connect to n8n. "
                "Make sure n8n is running and the webhook is listening."
            ),
        ) from error

    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The n8n workflow took too long to respond.",
        ) from error

    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "n8n returned an unsuccessful response: "
                f"{error.response.status_code}"
            ),
        ) from error

    except httpx.RequestError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to communicate with n8n.",
        ) from error