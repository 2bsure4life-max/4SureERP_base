from fastapi import APIRouter
router = APIRouter()

@router.post("/login")
def login():
    # Placeholder: real auth/RBAC coming next
    return {"access_token": "dev", "token_type": "bearer"}

@router.post("/refresh")
def refresh():
    return {"access_token": "dev", "token_type": "bearer"}
