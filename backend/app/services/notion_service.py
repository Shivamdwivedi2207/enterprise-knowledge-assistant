from typing import Any

from app.core.config import settings
from app.services.n8n_service import N8NService


class NotionService:
    """
    Service for all Notion-related n8n automations.

    All actions are sent to one master Notion webhook.
    The 'action' field controls the Switch node in n8n.
    """

    NOTION_TEXT_LIMIT = 1900

    def __init__(self) -> None:
        self.n8n = N8NService()

        self.webhook_url = (
            settings.N8N_NOTION_WEBHOOK_URL
        )

    # =====================================================
    # Helpers
    # =====================================================

    @classmethod
    def _split_text(
        cls,
        text: str,
    ) -> list[str]:
        """
        Split long text into Notion-safe chunks.

        Notion rich_text content has a practical
        per-item limit of around 2000 characters.

        We use 1900 characters as a safety margin.
        """

        if not text:
            return []

        cleaned = text.strip()

        if not cleaned:
            return []

        if len(cleaned) <= cls.NOTION_TEXT_LIMIT:
            return [
                cleaned
            ]

        chunks: list[str] = []

        remaining = cleaned

        while remaining:
            if len(remaining) <= cls.NOTION_TEXT_LIMIT:
                chunks.append(
                    remaining
                )

                break

            split_at = cls.NOTION_TEXT_LIMIT

            # Prefer paragraph boundary
            paragraph_break = remaining.rfind(
                "\n\n",
                0,
                cls.NOTION_TEXT_LIMIT,
            )

            if paragraph_break > 0:
                split_at = paragraph_break

            else:
                # Prefer line boundary
                line_break = remaining.rfind(
                    "\n",
                    0,
                    cls.NOTION_TEXT_LIMIT,
                )

                if line_break > 0:
                    split_at = line_break

                else:
                    # Prefer sentence/space boundary
                    space_break = remaining.rfind(
                        " ",
                        0,
                        cls.NOTION_TEXT_LIMIT,
                    )

                    if space_break > 0:
                        split_at = space_break

            chunk = remaining[
                :split_at
            ].strip()

            if chunk:
                chunks.append(
                    chunk
                )

            remaining = remaining[
                split_at:
            ].strip()

        return chunks

    @classmethod
    def _split_list(
        cls,
        values: list[str],
    ) -> list[str]:
        """
        Split every long item in a list into
        Notion-safe text chunks.
        """

        result: list[str] = []

        for value in values:
            result.extend(
                cls._split_text(
                    value
                )
            )

        return result

    # =====================================================
    # Shared Sender
    # =====================================================

    async def _send(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any] | list[Any] | str:
        return await self.n8n.trigger_workflow(
            webhook_url=self.webhook_url,
            payload=payload,
        )

    # =====================================================
    # Save Chat
    # =====================================================

    async def save_chat(
        self,
        title: str,
        question: str,
        answer: str,
        sources: list[str],
    ):
        payload = {
            "action": "save_chat",

            "title": title,

            "question_chunks": self._split_text(
                question
            ),

            "answer_chunks": self._split_text(
                answer
            ),

            "sources": self._split_list(
                sources
            ),
        }

        return await self._send(
            payload
        )

    # =====================================================
    # Save Summary
    # =====================================================

    async def save_summary(
        self,
        title: str,
        document_name: str,
        summary: str,
        key_points: list[str],
        conclusion: str,
    ):
        payload = {
            "action": "save_summary",

            "title": title,

            "document_name": document_name,

            "summary_chunks": self._split_text(
                summary
            ),

            "key_points": self._split_list(
                key_points
            ),

            "conclusion_chunks": self._split_text(
                conclusion
            ),
        }

        return await self._send(
            payload
        )

    # =====================================================
    # Create Task
    # =====================================================

    async def create_task(
        self,
        task: str,
        status: str = "Todo",
        priority: str = "Medium",
        due_date: str | None = None,
        description: str = "",
    ):
        payload = {
            "action": "create_task",

            "task": task,

            "status": status,

            "priority": priority,

            "due_date": due_date,

            "description_chunks": self._split_text(
                description
            ),
        }

        return await self._send(
            payload
        )

    # =====================================================
    # Save Meeting Notes
    # =====================================================

    async def save_meeting_notes(
        self,
        meeting_title: str,
        meeting_date: str,
        participants: list[str],
        agenda: list[str],
        discussion: str,
        decisions: list[str],
        action_items: list[str],
        next_meeting: str = "",
    ):
        payload = {
            "action": "meeting_notes",

            "meeting_title": meeting_title,

            "meeting_date": meeting_date,

            "participants": self._split_list(
                participants
            ),

            "agenda": self._split_list(
                agenda
            ),

            "discussion_chunks": self._split_text(
                discussion
            ),

            "decisions": self._split_list(
                decisions
            ),

            "action_items": self._split_list(
                action_items
            ),

            "next_meeting_chunks": self._split_text(
                next_meeting
            ),
        }

        return await self._send(
            payload
        )

    # =====================================================
    # Save Insight
    # =====================================================

    async def save_insight(
        self,
        insight_title: str,
        category: str,
        importance: str,
        insight: str,
        source_documents: list[str],
    ):
        payload = {
            "action": "save_insight",

            "insight_title": insight_title,

            "category": category,

            "importance": importance,

            "insight_chunks": self._split_text(
                insight
            ),

            "source_documents": self._split_list(
                source_documents
            ),
        }

        return await self._send(
            payload
        )

    # =====================================================
    # Create Project Review
    # =====================================================

    async def create_project_review(
        self,
        review_title: str,
        review_date: str,
        completed_features: list[str],
        pending_features: list[str],
        challenges: list[str],
        solutions: list[str],
        next_sprint: list[str],
        mentor_comments: str = "",
    ):
        payload = {
            "action": "project_review",

            "review_title": review_title,

            "review_date": review_date,

            "completed_features": self._split_list(
                completed_features
            ),

            "pending_features": self._split_list(
                pending_features
            ),

            "challenges": self._split_list(
                challenges
            ),

            "solutions": self._split_list(
                solutions
            ),

            "next_sprint": self._split_list(
                next_sprint
            ),

            "mentor_comments_chunks": self._split_text(
                mentor_comments
            ),
        }

        return await self._send(
            payload
        )