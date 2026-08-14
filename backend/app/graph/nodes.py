import asyncio
from collections import defaultdict

from pydantic import ValidationError
from requests import RequestException

from app.core.logger import logger
from app.database.session import SessionLocal
from app.graph.state import GraphState
from app.repositories.chat_history_repository import (
    ChatHistoryRepository,
)
from app.schemas.calendar_automation_schema import (
    CreateCalendarEventRequest,
)
from app.services.calendar_service import CalendarService
from app.services.gemini_service import GeminiService
from app.services.retrieval_service import RetrievalService
from app.graph.prompts import RAG_PROMPT
from app.tools.gmail_tool import send_email

from app.tools.notion_tool import (
    create_notion_task,
    create_project_review_in_notion,
    save_chat_to_notion,
    save_insight_to_notion,
    save_meeting_notes_to_notion,
    save_summary_to_notion,
)

gemini = GeminiService()
repository = ChatHistoryRepository()
retriever = RetrievalService()
calendar_service = CalendarService()


# =========================================================
# History Node
# =========================================================

def history_node(
    state: GraphState,
) -> GraphState:
    """
    Load the authenticated user's recent chat history.
    """

    db = SessionLocal()

    try:
        chats = repository.get_history(
            db=db,
            owner_id=state["owner_id"],
            limit=10,
        )

        history: list[str] = []

        for chat in reversed(chats):
            history.append(
                f"User: {chat.question}"
            )
            history.append(
                f"Assistant: {chat.answer}"
            )

        state["history"] = "\n".join(history)

    except Exception:
        logger.exception(
            "Unable to load chat history."
        )

        state["history"] = ""

    finally:
        db.close()

    return state


# =========================================================
# Agent Router Node
# =========================================================

def route_node(
    state: GraphState,
) -> GraphState:
    """
    Classify the user's request and populate GraphState
    with the data required by the selected action.

    Supported routes:
    - RAG
    - Gmail
    - Google Calendar
    - Notion
    """

    try:
        # =================================================
        # Debug: verify recent conversation history
        # =================================================

        logger.info(
            "History passed to router:\n%s",
            state.get("history", ""),
        )

        # =================================================
        # Classify user intent
        # =================================================

        decision = gemini.classify_agent_action(
            question=state["question"],
            history=state.get(
                "history",
                "",
            ),
        )

        # =================================================
        # Selected route
        # =================================================

        state["route"] = decision.action

        # =================================================
        # Gmail
        # =================================================

        state["email_to"] = decision.to
        state["email_subject"] = decision.subject
        state["email_message"] = decision.message

        # =================================================
        # Calendar
        # =================================================

        state["calendar_title"] = (
            decision.calendar_title
        )

        state["calendar_start_time"] = (
            decision.calendar_start_time
        )

        state["calendar_end_time"] = (
            decision.calendar_end_time
        )

        state["calendar_description"] = (
            decision.calendar_description
        )

        state["calendar_location"] = (
            decision.calendar_location
        )

        # =================================================
        # Common Notion
        # =================================================

        state["notion_title"] = (
            decision.notion_title
        )

        state["notion_description"] = (
            decision.notion_description
        )

        # =================================================
        # Notion — Summary
        # =================================================

        state["notion_document_name"] = (
            decision.notion_document_name
        )

        state["notion_summary"] = (
            decision.notion_summary
        )

        state["notion_key_points"] = (
            decision.notion_key_points
        )

        state["notion_conclusion"] = (
            decision.notion_conclusion
        )

        # =================================================
        # Notion — Task
        # =================================================

        state["notion_task"] = (
            decision.notion_task
        )

        state["notion_status"] = (
            decision.notion_status
        )

        state["notion_priority"] = (
            decision.notion_priority
        )

        state["notion_due_date"] = (
            decision.notion_due_date
        )

        # =================================================
        # Notion — Meeting Notes
        # =================================================

        state["notion_meeting_title"] = (
            decision.notion_meeting_title
        )

        state["notion_meeting_date"] = (
            decision.notion_meeting_date
        )

        state["notion_participants"] = (
            decision.notion_participants
        )

        state["notion_agenda"] = (
            decision.notion_agenda
        )

        state["notion_discussion"] = (
            decision.notion_discussion
        )

        state["notion_decisions"] = (
            decision.notion_decisions
        )

        state["notion_action_items"] = (
            decision.notion_action_items
        )

        state["notion_next_meeting"] = (
            decision.notion_next_meeting
        )

        # =================================================
        # Notion — AI Insight
        # =================================================

        state["notion_category"] = (
            decision.notion_category
        )

        state["notion_importance"] = (
            decision.notion_importance
        )

        state["notion_insight"] = (
            decision.notion_insight
        )

        state["notion_source_documents"] = (
            decision.notion_source_documents
        )

        # =================================================
        # Notion — Project Review
        # =================================================

        state["notion_review_title"] = (
            decision.notion_review_title
        )

        state["notion_review_date"] = (
            decision.notion_review_date
        )

        state["notion_completed_features"] = (
            decision.notion_completed_features
        )

        state["notion_pending_features"] = (
            decision.notion_pending_features
        )

        state["notion_challenges"] = (
            decision.notion_challenges
        )

        state["notion_solutions"] = (
            decision.notion_solutions
        )

        state["notion_next_sprint"] = (
            decision.notion_next_sprint
        )

        state["notion_mentor_comments"] = (
            decision.notion_mentor_comments
        )

        # =================================================
        # Logging
        # =================================================

        logger.info(
            "Agent route selected: %s",
            decision.action,
        )

        logger.info(
            "Router extracted Notion summary length: %s",
            len(
                decision.notion_summary
                or ""
            ),
        )

        logger.info(
            "Router extracted Notion insight length: %s",
            len(
                decision.notion_insight
                or ""
            ),
        )

    except Exception:
        logger.exception(
            "Agent routing failed. "
            "Falling back to RAG."
        )

        # Safe fallback:
        # never execute an external automation if
        # intent classification fails.
        state["route"] = "rag"

    return state


# =========================================================
# Gmail Automation Node
# =========================================================

def email_action_node(
    state: GraphState,
) -> GraphState:
    """
    Send an email through n8n or request missing details.
    """

    state["sources"] = []
    state["context"] = ""

    if state.get("route") == "email_missing_details":
        state["answer"] = (
            "Please provide the recipient's email address "
            "before I send the email."
        )

        return state

    recipient = state.get(
        "email_to",
        "",
    ).strip()

    subject = state.get(
        "email_subject",
        "",
    ).strip()

    message = state.get(
        "email_message",
        "",
    ).strip()

    if not recipient:
        state["answer"] = (
            "Please provide the recipient's email address "
            "before I send the email."
        )

        return state

    if not subject:
        state["answer"] = (
            "Please provide the email subject "
            "before I send the email."
        )

        return state

    if not message:
        state["answer"] = (
            "Please provide the email message "
            "before I send the email."
        )

        return state

    try:
        result = send_email(
            to=recipient,
            subject=subject,
            message=message,
        )

        state["automation_result"] = result

        if result.get("success"):
            state["answer"] = (
                f"Email sent successfully to {recipient}."
            )
        else:
            state["answer"] = result.get(
                "message",
                "The email could not be sent.",
            )

    except Exception as error:
        logger.exception(
            "Gmail automation failed."
        )

        state["answer"] = (
            "The email could not be sent. "
            f"Reason: {str(error)}"
        )

    return state


# =========================================================
# Calendar Automation Node
# =========================================================

def calendar_action_node(
    state: GraphState,
) -> GraphState:
    """
    Create a Google Calendar event through n8n or ask
    the user for missing event information.
    """

    state["sources"] = []
    state["context"] = ""

    if state.get("route") == "calendar_missing_details":
        state["answer"] = (
            "Please provide the event title, start date "
            "and time, and end date and time."
        )

        return state

    title = state.get(
        "calendar_title",
        "",
    ).strip()

    start_time = state.get(
        "calendar_start_time",
        "",
    ).strip()

    end_time = state.get(
        "calendar_end_time",
        "",
    ).strip()

    description = state.get(
        "calendar_description",
        "",
    ).strip()

    location = state.get(
        "calendar_location",
        "",
    ).strip()

    missing_fields: list[str] = []

    if not title:
        missing_fields.append("event title")

    if not start_time:
        missing_fields.append("start date and time")

    if not end_time:
        missing_fields.append("end date and time")

    if missing_fields:
        state["answer"] = (
            "Please provide the following information: "
            + ", ".join(missing_fields)
            + "."
        )

        return state

    try:
        event_request = CreateCalendarEventRequest(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
        )

        result = calendar_service.create_event(
            request=event_request,
        )

        state["automation_result"] = result

        if result.get("success", True):
            state["answer"] = (
                f'Calendar event "{title}" was created '
                "successfully."
            )
        else:
            state["answer"] = result.get(
                "message",
                "The calendar event could not be created.",
            )

    except ValidationError as error:
        logger.warning(
            "Calendar event validation failed: %s",
            error,
        )

        state["answer"] = (
            "The calendar event details are invalid. "
            "Please provide a valid start time and an end "
            "time that occurs after the start time."
        )

    except RequestException as error:
        logger.exception(
            "n8n Calendar workflow failed."
        )

        state["answer"] = (
            "The calendar event could not be created "
            "because the Calendar automation service "
            "is unavailable."
        )

    except Exception as error:
        logger.exception(
            "Calendar automation failed."
        )

        state["answer"] = (
            "The calendar event could not be created. "
            f"Reason: {str(error)}"
        )

    return state


# =========================================================
# Retrieval Node
# =========================================================

def retrieve_node(
    state: GraphState,
) -> GraphState:
    """
    Retrieve, rerank and group relevant document chunks.
    """

    chunks = retriever.retrieve(
        query=state["question"],
        owner_id=state["owner_id"],
    )

    if not chunks:
        state["context"] = ""
        state["sources"] = []

        return state

    grouped_chunks = defaultdict(list)

    for chunk in chunks:
        grouped_chunks[
            chunk["filename"]
        ].append(chunk)

    context_parts: list[str] = []

    for filename, document_chunks in (
        grouped_chunks.items()
    ):
        context_parts.append(
            f"========== {filename} =========="
        )

        for chunk in document_chunks:
            context_parts.append(
                f"\nChunk {chunk['chunk_index']}\n"
            )

            context_parts.append(
                chunk["text"]
            )

            context_parts.append("\n")

    state["context"] = "\n".join(
        context_parts
    )

    state["sources"] = [
        {
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "document_id": chunk["document_id"],
        }
        for chunk in chunks
    ]

    return state

# =========================================================
# Notion Action Node
# =========================================================
def notion_action_node(
    state: GraphState,
) -> GraphState:
    """
    Execute the selected Notion automation.

    Supported actions:
    - save_chat
    - save_summary
    - create_task
    - meeting_notes
    - save_insight
    - project_review
    - notion_missing_details
    """

    route = state.get(
        "route",
        "",
    )

    state["sources"] = []
    state["context"] = ""

    # =====================================================
    # Missing Details
    # =====================================================

    if route == "notion_missing_details":
        state["answer"] = (
            "I need a little more information before "
            "I can complete that Notion action."
        )

        return state

    try:
        # =================================================
        # Save Chat
        # =================================================

        if route == "save_chat":
            title = (
                state.get("notion_title", "").strip()
                or "Saved Conversation"
            )

            question = state.get(
                "question",
                "",
            )

            history = state.get(
                "history",
                "",
            )

            if not history:
                state["answer"] = (
                    "There is no conversation history "
                    "available to save yet."
                )

                return state

            result = asyncio.run(
                save_chat_to_notion(
                    title=title,
                    question=question,
                    answer=history,
                    sources=[],
                )
            )

            state["automation_result"] = result

            state["answer"] = (
                f'Conversation "{title}" was saved '
                "to Notion successfully."
            )

            return state

        # =================================================
        # Save Summary
        # =================================================

        if route == "save_summary":
            title = (
                state.get("notion_title", "").strip()
                or "Document Summary"
            )

            document_name = state.get(
                "notion_document_name",
                "",
            ).strip()

            summary = state.get(
                "notion_summary",
                "",
            ).strip()

            key_points = state.get(
                "notion_key_points",
                [],
            )

            conclusion = state.get(
                "notion_conclusion",
                "",
            ).strip()

            if not summary:
                state["answer"] = (
                    "I need the document summary before "
                    "I can save it to Notion."
                )

                return state

            result = asyncio.run(
                save_summary_to_notion(
                    title=title,
                    document_name=document_name,
                    summary=summary,
                    key_points=key_points,
                    conclusion=conclusion,
                )
            )

            state["automation_result"] = result

            state["answer"] = (
                f'Summary "{title}" was saved '
                "to Notion successfully."
            )

            return state

        # =================================================
        # Create Task
        # =================================================

        if route == "create_task":
            task = state.get(
                "notion_task",
                "",
            ).strip()

            if not task:
                state["answer"] = (
                    "Please provide the task you want "
                    "me to create."
                )

                return state

            result = asyncio.run(
                create_notion_task(
                    task=task,
                    status=state.get(
                        "notion_status",
                        "Todo",
                    ),
                    priority=state.get(
                        "notion_priority",
                        "Medium",
                    ),
                    due_date=(
                        state.get(
                            "notion_due_date",
                            "",
                        )
                        or None
                    ),
                    description=state.get(
                        "notion_description",
                        "",
                    ),
                )
            )

            state["automation_result"] = result

            state["answer"] = (
                f'Task "{task}" was created '
                "in Notion successfully."
            )

            return state

        # =================================================
        # Meeting Notes
        # =================================================

        if route == "meeting_notes":
            meeting_title = (
                state.get(
                    "notion_meeting_title",
                    "",
                ).strip()
                or "Meeting Notes"
            )

            discussion = state.get(
                "notion_discussion",
                "",
            ).strip()

            agenda = state.get(
                "notion_agenda",
                [],
            )

            decisions = state.get(
                "notion_decisions",
                [],
            )

            action_items = state.get(
                "notion_action_items",
                [],
            )

            if (
                not discussion
                and not agenda
                and not decisions
                and not action_items
            ):
                state["answer"] = (
                    "I need some meeting notes, agenda, "
                    "decisions, or action items before "
                    "I can save them."
                )

                return state

            result = asyncio.run(
                save_meeting_notes_to_notion(
                    meeting_title=meeting_title,
                    meeting_date=state.get(
                        "notion_meeting_date",
                        "",
                    ),
                    participants=state.get(
                        "notion_participants",
                        [],
                    ),
                    agenda=agenda,
                    discussion=discussion,
                    decisions=decisions,
                    action_items=action_items,
                    next_meeting=state.get(
                        "notion_next_meeting",
                        "",
                    ),
                )
            )

            state["automation_result"] = result

            state["answer"] = (
                f'Meeting notes "{meeting_title}" '
                "were saved to Notion successfully."
            )

            return state

        # =================================================
        # Save AI Insight
        # =================================================

        if route == "save_insight":
            insight = state.get(
                "notion_insight",
                "",
            ).strip()

            if not insight:
                state["answer"] = (
                    "I need the insight content before "
                    "I can save it to Notion."
                )

                return state

            title = (
                state.get(
                    "notion_title",
                    "",
                ).strip()
                or "AI Insight"
            )

            result = asyncio.run(
                save_insight_to_notion(
                    insight_title=title,
                    category=(
                        state.get(
                            "notion_category",
                            "",
                        )
                        or "General"
                    ),
                    importance=state.get(
                        "notion_importance",
                        "Medium",
                    ),
                    insight=insight,
                    source_documents=state.get(
                        "notion_source_documents",
                        [],
                    ),
                )
            )

            state["automation_result"] = result

            state["answer"] = (
                f'Insight "{title}" was saved '
                "to Notion successfully."
            )

            return state

        # =================================================
        # Project Review
        # =================================================

        if route == "project_review":
            review_title = (
                state.get(
                    "notion_review_title",
                    "",
                ).strip()
                or "Project Review"
            )

            result = asyncio.run(
                create_project_review_in_notion(
                    review_title=review_title,
                    review_date=state.get(
                        "notion_review_date",
                        "",
                    ),
                    completed_features=state.get(
                        "notion_completed_features",
                        [],
                    ),
                    pending_features=state.get(
                        "notion_pending_features",
                        [],
                    ),
                    challenges=state.get(
                        "notion_challenges",
                        [],
                    ),
                    solutions=state.get(
                        "notion_solutions",
                        [],
                    ),
                    next_sprint=state.get(
                        "notion_next_sprint",
                        [],
                    ),
                    mentor_comments=state.get(
                        "notion_mentor_comments",
                        "",
                    ),
                )
            )

            state["automation_result"] = result

            state["answer"] = (
                f'Project review "{review_title}" '
                "was created in Notion successfully."
            )

            return state

        # =================================================
        # Unknown Notion route
        # =================================================

        state["answer"] = (
            "The requested Notion action "
            "is not supported."
        )

        return state

    except Exception as error:
        logger.exception(
            "Notion automation failed."
        )

        state["answer"] = (
            "The Notion action could not be completed. "
            "Please try again."
        )

        state["automation_result"] = {
            "success": False,
            "error": str(error),
        }

        return state
    

def planner_node(
    state: GraphState,
) -> GraphState:
    """
    Build an ordered execution plan for the user's request.

    If the request contains one action, the normal
    single-action graph can still be used.

    If it contains multiple actions, the plan is stored
    in GraphState for sequential execution.
    """

    try:
        plan = gemini.plan_agent_actions(
            question=state["question"],
            history=state.get(
                "history",
                "",
            ),
        )

        actions = [
            action.model_dump()
            for action in plan.actions
        ]

        state["plan_actions"] = actions
        state["plan_index"] = 0
        state["plan_results"] = []

        state["is_multi_action"] = (
            len(actions) > 1
        )

        logger.info(
            "Planner created %s action(s).",
            len(actions),
        )

        logger.info(
            "Multi-action request: %s",
            state["is_multi_action"],
        )

    except Exception:
        logger.exception(
            "Agent planner failed."
        )

        state["plan_actions"] = []
        state["plan_index"] = 0
        state["plan_results"] = []
        state["is_multi_action"] = False

    return state

def select_planning_mode(
    state: GraphState,
) -> str:
    """
    Decide whether to use the existing single-action router
    or the new multi-action executor.
    """

    if state.get(
        "is_multi_action",
        False,
    ):
        return "multi"

    return "single"




def multi_action_node(
    state: GraphState,
) -> GraphState:
    """
    Execute multiple planned actions sequentially.

    Features:
    - Executes actions in planner order.
    - Supports dependency-aware execution.
    - RAG output can feed Notion/Gmail actions.
    - One failed action does not automatically stop
      independent later actions.
    - Records success / failure / skipped status for
      every action.
    """

    actions = state.get(
        "plan_actions",
        [],
    )

    if not actions:
        state["answer"] = (
            "I couldn't determine the actions "
            "required for this request."
        )

        state["plan_results"] = []

        return state

    results: list[dict] = []
    messages: list[str] = []

    # =====================================================
    # Dependency state
    # =====================================================

    last_action_output = ""

    multi_action_sources: list[dict] = []

    rag_attempted = False
    rag_success = False

    # =====================================================
    # Helper functions
    # =====================================================

    def record_success(
        action_name: str,
        message: str,
        result=None,
    ) -> None:
        """
        Record a successful action.
        """

        results.append(
            {
                "action": action_name,
                "status": "success",
                "success": True,
                "message": message,
                "result": result,
            }
        )

        messages.append(
            f"✓ {message}"
        )

    def record_failure(
        action_name: str,
        message: str,
        error: str = "",
    ) -> None:
        """
        Record a failed action.
        """

        results.append(
            {
                "action": action_name,
                "status": "failed",
                "success": False,
                "message": message,
                "error": error,
            }
        )

        messages.append(
            f"✗ {message}"
        )

    def record_skipped(
        action_name: str,
        message: str,
    ) -> None:
        """
        Record an action that could not run because
        required input was unavailable.
        """

        results.append(
            {
                "action": action_name,
                "status": "skipped",
                "success": False,
                "message": message,
            }
        )

        messages.append(
            f"• {message}"
        )

    # =====================================================
    # Execute planned actions
    # =====================================================

    for index, action_data in enumerate(actions):

        action = action_data.get(
            "action",
            "rag",
        )

        state["plan_index"] = index

        logger.info(
            "Executing multi-action step %s/%s: %s",
            index + 1,
            len(actions),
            action,
        )

        try:
            # =================================================
            # RAG
            # =================================================

            if action == "rag":

                rag_attempted = True

                logger.info(
                    "Executing dependent RAG step."
                )

                chunks = retriever.retrieve(
                    query=state["question"],
                    owner_id=state["owner_id"],
                )

                if not chunks:
                    rag_success = False

                    last_action_output = (
                        "I couldn't find that information "
                        "in the uploaded documents."
                    )

                    record_failure(
                        action_name="rag",
                        message=(
                            "Relevant information could not "
                            "be found in the uploaded documents."
                        ),
                    )

                    continue

                # -----------------------------------------
                # Group chunks by filename
                # -----------------------------------------

                grouped_chunks = defaultdict(list)

                for chunk in chunks:
                    grouped_chunks[
                        chunk["filename"]
                    ].append(chunk)

                context_parts: list[str] = []

                for filename, document_chunks in (
                    grouped_chunks.items()
                ):
                    context_parts.append(
                        f"========== {filename} =========="
                    )

                    for chunk in document_chunks:
                        context_parts.append(
                            f"\nChunk "
                            f"{chunk['chunk_index']}\n"
                        )

                        context_parts.append(
                            chunk["text"]
                        )

                        context_parts.append(
                            "\n"
                        )

                context = "\n".join(
                    context_parts
                )

                # -----------------------------------------
                # Sources
                # -----------------------------------------

                multi_action_sources = [
                    {
                        "filename": chunk["filename"],
                        "chunk_index": (
                            chunk["chunk_index"]
                        ),
                        "document_id": (
                            chunk["document_id"]
                        ),
                    }
                    for chunk in chunks
                ]

                state["context"] = context
                state["sources"] = (
                    multi_action_sources
                )

                # -----------------------------------------
                # Generate RAG response
                # -----------------------------------------

                prompt = RAG_PROMPT.format(
                    history=state.get(
                        "history",
                        "",
                    ),
                    context=context,
                    question=state["question"],
                )

                last_action_output = (
                    gemini.generate(
                        prompt
                    )
                )

                not_found_message = (
                    "I couldn't find that information "
                    "in the uploaded documents."
                )

                if (
                    not last_action_output.strip()
                    or last_action_output.strip()
                    == not_found_message
                ):
                    rag_success = False

                    record_failure(
                        action_name="rag",
                        message=(
                            "The document retrieval step "
                            "did not produce a usable answer."
                        ),
                    )

                    continue

                rag_success = True

                record_success(
                    action_name="rag",
                    message=(
                        "Document information was retrieved "
                        "and processed successfully."
                    ),
                    result={
                        "answer": last_action_output,
                        "sources": (
                            multi_action_sources
                        ),
                    },
                )

                logger.info(
                    "Dependent RAG step completed. "
                    "Output length: %s",
                    len(last_action_output),
                )

                continue

            # =================================================
            # Gmail
            # =================================================

            if action == "send_email":

                recipient = action_data.get(
                    "to",
                    "",
                ).strip()

                subject = action_data.get(
                    "subject",
                    "",
                ).strip()

                message = action_data.get(
                    "message",
                    "",
                ).strip()

                # -----------------------------------------
                # Dependency-aware email body
                # -----------------------------------------

                if (
                    not message
                    and last_action_output
                    and rag_success
                ):
                    message = (
                        last_action_output
                    )

                if not recipient:
                    record_skipped(
                        action_name=action,
                        message=(
                            "Email was not sent because "
                            "the recipient address was missing."
                        ),
                    )

                    continue

                if not subject:
                    subject = (
                        "Enterprise AI Workspace Update"
                    )

                if not message:
                    if rag_attempted and not rag_success:
                        record_skipped(
                            action_name=action,
                            message=(
                                "Email was not sent because "
                                "the document-processing step "
                                "did not produce content."
                            ),
                        )
                    else:
                        record_skipped(
                            action_name=action,
                            message=(
                                "Email was not sent because "
                                "the message content was missing."
                            ),
                        )

                    continue

                result = send_email(
                    to=recipient,
                    subject=subject,
                    message=message,
                )

                if result.get(
                    "success",
                    False,
                ):
                    record_success(
                        action_name=action,
                        message=(
                            f"Email sent successfully "
                            f"to {recipient}."
                        ),
                        result=result,
                    )

                else:
                    record_failure(
                        action_name=action,
                        message=result.get(
                            "message",
                            (
                                "The email could "
                                "not be sent."
                            ),
                        ),
                    )

                continue

            # =================================================
            # Calendar
            # =================================================

            if action == "create_calendar_event":

                title = action_data.get(
                    "calendar_title",
                    "",
                ).strip()

                start_time = action_data.get(
                    "calendar_start_time",
                    "",
                ).strip()

                end_time = action_data.get(
                    "calendar_end_time",
                    "",
                ).strip()

                description = action_data.get(
                    "calendar_description",
                    "",
                ).strip()

                location = action_data.get(
                    "calendar_location",
                    "",
                ).strip()

                missing_fields: list[str] = []

                if not title:
                    missing_fields.append(
                        "event title"
                    )

                if not start_time:
                    missing_fields.append(
                        "start time"
                    )

                if not end_time:
                    missing_fields.append(
                        "end time"
                    )

                if missing_fields:
                    record_skipped(
                        action_name=action,
                        message=(
                            "Calendar event was not created "
                            "because these details were "
                            "missing: "
                            + ", ".join(
                                missing_fields
                            )
                            + "."
                        ),
                    )

                    continue

                event_request = (
                    CreateCalendarEventRequest(
                        title=title,
                        start_time=start_time,
                        end_time=end_time,
                        description=description,
                        location=location,
                    )
                )

                result = (
                    calendar_service.create_event(
                        request=event_request,
                    )
                )

                if result.get(
                    "success",
                    True,
                ):
                    record_success(
                        action_name=action,
                        message=(
                            f'Calendar event "{title}" '
                            "was created successfully."
                        ),
                        result=result,
                    )

                else:
                    record_failure(
                        action_name=action,
                        message=result.get(
                            "message",
                            (
                                "The calendar event "
                                "could not be created."
                            ),
                        ),
                    )

                continue

            # =================================================
            # Notion — Create Task
            # =================================================

            if action == "create_task":

                task = action_data.get(
                    "notion_task",
                    "",
                ).strip()

                if not task:
                    record_skipped(
                        action_name=action,
                        message=(
                            "Notion task was not created "
                            "because the task description "
                            "was missing."
                        ),
                    )

                    continue

                result = asyncio.run(
                    create_notion_task(
                        task=task,
                        status=action_data.get(
                            "notion_status",
                            "Todo",
                        ),
                        priority=action_data.get(
                            "notion_priority",
                            "Medium",
                        ),
                        due_date=(
                            action_data.get(
                                "notion_due_date",
                                "",
                            )
                            or None
                        ),
                        description=action_data.get(
                            "notion_description",
                            "",
                        ),
                    )
                )

                record_success(
                    action_name=action,
                    message=(
                        f'Task "{task}" was created '
                        "in Notion successfully."
                    ),
                    result=result,
                )

                continue

            # =================================================
            # Notion — Save Chat
            # =================================================

            if action == "save_chat":

                title = (
                    action_data.get(
                        "notion_title",
                        "",
                    ).strip()
                    or "Saved Conversation"
                )

                history = state.get(
                    "history",
                    "",
                ).strip()

                if not history:
                    record_skipped(
                        action_name=action,
                        message=(
                            "Conversation could not be saved "
                            "because no chat history "
                            "was available."
                        ),
                    )

                    continue

                result = asyncio.run(
                    save_chat_to_notion(
                        title=title,
                        question=state.get(
                            "question",
                            "",
                        ),
                        answer=history,
                        sources=[],
                    )
                )

                record_success(
                    action_name=action,
                    message=(
                        f'Conversation "{title}" was '
                        "saved to Notion successfully."
                    ),
                    result=result,
                )

                continue

            # =================================================
            # Notion — Save Summary
            # =================================================

            if action == "save_summary":

                summary = (
                    action_data.get(
                        "notion_summary",
                        "",
                    ).strip()
                    or (
                        last_action_output.strip()
                        if rag_success
                        else ""
                    )
                )

                if not summary:
                    if (
                        rag_attempted
                        and not rag_success
                    ):
                        record_skipped(
                            action_name=action,
                            message=(
                                "Summary was not saved "
                                "because the RAG step "
                                "did not produce usable content."
                            ),
                        )
                    else:
                        record_skipped(
                            action_name=action,
                            message=(
                                "Summary was not saved "
                                "because summary content "
                                "was missing."
                            ),
                        )

                    continue

                title = (
                    action_data.get(
                        "notion_title",
                        "",
                    ).strip()
                    or "Document Summary"
                )

                document_name = (
                    action_data.get(
                        "notion_document_name",
                        "",
                    ).strip()
                )

                if (
                    not document_name
                    and multi_action_sources
                ):
                    document_name = (
                        multi_action_sources[0].get(
                            "filename",
                            "",
                        )
                    )

                result = asyncio.run(
                    save_summary_to_notion(
                        title=title,
                        document_name=document_name,
                        summary=summary,
                        key_points=action_data.get(
                            "notion_key_points",
                            [],
                        ),
                        conclusion=action_data.get(
                            "notion_conclusion",
                            "",
                        ),
                    )
                )

                record_success(
                    action_name=action,
                    message=(
                        f'Summary "{title}" was saved '
                        "to Notion successfully."
                    ),
                    result=result,
                )

                # Keep actual generated content available
                # for later dependent steps such as email.
                last_action_output = summary

                continue

            # =================================================
            # Notion — Meeting Notes
            # =================================================

            if action == "meeting_notes":

                title = (
                    action_data.get(
                        "notion_meeting_title",
                        "",
                    ).strip()
                    or "Meeting Notes"
                )

                discussion = (
                    action_data.get(
                        "notion_discussion",
                        "",
                    ).strip()
                )

                if (
                    not discussion
                    and rag_success
                    and last_action_output
                ):
                    discussion = (
                        last_action_output
                    )

                agenda = action_data.get(
                    "notion_agenda",
                    [],
                )

                decisions = action_data.get(
                    "notion_decisions",
                    [],
                )

                action_items = action_data.get(
                    "notion_action_items",
                    [],
                )

                if (
                    not discussion
                    and not agenda
                    and not decisions
                    and not action_items
                ):
                    record_skipped(
                        action_name=action,
                        message=(
                            "Meeting notes were not saved "
                            "because no meeting content "
                            "was available."
                        ),
                    )

                    continue

                result = asyncio.run(
                    save_meeting_notes_to_notion(
                        meeting_title=title,
                        meeting_date=action_data.get(
                            "notion_meeting_date",
                            "",
                        ),
                        participants=action_data.get(
                            "notion_participants",
                            [],
                        ),
                        agenda=agenda,
                        discussion=discussion,
                        decisions=decisions,
                        action_items=action_items,
                        next_meeting=action_data.get(
                            "notion_next_meeting",
                            "",
                        ),
                    )
                )

                record_success(
                    action_name=action,
                    message=(
                        f'Meeting notes "{title}" '
                        "were saved to Notion successfully."
                    ),
                    result=result,
                )

                continue

            # =================================================
            # Notion — Save Insight
            # =================================================

            if action == "save_insight":

                insight = (
                    action_data.get(
                        "notion_insight",
                        "",
                    ).strip()
                    or (
                        last_action_output.strip()
                        if rag_success
                        else ""
                    )
                )

                if not insight:
                    record_skipped(
                        action_name=action,
                        message=(
                            "Insight was not saved because "
                            "valid insight content "
                            "was unavailable."
                        ),
                    )

                    continue

                title = (
                    action_data.get(
                        "notion_title",
                        "",
                    ).strip()
                    or "AI Insight"
                )

                source_documents = (
                    action_data.get(
                        "notion_source_documents",
                        [],
                    )
                )

                if (
                    not source_documents
                    and multi_action_sources
                ):
                    source_documents = list(
                        dict.fromkeys(
                            source.get(
                                "filename",
                                "",
                            )
                            for source
                            in multi_action_sources
                            if source.get(
                                "filename"
                            )
                        )
                    )

                result = asyncio.run(
                    save_insight_to_notion(
                        insight_title=title,
                        category=(
                            action_data.get(
                                "notion_category",
                                "",
                            )
                            or "General"
                        ),
                        importance=action_data.get(
                            "notion_importance",
                            "Medium",
                        ),
                        insight=insight,
                        source_documents=(
                            source_documents
                        ),
                    )
                )

                record_success(
                    action_name=action,
                    message=(
                        f'Insight "{title}" was saved '
                        "to Notion successfully."
                    ),
                    result=result,
                )

                last_action_output = insight

                continue

            # =================================================
            # Notion — Project Review
            # =================================================

            if action == "project_review":

                title = (
                    action_data.get(
                        "notion_review_title",
                        "",
                    ).strip()
                    or "Project Review"
                )

                result = asyncio.run(
                    create_project_review_in_notion(
                        review_title=title,
                        review_date=action_data.get(
                            "notion_review_date",
                            "",
                        ),
                        completed_features=(
                            action_data.get(
                                "notion_completed_features",
                                [],
                            )
                        ),
                        pending_features=(
                            action_data.get(
                                "notion_pending_features",
                                [],
                            )
                        ),
                        challenges=action_data.get(
                            "notion_challenges",
                            [],
                        ),
                        solutions=action_data.get(
                            "notion_solutions",
                            [],
                        ),
                        next_sprint=action_data.get(
                            "notion_next_sprint",
                            [],
                        ),
                        mentor_comments=action_data.get(
                            "notion_mentor_comments",
                            "",
                        ),
                    )
                )

                record_success(
                    action_name=action,
                    message=(
                        f'Project review "{title}" '
                        "was created in Notion successfully."
                    ),
                    result=result,
                )

                continue

            # =================================================
            # Missing Detail Routes
            # =================================================

            if action == "email_missing_details":
                record_skipped(
                    action_name=action,
                    message=(
                        "Email action requires a valid "
                        "recipient email address."
                    ),
                )

                continue

            if action == "calendar_missing_details":
                record_skipped(
                    action_name=action,
                    message=(
                        "Calendar action requires an event "
                        "title, start time, and end time."
                    ),
                )

                continue

            if action == "notion_missing_details":
                record_skipped(
                    action_name=action,
                    message=(
                        "The Notion action requires "
                        "additional information."
                    ),
                )

                continue

            # =================================================
            # Unknown Action
            # =================================================

            record_skipped(
                action_name=action,
                message=(
                    f'The action "{action}" '
                    "is not supported."
                ),
            )

        except ValidationError as error:
            logger.warning(
                "Multi-action validation failed "
                "for %s: %s",
                action,
                error,
            )

            record_failure(
                action_name=action,
                message=(
                    f'The "{action}" action could not '
                    "be completed because its data "
                    "was invalid."
                ),
                error=str(error),
            )

        except RequestException as error:
            logger.exception(
                "External automation request failed "
                "for action: %s",
                action,
            )

            record_failure(
                action_name=action,
                message=(
                    f'The "{action}" automation service '
                    "is currently unavailable."
                ),
                error=str(error),
            )

        except Exception as error:
            logger.exception(
                "Multi-action step failed: %s",
                action,
            )

            record_failure(
                action_name=action,
                message=(
                    f'The "{action}" action could "not be completed."'
                ),
                error=str(error),
            )

    # =====================================================
    # Final State
    # =====================================================

    state["plan_results"] = results

    success_count = sum(
        1
        for result in results
        if result.get("status") == "success"
    )

    failed_count = sum(
        1
        for result in results
        if result.get("status") == "failed"
    )

    skipped_count = sum(
        1
        for result in results
        if result.get("status") == "skipped"
    )

    logger.info(
        (
            "Multi-action execution finished. "
            "Success=%s Failed=%s Skipped=%s"
        ),
        success_count,
        failed_count,
        skipped_count,
    )

    # =====================================================
    # Build final response
    # =====================================================

    response_parts: list[str] = []

    # If RAG generated useful content, include it.
    if rag_success and last_action_output:
        response_parts.append(
            last_action_output
        )

    if messages:
        response_parts.append(
            "\n".join(messages)
        )

    if not response_parts:
        response_parts.append(
            "The requested actions were processed."
        )

    state["answer"] = "\n\n".join(
        response_parts
    )

    # IMPORTANT:
    # Do not reset state["sources"] here.
    # RAG sources must remain available.

    return state