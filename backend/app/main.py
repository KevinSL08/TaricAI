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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
