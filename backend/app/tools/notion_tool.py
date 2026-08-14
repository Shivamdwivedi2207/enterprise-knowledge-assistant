from app.services.notion_service import NotionService


notion_service = NotionService()


async def save_chat_to_notion(
    title: str,
    question: str,
    answer: str,
    sources: list[str],
):
    return await notion_service.save_chat(
        title=title,
        question=question,
        answer=answer,
        sources=sources,
    )


async def save_summary_to_notion(
    title: str,
    document_name: str,
    summary: str,
    key_points: list[str],
    conclusion: str,
):
    return await notion_service.save_summary(
        title=title,
        document_name=document_name,
        summary=summary,
        key_points=key_points,
        conclusion=conclusion,
    )


async def create_notion_task(
    task: str,
    status: str = "Todo",
    priority: str = "Medium",
    due_date: str | None = None,
    description: str = "",
):
    return await notion_service.create_task(
        task=task,
        status=status,
        priority=priority,
        due_date=due_date,
        description=description,
    )


async def save_meeting_notes_to_notion(
    meeting_title: str,
    meeting_date: str,
    participants: list[str],
    agenda: list[str],
    discussion: str,
    decisions: list[str],
    action_items: list[str],
    next_meeting: str = "",
):
    return await notion_service.save_meeting_notes(
        meeting_title=meeting_title,
        meeting_date=meeting_date,
        participants=participants,
        agenda=agenda,
        discussion=discussion,
        decisions=decisions,
        action_items=action_items,
        next_meeting=next_meeting,
    )


async def save_insight_to_notion(
    insight_title: str,
    category: str,
    importance: str,
    insight: str,
    source_documents: list[str],
):
    return await notion_service.save_insight(
        insight_title=insight_title,
        category=category,
        importance=importance,
        insight=insight,
        source_documents=source_documents,
    )


async def create_project_review_in_notion(
    review_title: str,
    review_date: str,
    completed_features: list[str],
    pending_features: list[str],
    challenges: list[str],
    solutions: list[str],
    next_sprint: list[str],
    mentor_comments: str = "",
):
    return await notion_service.create_project_review(
        review_title=review_title,
        review_date=review_date,
        completed_features=completed_features,
        pending_features=pending_features,
        challenges=challenges,
        solutions=solutions,
        next_sprint=next_sprint,
        mentor_comments=mentor_comments,
    )