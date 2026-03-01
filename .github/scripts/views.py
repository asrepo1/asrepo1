#!/usr/bin/env python3
"""Accumulate GitHub profile repo traffic views into a shields.io endpoint gist + update README."""
import json, os, re, requests
from datetime import datetime, timezone

REPO = "areporeporepo/areporeporepo"
GIST_ID = os.environ["VIEWS_GIST_ID"]
TOKEN = os.environ["GH_GIST_TOKEN"]
headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}

# Get current state from gist
gist = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers).json()
badge = json.loads(gist["files"]["views.json"]["content"])
state = json.loads(gist["files"]["state.json"]["content"]) if "state.json" in gist["files"] else {}

total_u = state.get("total_u", int(badge["message"]))
last_seen = state.get("last", 0)
last_seen_u = state.get("last_u", 0)

# Get 14-day traffic from GitHub (needs repo scope)
traffic = requests.get(f"https://api.github.com/repos/{REPO}/traffic/views", headers=headers).json()
new_views = traffic.get("count", 0)
new_uniques = traffic.get("uniques", 0)

# Accumulate (avoid double-counting)
delta_u = max(0, new_uniques - last_seen_u)
total_u += delta_u

# Shields.io badge (clean, no extra fields)
badge = {"schemaVersion": 1, "label": "views", "message": str(total_u), "color": "grey", "style": "flat"}
# Internal state
state = {"last": new_views, "last_u": new_uniques, "total_u": total_u}
# Get referrers and popular paths
referrers = requests.get(f"https://api.github.com/repos/{REPO}/traffic/popular/referrers", headers=headers).json()
paths = requests.get(f"https://api.github.com/repos/{REPO}/traffic/popular/paths", headers=headers).json()

ref_lines = [f"{r['referrer']}: {r['count']} ({r['uniques']} unique)" for r in referrers[:10]]
path_lines = [f"{p['path']}: {p['count']} ({p['uniques']} unique)" for p in paths[:10]]

requests.patch(
    f"https://api.github.com/gists/{GIST_ID}",
    headers=headers,
    json={"files": {
        "views.json": {"content": json.dumps(badge)},
        "state.json": {"content": json.dumps(state)},
        "referrers.md": {"content": "# Referrers (14-day)\n\n" + ("\n".join(ref_lines) or "No data yet")},
        "popular.md": {"content": "# Popular Content (14-day)\n\n" + ("\n".join(path_lines) or "No data yet")},
    }},
)
print(f"unique={total_u} delta_u={delta_u}")
print(f"referrers: {ref_lines}")
print(f"paths: {path_lines}")

# --- Update README with analytics ---
readme_path = os.path.join(os.environ.get("GITHUB_WORKSPACE", "."), "README.md")
with open(readme_path) as f:
    readme = f.read()

now = datetime.now(timezone.utc).strftime("%b %d")
top_ref = referrers[0]["referrer"] if referrers else None
top_ref_count = referrers[0]["uniques"] if referrers else 0

lines = []
lines.append(f"`{total_u} visitors`")
if top_ref:
    lines.append(f"`via {top_ref}`")
lines.append(f"`as of {now}`")

analytics_block = " · ".join(lines)

readme = re.sub(
    r"<!-- analytics:start -->.*?<!-- analytics:end -->",
    f"<!-- analytics:start -->\n{analytics_block}\n<!-- analytics:end -->",
    readme, flags=re.DOTALL,
)

with open(readme_path, "w") as f:
    f.write(readme)
print(f"README updated: {analytics_block}")
