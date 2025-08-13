from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import get_db
from .models import User, Tenant
from .security import verify_password, make_token
from .config import settings
from .schemas import LoginIn, TokenOut

router = APIRouter()

@router.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    ten = db.query(Tenant).filter(Tenant.slug==body.tenant).first()
    if not ten:
        raise HTTPException(status_code=400, detail="Tenant not found")
    user = db.query(User).filter(User.tenant_id==ten.id, User.email==body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = make_token(sub=f"{ten.slug}:{user.id}", minutes=settings.ACCESS_TOKEN_MINUTES, extra={"role": user.role})
    refresh = make_token(sub=f"{ten.slug}:{user.id}", minutes=settings.REFRESH_TOKEN_MINUTES, extra={"type":"refresh"})
    return {"access_token": access, "refresh_token": refresh}

@router.post("/auth/refresh", response_model=TokenOut)
def refresh():
    # stub: in real flow you would verify refresh token; for day-1 we just say "not implemented"
    raise HTTPException(status_code=501, detail="Refresh not implemented in Day 1 stub")
