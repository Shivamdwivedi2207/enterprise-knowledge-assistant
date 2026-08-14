from pydantic import BaseModel, Field


class SaveChatRequest(BaseModel):
    title: str
    question: str
    answer: str
    sources: list[str] = []


class SaveSummaryRequest(BaseModel):
    title: str
    document_name: str
    summary: str
    key_points: list[str] = []
    conclusion: str = ""


class CreateTaskRequest(BaseModel):
    task: str
    status: str = "Todo"
    priority: str = "Medium"
    due_date: str | None = None
    description: str = ""


class MeetingNotesRequest(BaseModel):
    meeting_title: str
    meeting_date: str
    participants: list[str] = []
    agenda: list[str] = []
    discussion: str = ""
    decisions: list[str] = []
    action_items: list[str] = []
    next_meeting: str = ""


class SaveInsightRequest(BaseModel):
    insight_title: str
    category: str
    importance: str
    insight: str
    source_documents: list[str] = []


class ProjectReviewRequest(BaseModel):
    review_title: str
    review_date: str
    completed_features: list[str] = []
    pending_features: list[str] = []
    challenges: list[str] = []
    solutions: list[str] = []
    next_sprint: list[str] = []
    mentor_comments: str = ""


class NotionAutomationResponse(BaseModel):
    success: bool
    message: str