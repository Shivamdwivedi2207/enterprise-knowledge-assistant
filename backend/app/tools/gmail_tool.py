from typing import Any

from app.services.gmail_automation_service import (
    GmailAutomationService,
)


gmail_service = GmailAutomationService()


def send_email(
    to: str,
    subject: str,
    message: str,
) -> dict[str, Any]:
    """
    Send an email using the connected Gmail account.

    Use this tool only when the user explicitly asks to send
    an email and provides a valid recipient email address.

    Args:
        to:
            Recipient email address.

        subject:
            Subject of the email.

        message:
            Complete email body.

    Returns:
        The n8n Gmail workflow result.
    """

    if not to.strip():
        return {
            "success": False,
            "message": "Recipient email address is required.",
        }

    if "@" not in to:
        return {
            "success": False,
            "message": "Recipient email address is invalid.",
        }

    if not subject.strip():
        return {
            "success": False,
            "message": "Email subject is required.",
        }

    if not message.strip():
        return {
            "success": False,
            "message": "Email message is required.",
        }

    try:
        result = gmail_service.send_email_sync(
            to=to,
            subject=subject,
            message=message,
        )

        return {
            "success": True,
            "message": result.get(
                "message",
                "Email sent successfully.",
            ),
            "recipient": to,
        }

    except Exception as error:
        return {
            "success": False,
            "message": (
                "The email could not be sent. "
                f"Reason: {str(error)}"
            ),
        }