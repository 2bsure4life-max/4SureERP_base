#!/usr/bin/env python3
import json, os
src = "/opt/4sureerp/4SureERP_base/registry/modules_ports.json"
dst = "/etc/nginx/includes/modules_map.conf"
data = json.load(open(src))
lines = ["# name  port;"]
for name, port in sorted(data.items()):
    lines.append(f"{name} {int(port)};")
os.makedirs(os.path.dirname(dst), exist_ok=True)
open(dst, "w").write("\n".join(lines) + "\n")
print(f"wrote {dst} with {len(data)} entries")
