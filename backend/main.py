from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="Enterprise Knowledge Assistant API",
    version="1.0.0"
)

app.include_router(api_router)