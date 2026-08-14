from typing import Literal

from pydantic import BaseModel, Field


class AgentDecision(BaseModel):
    """
    Structured decision returned by Gemini.

    The router chooses one action and extracts
    all information required for that action.
    """

    # =====================================================
    # Action
    # =====================================================

    action: Literal[
        # RAG
        "rag",

        # Gmail
        "send_email",
        "email_missing_details",

        # Calendar
        "create_calendar_event",
        "calendar_missing_details",

        # Notion
        "save_chat",
        "save_summary",
        "create_task",
        "meeting_notes",
        "save_insight",
        "project_review",
        "notion_missing_details",
    ]

    # =====================================================
    # Gmail fields
    # =====================================================

    to: str = Field(
        default="",
        description="Recipient email address.",
    )

    subject: str = Field(
        default="",
        description="Email subject.",
    )

    message: str = Field(
        default="",
        description="Complete email body.",
    )

    # =====================================================
    # Calendar fields
    # =====================================================

    calendar_title: str = Field(
        default="",
        description="Title of the calendar event.",
    )

    calendar_start_time: str = Field(
        default="",
        description=(
            "Calendar event start datetime in "
            "ISO-8601 format."
        ),
    )

    calendar_end_time: str = Field(
        default="",
        description=(
            "Calendar event end datetime in "
            "ISO-8601 format."
        ),
    )

    calendar_description: str = Field(
        default="",
        description="Calendar event description.",
    )

    calendar_location: str = Field(
        default="",
        description="Calendar event location.",
    )

    # =====================================================
    # Common Notion fields
    # =====================================================

    notion_title: str = Field(
        default="",
        description=(
            "General Notion page title."
        ),
    )

    notion_description: str = Field(
        default="",
        description=(
            "General Notion description or task description."
        ),
    )

    # =====================================================
    # Save Summary fields
    # =====================================================

    notion_document_name: str = Field(
        default="",
        description=(
            "Original document name associated "
            "with the summary."
        ),
    )

    notion_summary: str = Field(
        default="",
        description="Document summary content.",
    )

    notion_key_points: list[str] = Field(
        default_factory=list,
        description="Important summary key points.",
    )

    notion_conclusion: str = Field(
        default="",
        description="Summary conclusion.",
    )

    # =====================================================
    # Project Task fields
    # =====================================================

    notion_task: str = Field(
        default="",
        description="Task title.",
    )

    notion_status: Literal[
        "Todo",
        "In Progress",
        "Done",
    ] = Field(
        default="Todo",
        description="Task status.",
    )

    notion_priority: Literal[
        "Low",
        "Medium",
        "High",
    ] = Field(
        default="Medium",
        description="Task priority.",
    )

    notion_due_date: str = Field(
        default="",
        description=(
            "Task due date, normally in YYYY-MM-DD format."
        ),
    )

    # =====================================================
    # Meeting Notes fields
    # =====================================================

    notion_meeting_title: str = Field(
        default="",
        description="Meeting title.",
    )

    notion_meeting_date: str = Field(
        default="",
        description="Meeting date.",
    )

    notion_participants: list[str] = Field(
        default_factory=list,
        description="Meeting participants.",
    )

    notion_agenda: list[str] = Field(
        default_factory=list,
        description="Meeting agenda items.",
    )

    notion_discussion: str = Field(
        default="",
        description="Meeting discussion summary.",
    )

    notion_decisions: list[str] = Field(
        default_factory=list,
        description="Decisions taken during the meeting.",
    )

    notion_action_items: list[str] = Field(
        default_factory=list,
        description="Action items from the meeting.",
    )

    notion_next_meeting: str = Field(
        default="",
        description="Next meeting information.",
    )

    # =====================================================
    # AI Insight fields
    # =====================================================

    notion_category: str = Field(
        default="",
        description="Insight category.",
    )

    notion_importance: Literal[
        "Low",
        "Medium",
        "High",
    ] = Field(
        default="Medium",
        description="Insight importance.",
    )

    notion_insight: str = Field(
        default="",
        description="AI-generated insight content.",
    )

    notion_source_documents: list[str] = Field(
        default_factory=list,
        description=(
            "Documents supporting the generated insight."
        ),
    )

    # =====================================================
    # Project Review fields
    # =====================================================

    notion_review_title: str = Field(
        default="",
        description="Project review title.",
    )

    notion_review_date: str = Field(
        default="",
        description="Project review date.",
    )

    notion_completed_features: list[str] = Field(
        default_factory=list,
        description="Completed project features.",
    )

    notion_pending_features: list[str] = Field(
        default_factory=list,
        description="Pending project features.",
    )

    notion_challenges: list[str] = Field(
        default_factory=list,
        description="Challenges faced during development.",
    )

    notion_solutions: list[str] = Field(
        default_factory=list,
        description="Solutions implemented for challenges.",
    )

    notion_next_sprint: list[str] = Field(
        default_factory=list,
        description="Goals for the next development sprint.",
    )

    notion_mentor_comments: str = Field(
        default="",
        description="Mentor or guide comments.",
    )