import httpx
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.core.security import get_current_user
from app.database.models.user import User
from app.schemas.notion_automation_schema import (
    CreateTaskRequest,
    MeetingNotesRequest,
    NotionAutomationResponse,
    ProjectReviewRequest,
    SaveChatRequest,
    SaveInsightRequest,
    SaveSummaryRequest,
)
from app.services.notion_service import NotionService


router = APIRouter(
    prefix="/automations/notion",
    tags=["Notion Automation"],
)

notion_service = NotionService()


def handle_n8n_error(
    error: Exception,
) -> None:
    if isinstance(error, ValueError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    if isinstance(error, httpx.ConnectError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Could not connect to n8n. "
                "Make sure n8n is running and the "
                "Notion workflow is active."
            ),
        ) from error

    if isinstance(error, httpx.TimeoutException):
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The Notion workflow timed out.",
        ) from error

    if isinstance(error, httpx.HTTPStatusError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The n8n Notion workflow failed with status "
                f"{error.response.status_code}."
            ),
        ) from error

    if isinstance(error, httpx.RequestError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to communicate with n8n.",
        ) from error

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unexpected Notion automation error.",
    ) from error


@router.post(
    "/save-chat",
    response_model=NotionAutomationResponse,
)
async def save_chat(
    request: SaveChatRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await notion_service.save_chat(
            title=request.title,
            question=request.question,
            answer=request.answer,
            sources=request.sources,
        )

        return NotionAutomationResponse(
            success=True,
            message=(
                result.get(
                    "message",
                    "Chat saved to Notion successfully.",
                )
                if isinstance(result, dict)
                else "Chat saved to Notion successfully."
            ),
        )

    except Exception as error:
        handle_n8n_error(error)


@router.post(
    "/save-summary",
    response_model=NotionAutomationResponse,
)
async def save_summary(
    request: SaveSummaryRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await notion_service.save_summary(
            title=request.title,
            document_name=request.document_name,
            summary=request.summary,
            key_points=request.key_points,
            conclusion=request.conclusion,
        )

        return NotionAutomationResponse(
            success=True,
            message=(
                result.get(
                    "message",
                    "Summary saved to Notion successfully.",
                )
                if isinstance(result, dict)
                else "Summary saved to Notion successfully."
            ),
        )

    except Exception as error:
        handle_n8n_error(error)


@router.post(
    "/create-task",
    response_model=NotionAutomationResponse,
)
async def create_task(
    request: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await notion_service.create_task(
            task=request.task,
            status=request.status,
            priority=request.priority,
            due_date=request.due_date,
            description=request.description,
        )

        return NotionAutomationResponse(
            success=True,
            message=(
                result.get(
                    "message",
                    "Task created in Notion successfully.",
                )
                if isinstance(result, dict)
                else "Task created in Notion successfully."
            ),
        )

    except Exception as error:
        handle_n8n_error(error)


@router.post(
    "/meeting-notes",
    response_model=NotionAutomationResponse,
)
async def meeting_notes(
    request: MeetingNotesRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await notion_service.save_meeting_notes(
            meeting_title=request.meeting_title,
            meeting_date=request.meeting_date,
            participants=request.participants,
            agenda=request.agenda,
            discussion=request.discussion,
            decisions=request.decisions,
            action_items=request.action_items,
            next_meeting=request.next_meeting,
        )

        return NotionAutomationResponse(
            success=True,
            message=(
                result.get(
                    "message",
                    "Meeting notes saved successfully.",
                )
                if isinstance(result, dict)
                else "Meeting notes saved successfully."
            ),
        )

    except Exception as error:
        handle_n8n_error(error)


@router.post(
    "/save-insight",
    response_model=NotionAutomationResponse,
)
async def save_insight(
    request: SaveInsightRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await notion_service.save_insight(
            insight_title=request.insight_title,
            category=request.category,
            importance=request.importance,
            insight=request.insight,
            source_documents=request.source_documents,
        )

        return NotionAutomationResponse(
            success=True,
            message=(
                result.get(
                    "message",
                    "AI insight saved successfully.",
                )
                if isinstance(result, dict)
                else "AI insight saved successfully."
            ),
        )

    except Exception as error:
        handle_n8n_error(error)


@router.post(
    "/project-review",
    response_model=NotionAutomationResponse,
)
async def project_review(
    request: ProjectReviewRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await notion_service.create_project_review(
            review_title=request.review_title,
            review_date=request.review_date,
            completed_features=request.completed_features,
            pending_features=request.pending_features,
            challenges=request.challenges,
            solutions=request.solutions,
            next_sprint=request.next_sprint,
            mentor_comments=request.mentor_comments,
        )

        return NotionAutomationResponse(
            success=True,
            message=(
                result.get(
                    "message",
                    "Project review created successfully.",
                )
                if isinstance(result, dict)
                else "Project review created successfully."
            ),
        )

    except Exception as error:
        handle_n8n_error(error)