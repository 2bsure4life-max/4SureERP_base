import json
from pathlib import Path
from typing import Any, List

REGISTRY_FILE = Path("/opt/4sureerp/4SureERP_base/registry/dashboards.json")

def load_dashboards() -> List[Any]:
    if not REGISTRY_FILE.exists():
        return []
    return json.loads(REGISTRY_FILE.read_text())

def save_dashboards(data: List[Any]) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(data, indent=2))
