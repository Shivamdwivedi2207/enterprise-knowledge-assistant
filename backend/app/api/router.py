from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.root import router as root_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.document import router as document_router
from app.api.routes.chat import router as chat_router
from app.api.routes.source import router as source_router
from app.api.routes.automation import router as automation_router
from app.api.routes.gmail_automation import (
    router as gmail_automation_router,
)
from app.api.routes.calendar_automation import (
    router as calendar_automation_router,
)
from app.api.routes.admin import router as admin_router
from app.api.routes import notion


api_router = APIRouter()


# =========================================================
# Core
# =========================================================

api_router.include_router(
    root_router
)

api_router.include_router(
    health_router
)


# =========================================================
# Authentication / Users
# =========================================================

api_router.include_router(
    auth_router
)

api_router.include_router(
    users_router
)

api_router.include_router(
    admin_router
)


# =========================================================
# Documents / RAG
# =========================================================

api_router.include_router(
    document_router
)

api_router.include_router(
    source_router
)

api_router.include_router(
    chat_router
)


# =========================================================
# Automations
# =========================================================

api_router.include_router(
    automation_router
)

api_router.include_router(
    gmail_automation_router
)

api_router.include_router(
    calendar_automation_router
)

api_router.include_router(
    notion.router,
    prefix="/notion",
    tags=["Notion"],
)