from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Application Starting...")

    # Future:
    # Database Connection
    # ChromaDB Initialization
    # Load Embedding Model
    # Load LLM

    yield

    logger.info("🛑 Application Shutting Down...")