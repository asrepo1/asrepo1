#!/usr/bin/env python3
"""Dynamic GitHub profile — README + bio/sidebar change based on traffic audience."""
import json, os, re, requests
from datetime import datetime, timezone

REPO = "areporeporepo/areporeporepo"
GIST_ID = os.environ["VIEWS_GIST_ID"]
TOKEN = os.environ["GH_GIST_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]
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
top_ref = referrers[0]["referrer"] if referrers else None
now = datetime.now(timezone.utc).strftime("%b %d, %Y")

# --- Deterministic audience detection ---
CATEGORIES = {
    "professional": ["linkedin.com", "indeed.com", "angel.co", "wellfound.com", "levels.fyi"],
    "academic": ["scholar.google.com", "pubmed.ncbi.nlm.nih.gov", "researchgate.net", "arxiv.org", "semanticscholar.org"],
    "technical": ["github.com", "stackoverflow.com", "news.ycombinator.com", "reddit.com", "dev.to"],
    "general": ["google.com", "t.co", "twitter.com", "x.com", "facebook.com", "instagram.com"],
}

def detect_audience(ref_map):
    scores = {cat: 0 for cat in CATEGORIES}
    for ref, count in ref_map.items():
        for cat, domains in CATEGORIES.items():
            if any(d in ref for d in domains):
                scores[cat] += count
                break
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "default"

audience = detect_audience(ref_map)
prev_audience = state.get("audience", "default")

# --- Deterministic sidebar profiles (bio, name, company, location) ---
SIDEBAR = {
    "default": {
        "name": "Anh Nguyen",
        "bio": "Neuro / BCI. EEG signal processing, brain-computer interfaces, motor imagery decoding.",
        "company": None,
        "location": "Palo Alto, CA",
        "blog": "https://huggingface.co/spaces/anhnq/agent",
    },
    "professional": {
        "name": "Anh Nguyen",
        "bio": "AI/ML engineer. BCI, EEG decoding, GPU-accelerated computing. UCLA 2019.",
        "company": None,
        "location": "Palo Alto, CA",
        "blog": "https://huggingface.co/spaces/anhnq/agent",
    },
    "academic": {
        "name": "Anh Q. Nguyen",
        "bio": "Neuroscience + computation. EEG signal processing, motor imagery decoding, brain-computer interfaces.",
        "company": None,
        "location": "Palo Alto, CA",
        "blog": "https://huggingface.co/spaces/anhnq/agent",
    },
    "technical": {
        "name": "Anh Nguyen",
        "bio": "Building BCI tools, solar system viz, GPU weather forecasting. Python/TS/Rust/Go.",
        "company": None,
        "location": "Palo Alto, CA",
        "blog": "https://huggingface.co/spaces/anhnq/agent",
    },
    "general": {
        "name": "Anh Nguyen",
        "bio": "Neuroscience and AI, Palo Alto. Building open-source tools from brain-computer interfaces to solar system viz.",
        "company": None,
        "location": "Palo Alto, CA",
        "blog": "https://huggingface.co/spaces/anhnq/agent",
    },
}

# Update sidebar if audience changed
sidebar = SIDEBAR[audience]
if audience != prev_audience:
    resp = requests.patch("https://api.github.com/user", headers=gh, json=sidebar)
    print(f"Sidebar updated: {resp.status_code} ({audience})")
else:
    print(f"Sidebar unchanged ({audience})")

# --- Default README (deterministic, no AI call needed) ---
DEFAULT_README = f"""### Skills

**Neuro / BCI** · `EEG signal processing` `brain-computer interfaces` `motor imagery decoding`

---

### Education

**Winter 2026** — NBIO 206 · NBIO 220

UCLA, 2019

---

[Globe](https://huggingface.co/spaces/anhnq/agent) · [Endorphin](https://www.icloud.com/sharedalbum/#B26GWZuqDe1JNh)

<sub>{total_u} visitors · {now}</sub>"""

# --- AI-generated README for non-default audiences ---
BIO = """Name: Anh Nguyen
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
Links (MUST include exactly as-is):
  - [Globe](https://huggingface.co/spaces/anhnq/agent) · [Endorphin](https://www.icloud.com/sharedalbum/#B26GWZuqDe1JNh)
Interests: fusion energy, neuroscience, semiconductors (TSMC/NVIDIA), national labs"""

AUDIENCE_INSTRUCTIONS = {
    "professional": "Write for recruiters/hiring managers from LinkedIn. Professional resume tone. Lead with impact and experience. Highlight engineering skills and project scale.",
    "academic": "Write for researchers from Google Scholar/arXiv. Academic tone. Lead with research interests and methodology. Highlight neuroscience work, coursework, and tools.",
    "technical": "Write for developers from GitHub/HN/Reddit. Technical tone. Lead with skills and code. Highlight projects with tech stack details.",
    "general": "Write for general visitors from Google/social media. Accessible, concise intro. Highlight the coolest projects in plain language.",
}

if audience == "default":
    profile_content = DEFAULT_README
    print("Using default README (no dominant referrer)")
else:
    prompt = f"""Write a GitHub profile README. Output ONLY markdown, nothing else.

{BIO}

Audience: {AUDIENCE_INSTRUCTIONS[audience]}
Dominant referrer: {top_ref}

RULES:
- Under 15 lines of markdown
- No emojis, no badges, no images
- MUST end with exactly: [Globe](https://huggingface.co/spaces/anhnq/agent) · [Endorphin](https://www.icloud.com/sharedalbum/#B26GWZuqDe1JNh)
- Last line MUST be exactly: <sub>{total_u} visitors · {top_ref} · {now}</sub>
"""

    resp = requests.post(
        "https://router.huggingface.co/v1/chat/completions",
        headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
        json={
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "max_tokens": 512,
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    if resp.status_code == 200:
        profile_content = resp.json()["choices"][0]["message"]["content"].strip()
        profile_content = re.sub(r"^```(?:markdown|md)?\n?", "", profile_content)
        profile_content = re.sub(r"\n?```$", "", profile_content)
        print(f"AI generated {len(profile_content)} chars for audience={audience}")
    else:
        print(f"HF API error {resp.status_code}: {resp.text}")
        profile_content = DEFAULT_README

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
state = {"last": traffic.get("count", 0), "last_u": new_uniques, "total_u": total_u, "audience": audience, "top_ref": top_ref}
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

print(f"audience={audience} top_ref={top_ref} unique={total_u}")
print(f"referrers: {ref_map}")
