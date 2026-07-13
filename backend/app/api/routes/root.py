from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }