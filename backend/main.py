from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.logging import logger
from app.exceptions.handlers import global_exception_handler


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# ----------------------------
# Global Exception Handler
# ----------------------------
app.add_exception_handler(
    Exception,
    global_exception_handler,
)


# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Root Endpoint
# ----------------------------
@app.get(
    "/",
    tags=["Health"],
)
async def root():
    logger.info("Health endpoint accessed")

    return {
        "message": "Enterprise Knowledge Assistant API",
        "version": settings.APP_VERSION,
        "status": "running",
    }


# ----------------------------
# API Routes
# ----------------------------
app.include_router(
    api_router,
    prefix=settings.API_PREFIX,
)