from app.services.gemini_service import GeminiService
from app.tools.gmail_tool import send_email


RECIPIENT_EMAIL = "dwivedishivamcolab@gmail.com"


gemini = GeminiService()

prompt = f"""
You are an automation assistant.

The user explicitly requested the following action:

Send an email to {RECIPIENT_EMAIL}.

Subject:
Gemini Tool Calling Test

Message:
Hello Shivam,

This email was sent by Gemini automatic function calling
through FastAPI, n8n, and Gmail.

Regards,
Enterprise Knowledge Assistant

Use the send_email tool to perform the action.
After the tool finishes, clearly report whether it succeeded.
"""


result = gemini.generate_with_tools(
    prompt=prompt,
    tools=[
        send_email,
    ],
)

print("=" * 70)
print("GMAIL TOOL RESULT")
print("=" * 70)
print(result)