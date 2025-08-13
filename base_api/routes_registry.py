from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from .db import get_db
from .models import Dashboard, Tenant
from .schemas import RegistryOut, DashboardOut

router = APIRouter()

@router.get("/api/registry/dashboards", response_model=RegistryOut)
def get_dashboards(tenant: str = Query("demo"), db: Session = Depends(get_db)):
    ten = db.query(Tenant).filter(Tenant.slug==tenant).first()
    if not ten:
        return {"dashboards": []}
    rows = db.query(Dashboard).filter(Dashboard.tenant_id==ten.id).order_by(Dashboard.dashboard_id).all()
    out = []
    for r in rows:
        out.append(DashboardOut(
            dashboard_id=r.dashboard_id,
            label=r.label,
            embed={"url": r.embed_url, "height": r.height, "capabilities": r.capabilities.get("capabilities", [])},
            scopesRequired=r.scopes_required.get("scopes", [])
        ))
    return {"dashboards": out}
