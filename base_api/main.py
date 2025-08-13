from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import jwt
import os

# ==== Settings ====
APP_ROOT = "/opt/4sureerp/4SureERP_base"
TEMPLATES = os.path.join(APP_ROOT, "views", "templates")
STATIC = os.path.join(APP_ROOT, "static")

JWT_KEY = os.environ.get("FOURSURE_JWT_KEY", "change-this-key")
JWT_ALG = "HS256"
TOKEN_MINUTES = 60  # session length

# ==== App ====
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://4sureerp.com", "https://www.4sureerp.com", "http://localhost:8000", "http://127.0.0.1:8000", "*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Models ----
class LoginReq(BaseModel):
    username: Optional[str] = None  # front-end uses username
    email: Optional[str] = None     # legacy field supported
    password: str

class LoginRes(BaseModel):
    access_token: str
    token_type: str = "bearer"
    exp: int

# ---- Helpers ----
def _utcnow():
    return datetime.now(timezone.utc)

def create_token(sub: str) -> dict:
    exp_dt = _utcnow() + timedelta(minutes=TOKEN_MINUTES)
    payload = {"sub": sub, "role": "owner", "exp": int(exp_dt.timestamp())}
    token = jwt.encode(payload, JWT_KEY, algorithm=JWT_ALG)
    return {"token": token, "exp": int(exp_dt.timestamp())}

def read_session_cookie(request: Request):
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Missing session")
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=[JWT_ALG])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session")

def require_session(request: Request):
    return read_session_cookie(request)

# ==== Health/version ====
@app.get("/api/health")
def health():
    return {"ok": True, "ts": _utcnow().isoformat()}

@app.get("/api/version")
def version():
    return {"service": "4sure-base", "version": "0.1.0"}

# ==== Login (new, used by your tiger page) ====
@app.post("/login", response_model=LoginRes)
def login(payload: LoginReq, response: Response):
    # Support either username or email; front-end sends `username`
    user_id = (payload.username or payload.email or "").strip()

    # Hardcoded owner credential for now (you asked for this):
    if user_id == "Admin" and payload.password == "FloRight4u":
        tok = create_token(sub=user_id)
        # Set secure, httpOnly cookie
        response.set_cookie(
            key="session",
            value=tok["token"],
            max_age=TOKEN_MINUTES * 60,
            secure=True,
            httponly=True,
            samesite="Lax",
            path="/"
        )
        return {"access_token": tok["token"], "exp": tok["exp"]}

    # If you later hook a DB/tenant login, add it here and keep the cookie logic.
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Legacy compatibility: /auth/login -> same behavior
@app.post("/auth/login", response_model=LoginRes)
def auth_login(payload: LoginReq, response: Response):
    return login(payload, response)

# ==== Logout ====
@app.post("/logout")
def logout():
    r = JSONResponse({"ok": True})
    # expire cookie
    r.delete_cookie("session", path="/")
    return r

# ==== Protected dashboard file ====
# We let FastAPI serve the HTML only if the session cookie is valid.
@app.get("/dashboard")
def dashboard(_: dict = Depends(require_session)):
    html_path = os.path.join(TEMPLATES, "dashboard.html")
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="dashboard.html not found")
    return FileResponse(html_path, media_type="text/html")

# (Optional) A quick guard endpoint to test auth from command line:
@app.get("/api/me")
def me(user: dict = Depends(require_session)):
    return {"user": user.get("sub"), "role": user.get("role")}
