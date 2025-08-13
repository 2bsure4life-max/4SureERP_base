from fastapi import APIRouter
from ..config import settings

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/version")
def version():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION}

@router.get("/whoami")
def whoami():
    # Stub until auth is wired: demo owner/root of demo tenant
    return {"sub": "owner:root", "tenant": "demo", "roles": ["owner"], "scopes": []}
