import json
import os

# Load roles.json dynamically
SECURITY_FILE = os.path.join(os.path.dirname(__file__), "roles.json")
with open(SECURITY_FILE, "r") as f:
    ROLES = json.load(f)["roles"]

def has_permission(role, permission):
    """Check if a given role has a specific permission"""
    role_data = ROLES.get(role)
    if not role_data:
        return False
    if "*" in role_data["permissions"]:
        return True
    return permission in role_data["permissions"]
