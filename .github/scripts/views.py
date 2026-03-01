#!/usr/bin/env python3
"""Dynamic profile README — Claude generates content based on traffic audience."""
import json, os, re, requests
from datetime import datetime, timezone

REPO = "areporeporepo/areporeporepo"
GIST_ID = os.environ["VIEWS_GIST_ID"]
TOKEN = os.environ["GH_GIST_TOKEN"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
gh = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}

# --- Collect traffic data ---
gist = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=gh).json()
state = json.loads(gist["files"]["state.json"]["content"]) if "state.json" in gist.get("files", {}) else {}

total_u = state.get("total_u", 0)
last_seen_u = state.get("last_u", 0)

traffic = requests.get(f"https://api.github.com/repos/{REPO}/traffic/views", headers=gh).json()
new_uniques = traffic.get("uniques", 0)
delta_u = max(0, new_uniques - last_seen_u)
total_u += delta_u

referrers = requests.get(f"https://api.github.com/repos/{REPO}/traffic/popular/referrers", headers=gh).json()
paths = requests.get(f"https://api.github.com/repos/{REPO}/traffic/popular/paths", headers=gh).json()

ref_map = {r["referrer"]: r["count"] for r in referrers} if referrers else {}
top_ref = referrers[0]["referrer"] if referrers else "github.com"
now = datetime.now(timezone.utc).strftime("%b %d, %Y")

# --- Ask Claude to write the profile ---
BIO = """
Name: Anh Nguyen
Location: Palo Alto, CA
Education: UCLA, 2019
Current coursework: NBIO 206, NBIO 220 (Winter 2026)
Skills: EEG signal processing, brain-computer interfaces, motor imagery decoding
Tech: Python, PyTorch, MNE-Python, Three.js, TypeScript, Rust, Go
Projects:
  - OpenEyes1: open-source NASA Eyes solar system visualization (Three.js + astronomy-engine)
  - Agent Space: 3D globe + AI chat on HuggingFace (CesiumJS + FastAPI + Qwen 72B)
  - NVIDIA Atlas weather forecasting on Modal (4.3B param model, A100 GPU)
  - Brain-computer interface research (EEG, motor imagery)
Links:
  - Globe: https://huggingface.co/spaces/anhnq/agent
  - Photos: https://www.icloud.com/sharedalbum/#B26GWZuqDe1JNh
Interests: fusion energy, neuroscience, semiconductors (TSMC/NVIDIA), national labs
"""

prompt = f"""Write a GitHub profile README for this person. Output ONLY the markdown, nothing else.

{BIO}

Traffic analytics (last 14 days):
- {total_u} unique visitors
- Top referrers: {json.dumps(ref_map)}
- Top pages: {json.dumps([p['path'] for p in paths[:5]])}
- Dominant referrer: {top_ref}

Adapt the tone and content emphasis based on where visitors are coming from:
- linkedin.com / indeed.com → professional resume tone, highlight experience and impact
- github.com / stackoverflow / HN / reddit → technical, show skills and projects with code details
- scholar.google / arxiv / pubmed → academic, emphasize research and publications
- google.com / twitter / social → general intro, accessible, highlight cool projects

Keep it SHORT — under 15 lines of markdown. No emojis. No badges. No images.
Must include the Globe and Photos links at the bottom separated by " · ".
End with a single line: <sub>visitor count · top referrer · date</sub>
"""

resp = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers={
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    },
    json={
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}],
    },
)

if resp.status_code == 200:
    profile_content = resp.json()["content"][0]["text"].strip()
    print(f"Claude generated {len(profile_content)} chars")
else:
    # Fallback if API fails
    print(f"Claude API error {resp.status_code}: {resp.text}")
    profile_content = f"""### Anh Nguyen

Neuroscience + AI, Palo Alto. UCLA 2019.

`EEG signal processing` `brain-computer interfaces` `motor imagery decoding`

---

[🌍 Globe](https://huggingface.co/spaces/anhnq/agent) · [Endorphin](https://www.icloud.com/sharedalbum/#B26GWZuqDe1JNh)

<sub>{total_u} visitors from {top_ref} · {now}</sub>"""

# --- Write README ---
readme_path = os.path.join(os.environ.get("GITHUB_WORKSPACE", "."), "README.md")
with open(readme_path) as f:
    readme = f.read()

readme = re.sub(
    r"<!-- profile:start -->.*?<!-- profile:end -->",
    f"<!-- profile:start -->\n{profile_content}\n<!-- profile:end -->",
    readme, flags=re.DOTALL,
)

with open(readme_path, "w") as f:
    f.write(readme)

# --- Update gist ---
state = {"last": traffic.get("count", 0), "last_u": new_uniques, "total_u": total_u, "audience": top_ref, "top_ref": top_ref}
badge = {"schemaVersion": 1, "label": "views", "message": str(total_u), "color": "grey", "style": "flat"}
ref_lines = [f"{r['referrer']}: {r['count']} ({r['uniques']} unique)" for r in referrers[:10]]
path_lines = [f"{p['path']}: {p['count']} ({p['uniques']} unique)" for p in paths[:10]]

requests.patch(
    f"https://api.github.com/gists/{GIST_ID}",
    headers=gh,
    json={"files": {
        "views.json": {"content": json.dumps(badge)},
        "state.json": {"content": json.dumps(state)},
        "referrers.md": {"content": "# Referrers (14-day)\n\n" + ("\n".join(ref_lines) or "No data yet")},
        "popular.md": {"content": "# Popular Content (14-day)\n\n" + ("\n".join(path_lines) or "No data yet")},
    }},
)

print(f"top_ref={top_ref} unique={total_u}")
print(f"referrers: {ref_map}")
