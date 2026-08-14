from app.services.gemini_service import GeminiService


service = GeminiService()


test_questions = [
    (
        "What machine learning frameworks are "
        "mentioned in my resume?"
    ),
    (
        "Send an email to test@gmail.com saying "
        "the project meeting is postponed."
    ),
    (
        "Schedule a project review tomorrow "
        "from 5 PM to 6 PM."
    ),
    (
        "Schedule a meeting tomorrow."
    ),
]


for question in test_questions:
    print("\n" + "=" * 70)
    print("QUESTION:")
    print(question)

    decision = service.classify_agent_action(
        question=question,
    )

    print("\nDECISION:")
    print(
        decision.model_dump_json(
            indent=2
        )
    )