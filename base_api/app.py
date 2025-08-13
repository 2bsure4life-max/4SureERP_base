from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes_base import router as base_router
from .routes_auth import router as auth_router
from .routes_registry import router as registry_router

def build_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(base_router)
    app.include_router(auth_router)
    app.include_router(registry_router)
    return app

app = build_app()
