from __future__ import annotations
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .db import engine, Base, SessionLocal
from .models import Tenant, User, Dashboard

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def run():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        tenant = db.query(Tenant).filter_by(key="demo").first()
        if not tenant:
            tenant = Tenant(key="demo", name="Demo Tenant")
            db.add(tenant); db.flush()

        owner = db.query(User).filter_by(email="owner@demo.local").first()
        if not owner:
            owner = User(tenant_id=tenant.id, email="owner@demo.local",
                         password_hash=pwd.hash("Owner123!"), role="owner")
            db.add(owner)

        defaults = [
            ("sales.main", "Sales", "/dashboard/sales.html"),
            ("accounting.main", "Accounting", "/dashboard/accounting.html"),
            ("employees.main", "Employees", "/dashboard/employees.html"),
            ("utility.web", "Web Search", "https://www.google.com/"),
        ]
        for module_id, label, url in defaults:
            if not db.query(Dashboard).filter_by(tenant_id=tenant.id, module_id=module_id).first():
                db.add(Dashboard(tenant_id=tenant.id, module_id=module_id, label=label, url=url, is_active=True))
        db.commit()
        print("Seed OK")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run()
