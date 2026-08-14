import time
from collections.abc import Callable
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logger import logger
from app.schemas.agent_schema import AgentDecision
from app.schemas.agent_plan_schema import AgentPlan

class GeminiService:

    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.GOOGLE_API_KEY
        )

    def _models(self) -> list[str]:
        models = [
            settings.GEMINI_PRIMARY_MODEL,
            settings.GEMINI_FALLBACK_MODEL,
        ]

        return list(dict.fromkeys(models))

    @staticmethod
    def _is_quota_error(
        error: Exception,
    ) -> bool:
        """
        Detect quota/rate-limit errors that should cause
        immediate fallback to the next Gemini model.
        """

        error_text = str(error).lower()

        return (
            "429" in error_text
            or "resource_exhausted" in error_text
            or "quota exceeded" in error_text
        )

    # =====================================================
    # Normal Generation
    # =====================================================

    def generate(
        self,
        prompt: str,
    ) -> str:
        last_exception: Exception | None = None

        for model in self._models():
            for attempt in range(3):
                try:
                    logger.info(
                        "Using Gemini model: %s",
                        model,
                    )

                    response = (
                        self.client.models.generate_content(
                            model=model,
                            contents=prompt,
                        )
                    )

                    return response.text or ""

                except Exception as error:
                    last_exception = error

                    logger.warning(
                        "%s failed (attempt %s/3): %s",
                        model,
                        attempt + 1,
                        error,
                    )

                    if self._is_quota_error(error):
                        logger.warning(
                            "Quota exhausted for %s. "
                            "Switching to fallback model.",
                            model,
                        )
                        break

                    time.sleep(
                        2 * (attempt + 1)
                    )

        if last_exception is None:
            raise RuntimeError(
                "Gemini generation failed."
            )

        logger.error(
            "All Gemini models failed: %s",
            last_exception,
        )

        raise last_exception

    # =====================================================
    # Streaming Generation
    # =====================================================

    def generate_stream(
        self,
        prompt: str,
    ):
        last_exception: Exception | None = None

        for model in self._models():
            for attempt in range(3):
                try:
                    logger.info(
                        "Streaming with Gemini model: %s",
                        model,
                    )

                    stream = (
                        self.client.models.generate_content_stream(
                            model=model,
                            contents=prompt,
                        )
                    )

                    for chunk in stream:
                        if chunk.text:
                            yield chunk.text

                    return

                except Exception as error:
                    last_exception = error

                    logger.warning(
                        "%s stream failed "
                        "(attempt %s/3): %s",
                        model,
                        attempt + 1,
                        error,
                    )

                    if self._is_quota_error(error):
                        logger.warning(
                            "Quota exhausted for %s. "
                            "Switching to fallback model.",
                            model,
                        )
                        break

                    time.sleep(
                        2 * (attempt + 1)
                    )

        if last_exception is None:
            raise RuntimeError(
                "Gemini streaming failed."
            )

        logger.error(
            "All Gemini streaming models failed: %s",
            last_exception,
        )

        raise last_exception

    # =====================================================
    # Tool Generation
    # =====================================================

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[Callable[..., Any]],
    ) -> str:
        if not tools:
            return self.generate(prompt)

        last_exception: Exception | None = None

        for model in self._models():
            for attempt in range(3):
                try:
                    logger.info(
                        "Using Gemini tools with model: %s",
                        model,
                    )

                    response = (
                        self.client.models.generate_content(
                            model=model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                tools=tools,
                                temperature=0.1,
                            ),
                        )
                    )

                    return (
                        response.text
                        or "The requested action was completed."
                    )

                except Exception as error:
                    last_exception = error

                    logger.warning(
                        "%s tool call failed "
                        "(attempt %s/3): %s",
                        model,
                        attempt + 1,
                        error,
                    )

                    if self._is_quota_error(error):
                        logger.warning(
                            "Quota exhausted for %s. "
                            "Switching to fallback model.",
                            model,
                        )
                        break

                    time.sleep(
                        2 * (attempt + 1)
                    )

        if last_exception is None:
            raise RuntimeError(
                "Gemini tool execution failed."
            )

        logger.error(
            "All Gemini tool calls failed: %s",
            last_exception,
        )

        raise last_exception

    # =====================================================
    # Agent Intent Router
    # =====================================================

    def classify_agent_action(
        self,
        question: str,
        history: str = "",
    ) -> AgentDecision:
        """
        Classify a user request and extract information
        required for RAG, Gmail, Calendar, or Notion.
        """

        current_datetime = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )

        current_datetime_text = (
            current_datetime.isoformat()
        )

        prompt = f"""
        You are the intelligent intent router for an
        Enterprise AI Workspace Assistant.

        Your responsibilities are:

        1. Understand the user's request.
        2. Choose exactly ONE action.
        3. Extract the information required for that action.
        4. Never invent important missing information.
        5. Return structured output matching AgentDecision.

        Current date and time:
        {current_datetime_text}

        User timezone:
        Asia/Kolkata


        ========================================================
        AVAILABLE ACTIONS
        ========================================================

        1. rag
        2. send_email
        3. email_missing_details
        4. create_calendar_event
        5. calendar_missing_details
        6. save_chat
        7. save_summary
        8. create_task
        9. meeting_notes
        10. save_insight
        11. project_review
        12. notion_missing_details


        ========================================================
        1. rag
        ========================================================

        Use "rag" when the user wants information or an answer
        but does NOT explicitly request an external automation.

        Examples:

        "What skills are mentioned in my resume?"

        "Explain the uploaded report."

        "Summarize the uploaded document."

        "What is the leave policy?"

        "Draft an email to my project guide."

        Use rag for:

        - Questions about uploaded documents
        - Resume questions
        - PDF/report/policy questions
        - Normal document summarization
        - General questions
        - Drafting content without sending it
        - Requests that do not require Gmail, Calendar, or Notion

        Important:

        "Summarize this PDF"
        → rag

        "Summarize this PDF and save it to Notion"
        → save_summary


        ========================================================
        2. send_email
        ========================================================

        Use "send_email" only when:

        - The user explicitly asks to SEND an email
        - A valid recipient email address is available

        Extract:

        to
        subject
        message

        Rules:

        - Never invent an email address.
        - If the subject is missing, create a short professional
        subject.
        - Build a complete email body from the user's instruction.

        Example:

        "Send an email to abc@gmail.com saying the project
        meeting has been postponed."


        ========================================================
        3. email_missing_details
        ========================================================

        Use "email_missing_details" when:

        - The user explicitly asks to send an email
        - But the recipient email address is missing

        Example:

        "Send an email saying tomorrow's meeting is cancelled."

        Never invent the recipient.


        ========================================================
        4. create_calendar_event
        ========================================================

        Use "create_calendar_event" when the user explicitly
        asks to:

        - schedule
        - create
        - book
        - arrange
        - add

        a meeting or calendar event.

        Required fields:

        calendar_title
        calendar_start_time
        calendar_end_time

        Optional:

        calendar_description
        calendar_location

        Rules:

        - Interpret relative dates using the current datetime.
        - Use Asia/Kolkata timezone.
        - Return ISO-8601 timestamps.
        - Include the +05:30 timezone offset.
        - Never schedule an event in the past.
        - End time must be later than start time.
        - Never invent missing start or end times.
        - Never invent a location.

        Example:

        "Schedule a project review tomorrow from 5 PM to 6 PM."


        ========================================================
        5. calendar_missing_details
        ========================================================

        Use this when the user wants to create a calendar event
        but one or more essential details cannot be determined.

        Essential details:

        - Event purpose/title
        - Start date and time
        - End date and time

        Examples:

        "Schedule a meeting."

        "Create an event tomorrow."

        "Book a discussion at 5 PM."


        ========================================================
        6. save_chat
        ========================================================

        Use "save_chat" when the user explicitly asks to save the
        current conversation or chat to Notion.

        Examples:

        "Save this chat to Notion."

        "Save this conversation."

        "Store our discussion in Notion."

        Extract:

        notion_title

        If the user does not provide a title, create a short,
        professional title describing the conversation.

        Do NOT invent the chat content.
        The application will obtain the actual conversation from
        chat history.


        ========================================================
        7. save_summary
        ========================================================

        Use "save_summary" when the user explicitly wants a
        document summary stored in Notion.

        Examples:

        "Save this summary to Notion."

        "Summarize the report and save it in Notion."

        "Store the document summary in our knowledge base."

        Extract when available:

        notion_title
        notion_document_name
        notion_summary
        notion_key_points
        notion_conclusion

        Rules:

        - Do not invent a document name.
        - If the user refers to "this summary", the application may
        obtain the summary from conversation history.
        - If important content is unavailable, use
        notion_missing_details rather than fabricating it.


        ========================================================
        8. create_task
        ========================================================

        Use "create_task" when the user explicitly asks to create
        a project task in Notion.

        Examples:

        "Create a task to deploy Docker."

        "Add a high priority task to test the backend by Friday."

        Extract:

        notion_task
        notion_status
        notion_priority
        notion_due_date
        notion_description

        Allowed status values:

        Todo
        In Progress
        Done

        Allowed priority values:

        Low
        Medium
        High

        Defaults:

        status → Todo

        priority → Medium

        Rules:

        - Convert relative due dates such as tomorrow or next Monday
        to YYYY-MM-DD.
        - Do not invent a task if the user has not described one.

        Example:

        "Create a high priority task to deploy Docker by
        August 20."


        ========================================================
        9. meeting_notes
        ========================================================

        Use "meeting_notes" when the user explicitly asks to save
        or create meeting notes in Notion.

        Examples:

        "Save today's meeting notes to Notion."

        "Create meeting notes for our project discussion."

        Extract when available:

        notion_meeting_title
        notion_meeting_date
        notion_participants
        notion_agenda
        notion_discussion
        notion_decisions
        notion_action_items
        notion_next_meeting

        Rules:

        - Do not invent participants.
        - Do not invent decisions.
        - Do not invent action items.
        - Optional missing fields should remain empty.
        - If there is no usable meeting context at all, use
        notion_missing_details.


        ========================================================
        10. save_insight
        ========================================================

        Use "save_insight" when the user explicitly asks to store
        an important AI-generated finding or insight in Notion.

        Examples:

        "Save this insight."

        "Store this security finding in Notion."

        "Save this analysis to the knowledge base."

        Extract:

        notion_title
        notion_category
        notion_importance
        notion_insight
        notion_source_documents

        Allowed importance values:

        Low
        Medium
        High

        Default:

        Medium

        Rules:

        - Never invent source documents.
        - If the user says "this insight", the application may use
        previous conversation content.
        - Do not classify ordinary information questions as
        save_insight unless the user explicitly asks to save it.


        ========================================================
        11. project_review
        ========================================================

        Use "project_review" when the user explicitly asks to
        create a:

        - Project review
        - Weekly review
        - Sprint review
        - Progress report

        in Notion.

        Extract when available:

        notion_review_title
        notion_review_date
        notion_completed_features
        notion_pending_features
        notion_challenges
        notion_solutions
        notion_next_sprint
        notion_mentor_comments

        Rules:

        - If review date is missing, use today's date.
        - Never invent mentor comments.
        - Missing optional lists should be empty.

        Examples:

        "Create this week's project review."

        "Save today's sprint review to Notion."


        ========================================================
        12. notion_missing_details
        ========================================================

        Use "notion_missing_details" when the user explicitly asks
        for a Notion action but essential information required to
        execute it safely is unavailable.

        Examples:

        "Create a task."

        without describing the task.

        "Save meeting notes."

        when there is no meeting context or notes available.

        "Save this summary."

        when no summary exists in the request or available context.

        Never fabricate missing business information.


        ========================================================
        ROUTING EXAMPLES
        ========================================================

        "What technologies are mentioned in my resume?"
        → rag

        "Summarize my project PDF."
        → rag

        "Save this document summary to Notion."
        → save_summary

        "Send an email to test@example.com saying the meeting
        is postponed."
        → send_email

        "Send an email saying the meeting is postponed."
        → email_missing_details

        "Schedule a project review tomorrow from 5 PM to 6 PM."
        → create_calendar_event

        "Schedule a meeting tomorrow."
        → calendar_missing_details

        "Save this conversation to Notion."
        → save_chat

        "Create a task to deploy Docker by August 20."
        → create_task

        "Save today's meeting notes."
        → meeting_notes

        "Save this security insight."
        → save_insight

        "Create this week's project review."
        → project_review


        ========================================================
        SAFETY AND EXECUTION RULES
        ========================================================

        - Automation must only be selected when explicitly requested.
        - Never invent email addresses.
        - Never invent missing calendar times.
        - Never invent document names.
        - Never invent meeting participants.
        - Never invent meeting decisions.
        - Never invent action items.
        - Never invent source documents.
        - Never invent mentor comments.
        - Normal document questions must stay on the RAG route.
        - Fill only fields relevant to the selected action.
        - Unused string fields should remain empty.
        - Unused list fields should remain empty lists.
        - Return structured output matching AgentDecision exactly.

        ========================================================
        RECENT CONVERSATION
        ========================================================

        {history}

        Use this conversation only when the user's current
        request refers to previous content using phrases such as:

        - this summary
        - that answer
        - this insight
        - our discussion
        - today's notes
        - the previous response

        Do not treat conversation history as permission to perform
        an automation unless the CURRENT user request explicitly
        asks for the action.

        Examples:

        Previous conversation:
        Assistant: RAG combines retrieval with generation.

        Current request:
        "Save this summary to Notion."

        → save_summary

        The summary should be extracted from the recent
        conversation when possible.


        Previous conversation:
        Assistant: Missing MFA increases unauthorized access risk.

        Current request:
        "Save that insight."

        → save_insight

        The insight should be extracted from the recent
        conversation.


        Previous conversation:
        Assistant: Here are three deployment steps...

        Current request:
        "What does Docker do?"

        → rag

        Do NOT save anything because the current request does
        not explicitly request an automation.

        ========================================================
        USER REQUEST
        ========================================================

        {question}
        """

        last_exception: Exception | None = None

        for model in self._models():
            for attempt in range(3):
                try:
                    logger.info(
                        "Classifying agent action with model: %s",
                        model,
                    )

                    response = (
                        self.client.models.generate_content(
                            model=model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type=(
                                    "application/json"
                                ),
                                response_schema=AgentDecision,
                                temperature=0,
                            ),
                        )
                    )

                    if response.parsed:
                        if isinstance(
                            response.parsed,
                            AgentDecision,
                        ):
                            decision = response.parsed

                        else:
                            decision = (
                                AgentDecision.model_validate(
                                    response.parsed
                                )
                            )

                    elif response.text:
                        decision = (
                            AgentDecision.model_validate_json(
                                response.text
                            )
                        )

                    else:
                        raise ValueError(
                            "Gemini returned an empty "
                            "routing response."
                        )

                    logger.info(
                        "Agent action selected: %s",
                        decision.action,
                    )

                    return decision

                except Exception as error:
                    last_exception = error

                    logger.warning(
                        "Agent classification failed with %s "
                        "(attempt %s/3): %s",
                        model,
                        attempt + 1,
                        error,
                    )

                    if self._is_quota_error(error):
                        logger.warning(
                            "Quota exhausted for %s. "
                            "Switching to fallback model.",
                            model,
                        )
                        break

                    time.sleep(
                        2 * (attempt + 1)
                    )

        logger.error(
            "All agent routing attempts failed: %s",
            last_exception,
        )

        # Safe fallback:
        # never execute an automation if routing fails.
        return AgentDecision(
            action="rag",
        )


    def plan_agent_actions(
        self,
        question: str,
        history: str = "",
    ) -> AgentPlan:
        """
        Build an ordered execution plan for requests
        that may require more than one action.
        """

        current_datetime = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )

        current_datetime_text = (
            current_datetime.isoformat()
        )

        prompt = f"""
    You are the multi-action planner for an
    Enterprise AI Workspace Assistant.

    Your job is to determine whether the user's request
    requires one action or multiple actions.

    Return an AgentPlan containing an ordered list of
    AgentDecision objects.

    Current date and time:
    {current_datetime_text}

    User timezone:
    Asia/Kolkata


    ========================================================
    AVAILABLE ACTIONS
    ========================================================

    rag

    send_email
    email_missing_details

    create_calendar_event
    calendar_missing_details

    save_chat
    save_summary
    create_task
    meeting_notes
    save_insight
    project_review
    notion_missing_details


    ========================================================
    GENERAL RULES
    ========================================================

    1. Preserve the order implied by the user's request.

    2. Use multiple actions only when the user explicitly
    requests multiple operations.

    3. Do NOT split a normal single request unnecessarily.

    4. Each action must contain the fields required for that
    action.

    5. Never invent:
    - email addresses
    - calendar times
    - document names
    - meeting participants
    - source documents
    - mentor comments

    6. Use recent conversation only when the current request
    refers to prior content such as:
    - this summary
    - that answer
    - this insight
    - our discussion

    7. A normal knowledge question should remain one "rag"
    action.

    8. If one action depends on another, place them in the
    correct execution order.


    ========================================================
    EXAMPLES
    ========================================================

    USER:
    Schedule a project review tomorrow from 5 PM to 6 PM.

    PLAN:

    1. create_calendar_event


    USER:
    Schedule a project review tomorrow from 5 PM to 6 PM
    and email test@example.com about it.

    PLAN:

    1. create_calendar_event
    2. send_email


    USER:
    Create a high priority task to deploy Docker and save
    this conversation to Notion.

    PLAN:

    1. create_task
    2. save_chat


    USER:
    Summarize the uploaded report and save the summary
    to Notion.

    PLAN:

    1. rag
    2. save_summary

    Important:
    The second action may depend on the output of the first.


    USER:
    Create a project review and email it to
    test@example.com.

    PLAN:

    1. project_review
    2. send_email


    ========================================================
    RECENT CONVERSATION
    ========================================================

    {history}


    ========================================================
    USER REQUEST
    ========================================================

    {question}


    ========================================================
    OUTPUT RULE
    ========================================================

    Return structured output matching AgentPlan exactly.

    The "actions" field must contain the actions in the order
    they should execute.

    The "reasoning_summary" must be short and must not expose
    private chain-of-thought. Use only a brief operational
    summary such as:

    "Calendar creation followed by email notification."
    """

        last_exception: Exception | None = None

        for model in self._models():
            for attempt in range(3):
                try:
                    logger.info(
                        "Planning agent actions with model: %s",
                        model,
                    )

                    response = (
                        self.client.models.generate_content(
                            model=model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type=(
                                    "application/json"
                                ),
                                response_schema=AgentPlan,
                                temperature=0,
                            ),
                        )
                    )

                    if response.parsed:
                        if isinstance(
                            response.parsed,
                            AgentPlan,
                        ):
                            plan = response.parsed

                        else:
                            plan = AgentPlan.model_validate(
                                response.parsed
                            )

                    elif response.text:
                        plan = (
                            AgentPlan.model_validate_json(
                                response.text
                            )
                        )

                    else:
                        raise ValueError(
                            "Gemini returned an empty "
                            "planning response."
                        )

                    logger.info(
                        "Agent plan created with %s action(s).",
                        len(plan.actions),
                    )

                    return plan

                except Exception as error:
                    last_exception = error

                    logger.warning(
                        "Agent planning failed with %s "
                        "(attempt %s/3): %s",
                        model,
                        attempt + 1,
                        error,
                    )

                    if self._is_quota_error(error):
                        logger.warning(
                            "Quota exhausted for %s. "
                            "Switching to fallback model.",
                            model,
                        )
                        break

                    time.sleep(
                        2 * (attempt + 1)
                    )

        logger.error(
            "All agent planning attempts failed: %s",
            last_exception,
        )

        # Safe fallback:
        # Never execute multiple automations if planning fails.
        return AgentPlan(
            actions=[
                AgentDecision(
                    action="rag",
                )
            ],
            reasoning_summary=(
                "Planner failed, so the request "
                "was routed safely to RAG."
            ),
        )