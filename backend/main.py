from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import logger

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(api_router)


logger.info("Application Started Successfully")