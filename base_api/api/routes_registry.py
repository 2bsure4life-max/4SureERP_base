from typing import List, Any
from fastapi import APIRouter
from ..domain.registry import load_dashboards, save_dashboards

router = APIRouter()

@router.get("/registry/dashboards")
def get_dashboards() -> List[Any]:
    return load_dashboards()

@router.put("/registry/dashboards")
def put_dashboards(payload: List[Any]) -> dict:
    save_dashboards(payload)
    return {"ok": True, "count": len(payload)}
