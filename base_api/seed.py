from base_api.db import SessionLocal
from base_api.models import User  # adjust if name differs
from base_api.security import hash_password  # adjust if your helper name differs

def ensure_owner_admin(email: str, password: str):
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == email).one_or_none()
        if u:
            return {"ok": True, "msg": "admin already exists", "id": u.id}
        u = User(email=email, password_hash=hash_password(password), is_active=True, is_admin=True)
        db.add(u)
        db.commit()
        db.refresh(u)
        return {"ok": True, "msg": "admin created", "id": u.id}
    finally:
        db.close()
