#!/usr/bin/env python3
"""Dynamic profile README that reshapes based on traffic referrers."""
import json, os, re, requests
from datetime import datetime, timezone

REPO = "areporeporepo/areporeporepo"
GIST_ID = os.environ["VIEWS_GIST_ID"]
TOKEN = os.environ["GH_GIST_TOKEN"]
headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}

# --- Collect traffic data ---
gist = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers).json()
state = json.loads(gist.files["state.json"]["content"]) if "state.json" in gist.get("files", {}) else {}

total_u = state.get("total_u", 0)
last_seen_u = state.get("last_u", 0)

traffic = requests.get(f"https://api.github.com/repos/{REPO}/traffic/views", headers=headers).json()
new_uniques = traffic.get("uniques", 0)
delta_u = max(0, new_uniques - last_seen_u)
total_u += delta_u

referrers = requests.get(f"https://api.github.com/repos/{REPO}/traffic/popular/referrers", headers=headers).json()
paths = requests.get(f"https://api.github.com/repos/{REPO}/traffic/popular/paths", headers=headers).json()

# Determine audience from top referrer
ref_map = {r["referrer"]: r["count"] for r in referrers} if referrers else {}
top_ref = referrers[0]["referrer"] if referrers else "github.com"

def detect_audience(ref_map):
    """Classify the dominant audience from referrer data."""
    categories = {
        "professional": ["linkedin.com", "indeed.com", "angel.co", "wellfound.com"],
        "academic": ["scholar.google.com", "pubmed.ncbi.nlm.nih.gov", "researchgate.net", "arxiv.org", "semanticscholar.org"],
        "technical": ["github.com", "stackoverflow.com", "news.ycombinator.com", "reddit.com", "dev.to"],
        "general": ["google.com", "t.co", "twitter.com", "x.com", "facebook.com"],
    }
    scores = {cat: 0 for cat in categories}
    for ref, count in ref_map.items():
        for cat, domains in categories.items():
            if any(d in ref for d in domains):
                scores[cat] += count
                break
    if max(scores.values()) == 0:
        return "technical"  # default for github profile
    return max(scores, key=scores.get)

audience = detect_audience(ref_map)
now = datetime.now(timezone.utc).strftime("%b %d, %Y")

# --- Audience-specific content ---

PROFILES = {
    "professional": """### Anh Nguyen

Building at the intersection of neuroscience and AI.

**Experience** — Software engineering across AI/ML systems, real-time signal processing, and full-stack development.

**Focus areas** — Brain-computer interfaces, EEG decoding, generative AI, GPU-accelerated computing.

**Education** — UCLA, 2019

---

[🌍 Globe](https://huggingface.co/spaces/anhnq/agent) · [Endorphin](https://www.icloud.com/sharedalbum/#B26GWZuqDe1JNh)""",

    "academic": """### Anh Nguyen

Neuroscience + computation.

**Research interests** — EEG signal processing, motor imagery decoding, brain-computer interfaces, neural data analysis.

**Coursework** — NBIO 206 · NBIO 220 (Winter 2026)

**Education** — UCLA, 2019

**Tools** — Python, PyTorch, MNE-Python, earth2studio, Three.js

---

[🌍 Globe](https://huggingface.co/spaces/anhnq/agent) · [Endorphin](https://www.icloud.com/sharedalbum/#B26GWZuqDe1JNh)""",

    "technical": """### Skills

**Neuro / BCI** · `EEG signal processing` `brain-computer interfaces` `motor imagery decoding`

---

### Education

**Winter 2026** — NBIO 206 · NBIO 220

UCLA, 2019

---

[🌍 Globe](https://huggingface.co/spaces/anhnq/agent) · [Endorphin](https://www.icloud.com/sharedalbum/#B26GWZuqDe1JNh)""",

    "general": """### Anh Nguyen

Neuroscience and AI, Palo Alto.

Building open-source tools — from [solar system visualization](https://huggingface.co/spaces/anhnq/openeyes1) to brain-computer interfaces.

UCLA, 2019

---

[🌍 Globe](https://huggingface.co/spaces/anhnq/agent) · [Endorphin](https://www.icloud.com/sharedalbum/#B26GWZuqDe1JNh)""",
}

profile_content = PROFILES[audience]

# Analytics footer
ref_list = " · ".join(f"`{r['referrer']}`" for r in referrers[:3]) if referrers else "`direct`"
footer = f"<sub>{total_u} visitors from {ref_list} · audience: {audience} · {now}</sub>"

readme_block = f"{profile_content}\n\n{footer}"

# --- Write README ---
readme_path = os.path.join(os.environ.get("GITHUB_WORKSPACE", "."), "README.md")
with open(readme_path) as f:
    readme = f.read()

readme = re.sub(
    r"<!-- profile:start -->.*?<!-- profile:end -->",
    f"<!-- profile:start -->\n{readme_block}\n<!-- profile:end -->",
    readme, flags=re.DOTALL,
)

with open(readme_path, "w") as f:
    f.write(readme)

# --- Update gist ---
state = {"last": traffic.get("count", 0), "last_u": new_uniques, "total_u": total_u, "audience": audience, "top_ref": top_ref}
badge = {"schemaVersion": 1, "label": "views", "message": str(total_u), "color": "grey", "style": "flat"}
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

print(f"audience={audience} top_ref={top_ref} unique={total_u}")
print(f"referrers: {ref_map}")
print(f"README mode: {audience}")
