from app.services.gemini_service import GeminiService


service = GeminiService()


test_cases = [
    {
        "name": "RAG",
        "question": (
            "What skills are mentioned in my uploaded resume?"
        ),
        "expected": "rag",
    },
    {
        "name": "Send Email",
        "question": (
            "Send an email to test@example.com saying "
            "the project meeting is postponed."
        ),
        "expected": "send_email",
    },
    {
        "name": "Email Missing Details",
        "question": (
            "Send an email saying tomorrow's meeting "
            "has been cancelled."
        ),
        "expected": "email_missing_details",
    },
    {
        "name": "Calendar",
        "question": (
            "Schedule a project review tomorrow "
            "from 5 PM to 6 PM."
        ),
        "expected": "create_calendar_event",
    },
    {
        "name": "Calendar Missing Details",
        "question": (
            "Schedule a project meeting tomorrow."
        ),
        "expected": "calendar_missing_details",
    },
    {
        "name": "Save Chat",
        "question": (
            "Save this conversation to Notion."
        ),
        "expected": "save_chat",
    },
    {
        "name": "Save Summary",
        "question": (
            "Save this document summary to Notion. "
            "Document: project_report.pdf. "
            "Summary: The project uses RAG, LangGraph, "
            "FastAPI and n8n for enterprise knowledge "
            "retrieval and automation."
        ),
        "expected": "save_summary",
    },
    {
        "name": "Create Task",
        "question": (
            "Create a high priority task to deploy "
            "Docker by August 20."
        ),
        "expected": "create_task",
    },
    {
        "name": "Meeting Notes",
        "question": (
            "Save today's project meeting notes to Notion. "
            "The meeting was about completing the Notion "
            "integration. We decided to finish FastAPI "
            "integration before LangGraph. "
            "Action item: test all Notion APIs."
        ),
        "expected": "meeting_notes",
    },
    {
        "name": "Save Insight",
        "question": (
            "Save this security insight to Notion. "
            "Title: Authentication Security Risk. "
            "Category: Security. "
            "Importance: High. "
            "Insight: Missing multi-factor authentication "
            "increases the risk of unauthorized access. "
            "Source document: security_report.pdf."
        ),
        "expected": "save_insight",
    },
    {
        "name": "Project Review",
        "question": (
            "Create this week's project review in Notion. "
            "Completed: Gmail, Calendar and Notion integration. "
            "Pending: LangGraph integration and Docker deployment. "
            "Challenge: Notion property mapping. "
            "Solution: corrected database property mappings. "
            "Next sprint: complete LangGraph integration."
        ),
        "expected": "project_review",
    },
]


passed = 0


for test in test_cases:
    print("\n" + "=" * 70)
    print("TEST:", test["name"])

    print("QUESTION:")
    print(test["question"])

    decision = service.classify_agent_action(
        question=test["question"],
    )

    print("\nEXPECTED:")
    print(test["expected"])

    print("\nACTUAL:")
    print(decision.action)

    print("\nFULL DECISION:")
    print(
        decision.model_dump_json(
            indent=2
        )
    )

    if decision.action == test["expected"]:
        print("\nRESULT: PASS")
        passed += 1
    else:
        print("\nRESULT: FAIL")


print("\n" + "=" * 70)

print(
    f"FINAL RESULT: "
    f"{passed}/{len(test_cases)} tests passed"
)

print("=" * 70)