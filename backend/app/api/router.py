from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.root import router as root_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.document import router as document_router
from app.api.routes.chat import router as chat_router


api_router = APIRouter()

api_router.include_router(root_router)
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(document_router)
api_router.include_router(chat_router)
