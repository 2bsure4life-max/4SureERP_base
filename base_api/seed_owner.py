from base_api.db import SessionLocal
from base_api.models import Tenant, User
from base_api.security import hash_password
from sqlalchemy.inspection import inspect as sx
from sqlalchemy import String, Integer, Boolean

def _fallback_value(col):
    t = col.type
    if isinstance(t, String):
        return "default"
    if isinstance(t, Integer):
        return 0
    if isinstance(t, Boolean):
        return True
    # generic fallback
    return "default"

def ensure_default_tenant():
    db = SessionLocal()
    try:
        t = db.query(Tenant).filter(Tenant.name == "Default").one_or_none()
        if t:
            return t

        # Build kwargs that match your actual model
        mapper = sx(Tenant)
        kwargs = {}
        # Always set a name if present
        if hasattr(Tenant, "name"):
            kwargs["name"] = "Default"

        # Fill common identifier-ish fields *if they exist*
        for alias in ("code", "slug", "key", "short_name", "subdomain", "identifier"):
            if hasattr(Tenant, alias):
                kwargs[alias] = "default"

        # Ensure all required fields (non-null, no default, not PK) are filled
        for c in mapper.columns:
            if c.primary_key:
                continue
            if not c.nullable and not c.default and not c.server_default and c.key not in kwargs:
                kwargs[c.key] = _fallback_value(c)

        t = Tenant(**kwargs)
        db.add(t)
        db.commit()
        db.refresh(t)
        return t
    finally:
        db.close()

def ensure_owner_admin(email: str, password: str):
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.name == "Default").one_or_none()
        if not tenant:
            tenant = ensure_default_tenant()

        u = db.query(User).filter(User.email == email).one_or_none()
        if u:
            return {"ok": True, "msg": "admin already exists", "id": u.id, "tenant_id": u.tenant_id}

        u = User(
            tenant_id=tenant.id,
            email=email,
            password_hash=hash_password(password),
            role="owner",  # explicit even if default
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        return {"ok": True, "msg": "admin created", "id": u.id, "tenant_id": u.tenant_id}
    finally:
        db.close()

if __name__ == "__main__":
    print(ensure_owner_admin("owner@4sureerp.local", "ChangeMe!123"))
