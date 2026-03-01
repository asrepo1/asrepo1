#!/usr/bin/env python3
"""Accumulate GitHub profile repo traffic views into a shields.io endpoint gist."""
import json, os, requests

REPO = "areporeporepo/areporeporepo"
GIST_ID = os.environ["VIEWS_GIST_ID"]
TOKEN = os.environ["GH_GIST_TOKEN"]
headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}

# Get current count from gist
gist = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers).json()
current = json.loads(gist["files"]["views.json"]["content"])
total = int(current["message"])

# Get 14-day traffic from GitHub (needs repo scope)
traffic = requests.get(f"https://api.github.com/repos/{REPO}/traffic/views", headers=headers).json()
new_views = traffic.get("count", 0)
new_uniques = traffic.get("uniques", 0)

# Accumulate (store last seen count to avoid double-counting)
last_seen = int(current.get("_last", 0))
last_seen_u = int(current.get("_last_u", 0))
delta = max(0, new_views - last_seen)
delta_u = max(0, new_uniques - last_seen_u)
total += delta
total_u = int(current.get("_total_u", 0)) + delta_u

# Update gist
payload = {
    "schemaVersion": 1,
    "label": "views",
    "message": str(total_u),
    "color": "grey",
    "style": "flat",
    "_last": new_views,
    "_last_u": new_uniques,
    "_total_u": total_u,
}
requests.patch(
    f"https://api.github.com/gists/{GIST_ID}",
    headers=headers,
    json={"files": {"views.json": {"content": json.dumps(payload)}}},
)
print(f"total={total} unique={total_u} delta={delta} delta_u={delta_u}")
