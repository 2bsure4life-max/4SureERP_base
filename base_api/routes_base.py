from fastapi import APIRouter, Request
from .config import settings

router = APIRouter()

@router.get("/api/health")
def health(): return {"status":"ok"}

@router.get("/api/version")
def version(): return {"name": settings.APP_NAME, "version": settings.APP_VERSION}

@router.get("/api/whoami")
def whoami(req: Request):
    # Day-1 stub: no session parsing; return a simple owner:root identity
    return {"sub":"owner:root","tenant":"demo","roles":["owner"],"scopes":[]}
