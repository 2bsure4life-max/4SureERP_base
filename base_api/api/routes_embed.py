from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ..services.embed_tokens import mint_embed_token

class EmbedReq(BaseModel):
    tenant: str = Field(..., alias="tenant")
    dashboard_id: str = Field(..., alias="dashboardId")
    scopes: List[str]
    subject: Optional[str] = "owner:root"

router = APIRouter()

@router.post("/embed-token")
def create_embed_token(req: EmbedReq):
    try:
        data = req.model_dump(by_alias=False)
        token = mint_embed_token(
            tenant=data["tenant"],
            dashboard_id=data["dashboard_id"],
            scopes=data["scopes"],
            subject=data.get("subject") or "owner:root",
        )
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"token_error: {e}")
