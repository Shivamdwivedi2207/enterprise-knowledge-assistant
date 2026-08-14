import json
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.logger import logger
from app.graph.graph import graph
from app.graph.prompts import RAG_PROMPT
from app.repositories.chat_history_repository import (
    ChatHistoryRepository,
)
from app.services.gemini_service import GeminiService


# =========================================================
# Routes completed inside LangGraph itself
# =========================================================

AUTOMATION_ROUTES = {
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
}


class GraphService:

    def __init__(self) -> None:
        self.repository = ChatHistoryRepository()
        self.gemini = GeminiService()

    # =====================================================
    # Initial Graph State
    # =====================================================

    @staticmethod
    def _initial_state(
        question: str,
        owner_id: str,
    ) -> dict:
        """
        Build the initial LangGraph state.

        Every supported field is initialized so graph nodes
        can safely read/write values without KeyError issues.
        """

        return {
            # =================================================
            # Common
            # =================================================

            "question": question,
            "owner_id": owner_id,

            "history": "",
            "context": "",
            "answer": "",
            "sources": [],

            "route": "rag",

            "automation_result": {},

            # =================================================
            # Gmail
            # =================================================

            "email_to": "",
            "email_subject": "",
            "email_message": "",

            # =================================================
            # Calendar
            # =================================================

            "calendar_title": "",
            "calendar_start_time": "",
            "calendar_end_time": "",
            "calendar_description": "",
            "calendar_location": "",

            # =================================================
            # Common Notion
            # =================================================

            "notion_title": "",
            "notion_description": "",

            # =================================================
            # Notion — Save Summary
            # =================================================

            "notion_document_name": "",
            "notion_summary": "",
            "notion_key_points": [],
            "notion_conclusion": "",

            # =================================================
            # Notion — Task
            # =================================================

            "notion_task": "",
            "notion_status": "Todo",
            "notion_priority": "Medium",
            "notion_due_date": "",

            # =================================================
            # Notion — Meeting Notes
            # =================================================

            "notion_meeting_title": "",
            "notion_meeting_date": "",
            "notion_participants": [],
            "notion_agenda": [],
            "notion_discussion": "",
            "notion_decisions": [],
            "notion_action_items": [],
            "notion_next_meeting": "",

            # =================================================
            # Notion — AI Insight
            # =================================================

            "notion_category": "",
            "notion_importance": "Medium",
            "notion_insight": "",
            "notion_source_documents": [],

            # =================================================
            # Notion — Project Review
            # =================================================

            "notion_review_title": "",
            "notion_review_date": "",
            "notion_completed_features": [],
            "notion_pending_features": [],
            "notion_challenges": [],
            "notion_solutions": [],
            "notion_next_sprint": [],
            "notion_mentor_comments": "",

            # =================================================
            # Multi-action Planner
            # =================================================

            "plan_actions": [],
            "plan_index": 0,
            "plan_results": [],
            "is_multi_action": False,
        }

    # =====================================================
    # Non-streaming Chat
    # =====================================================

    def ask(
        self,
        db: Session,
        question: str,
        owner_id: str,
    ) -> dict:
        """
        Process a normal non-streaming chat request.

        Single automations and multi-action requests return
        the answer generated inside LangGraph.

        Only RAG requests call Gemini after graph execution.
        """

        state = self._initial_state(
            question=question,
            owner_id=owner_id,
        )

        result = graph.invoke(state)

        selected_route = result.get(
            "route",
            "rag",
        )

        is_multi_action = result.get(
            "is_multi_action",
            False,
        )

        # =================================================
        # Multi-Action Request
        # =================================================

        if is_multi_action:
            logger.info(
                "Using multi-action result directly."
            )

            answer = result.get(
                "answer",
                "The requested actions could not be completed.",
            )

            sources = []

        # =================================================
        # Single Automation
        # =================================================

        elif selected_route in AUTOMATION_ROUTES:
            answer = result.get(
                "answer",
                "The automation could not be completed.",
            )

            sources = []

        # =================================================
        # RAG
        # =================================================

        else:
            prompt = RAG_PROMPT.format(
                history=result.get(
                    "history",
                    "",
                ),
                context=result.get(
                    "context",
                    "",
                ),
                question=question,
            )

            answer = self.gemini.generate(
                prompt
            )

            sources = result.get(
                "sources",
                [],
            )

        # =================================================
        # Save Chat History
        # =================================================

        self.repository.create(
            db=db,
            owner_id=owner_id,
            question=question,
            answer=answer,
        )

        return {
            "answer": answer,
            "sources": sources,
        }

    # =====================================================
    # Streaming Chat
    # =====================================================

    def ask_stream(
        self,
        db: Session,
        question: str,
        owner_id: str,
    ) -> Generator[str, None, None]:
        """
        Process a streaming chat request.

        RAG responses stream token-by-token.

        Automation and multi-action responses are emitted
        as one SSE chunk because their execution has already
        completed inside LangGraph.
        """

        state = self._initial_state(
            question=question,
            owner_id=owner_id,
        )

        try:
            result = graph.invoke(state)

            selected_route = result.get(
                "route",
                "rag",
            )

            is_multi_action = result.get(
                "is_multi_action",
                False,
            )

            # =================================================
            # Multi-Action / Single Automation
            # =================================================

            if (
                is_multi_action
                or selected_route in AUTOMATION_ROUTES
            ):
                if is_multi_action:
                    logger.info(
                        "Streaming multi-action result directly."
                    )

                answer = result.get(
                    "answer",
                    (
                        "The requested action could not "
                        "be completed."
                    ),
                )

                chunk_data = json.dumps(
                    {
                        "content": answer,
                    }
                )

                yield (
                    "event: chunk\n"
                    f"data: {chunk_data}\n\n"
                )

                # =============================================
                # Save interaction
                # =============================================

                self.repository.create(
                    db=db,
                    owner_id=owner_id,
                    question=question,
                    answer=answer,
                )

                # Automations don't have document sources.
                yield (
                    "event: sources\n"
                    "data: []\n\n"
                )

                yield (
                    "event: done\n"
                    "data: {}\n\n"
                )

                return

            # =================================================
            # RAG
            # =================================================

            prompt = RAG_PROMPT.format(
                history=result.get(
                    "history",
                    "",
                ),
                context=result.get(
                    "context",
                    "",
                ),
                question=question,
            )

            full_answer = ""

            for chunk in self.gemini.generate_stream(
                prompt
            ):
                full_answer += chunk

                chunk_data = json.dumps(
                    {
                        "content": chunk,
                    }
                )

                yield (
                    "event: chunk\n"
                    f"data: {chunk_data}\n\n"
                )

            # =================================================
            # Save RAG Chat History
            # =================================================

            self.repository.create(
                db=db,
                owner_id=owner_id,
                question=question,
                answer=full_answer,
            )

            sources_data = json.dumps(
                result.get(
                    "sources",
                    [],
                )
            )

            yield (
                "event: sources\n"
                f"data: {sources_data}\n\n"
            )

            yield (
                "event: done\n"
                "data: {}\n\n"
            )

        except Exception:
            logger.exception(
                "LangGraph streaming request failed."
            )

            error_data = json.dumps(
                {
                    "message": (
                        "Unable to complete the request."
                    )
                }
            )

            yield (
                "event: error\n"
                f"data: {error_data}\n\n"
            )