from app.services.gemini_service import GeminiService


service = GeminiService()


tests = [
    (
        "Schedule a project review tomorrow from "
        "5 PM to 6 PM and email test@example.com "
        "about it."
    ),
    (
        "Create a high priority task to deploy Docker "
        "and save this conversation to Notion."
    ),
    (
        "What skills are mentioned in my resume?"
    ),
]


for question in tests:
    print("=" * 70)
    print("QUESTION:")
    print(question)

    plan = service.plan_agent_actions(
        question=question,
    )

    print("\nPLAN:")
    print(
        plan.model_dump_json(
            indent=2
        )
    )