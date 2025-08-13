from typing import List, Dict, Any
from time import time
import jwt  # PyJWT
from ..config import settings

def mint_embed_token(
    *,
    tenant: str,
    dashboard_id: str,
    scopes: List[str],
    subject: str = "owner:root"
) -> Dict[str, Any]:
    now = int(time())
    ttl = int(getattr(settings, "JWT_EXP_SECONDS", 600))
    iss = getattr(settings, "JWT_ISSUER", "4sure-base")
    key = getattr(settings, "JWT_SIGNING_KEY", "")
    if not key:
        raise RuntimeError("settings_missing: JWT_SIGNING_KEY")
    claims = {
        "sub": subject,
        "ten": tenant,
        "scopes": scopes,
        "dash": dashboard_id,
        "iat": now,
        "exp": now + ttl,
        "iss": iss,
    }
    token = jwt.encode(claims, key, algorithm="HS256")
    return {"token": token, "exp": claims["exp"], "iat": claims["iat"]}
