from typing import Any, Literal, TypedDict


class GraphState(TypedDict, total=False):
    # =====================================================
    # Common state
    # =====================================================

    question: str
    owner_id: str

    history: str
    context: str
    answer: str
    sources: list[dict[str, Any]]

    route: Literal[
        "rag",

        "send_email",
        "email_missing_details",

        "create_calendar_event",
        "calendar_missing_details",

        "save_chat",
        "save_summary",
        "create_task",
        "meeting_notes",
        "save_insight",
        "project_review",
        "notion_missing_details",
    ]

    automation_result: dict[str, Any]

    # =====================================================
    # Gmail
    # =====================================================

    email_to: str
    email_subject: str
    email_message: str

    # =====================================================
    # Calendar
    # =====================================================

    calendar_title: str
    calendar_start_time: str
    calendar_end_time: str
    calendar_description: str
    calendar_location: str

    # =====================================================
    # Common Notion
    # =====================================================

    notion_title: str
    notion_description: str

    # =====================================================
    # Save Summary
    # =====================================================

    notion_document_name: str
    notion_summary: str
    notion_key_points: list[str]
    notion_conclusion: str

    # =====================================================
    # Project Task
    # =====================================================

    notion_task: str

    notion_status: Literal[
        "Todo",
        "In Progress",
        "Done",
    ]

    notion_priority: Literal[
        "Low",
        "Medium",
        "High",
    ]

    notion_due_date: str

    # =====================================================
    # Meeting Notes
    # =====================================================

    notion_meeting_title: str
    notion_meeting_date: str
    notion_participants: list[str]
    notion_agenda: list[str]
    notion_discussion: str
    notion_decisions: list[str]
    notion_action_items: list[str]
    notion_next_meeting: str

    # =====================================================
    # AI Insight
    # =====================================================

    notion_category: str

    notion_importance: Literal[
        "Low",
        "Medium",
        "High",
    ]

    notion_insight: str
    notion_source_documents: list[str]

    # =====================================================
    # Project Review
    # =====================================================

    notion_review_title: str
    notion_review_date: str
    notion_completed_features: list[str]
    notion_pending_features: list[str]
    notion_challenges: list[str]
    notion_solutions: list[str]
    notion_next_sprint: list[str]
    notion_mentor_comments: str

    # =====================================================
    # Plan Actions
    # =====================================================
    plan_actions: list[dict[str, Any]]
    plan_index: int
    plan_results: list[dict[str, Any]]
    is_multi_action: bool