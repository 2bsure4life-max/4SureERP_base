from pydantic import BaseModel, Field
from typing import List

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: str
    password: str
    tenant: str = "demo"

class DashboardOut(BaseModel):
    dashboardId: str = Field(alias="dashboard_id")
    label: str
    embed: dict
    scopesRequired: list[str] = []

class RegistryOut(BaseModel):
    dashboards: List[DashboardOut]
