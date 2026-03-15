from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router
from app.core.config import settings

app = FastAPI(
    title="TaricAI API",
    description="Motor de clasificación arancelaria TARIC con IA",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

import os

# CORS: allow Vercel frontend + localhost for development
_cors_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]
# Add production frontend URL from env
_frontend_url = os.getenv("FRONTEND_URL", "")
if _frontend_url:
    _cors_origins.append(_frontend_url)
# In development, allow all origins
if settings.app_env == "development":
    _cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(v1_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "TaricAI API",
        "version": "0.1.0",
        "environment": settings.app_env,
    }
