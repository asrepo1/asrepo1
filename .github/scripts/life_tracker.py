#!/usr/bin/env python3
"""Combined life tracker gist updater for GitHub Actions.

Refreshes the pinned gist hourly. Auto-resets CC bar after 5h staleness.
Auto-resets sanity checks each hour.
"""
import json
import os
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone

CONTENT_GIST_ID = os.environ.get("LIFE_GIST_ID", "160d94564f066a467d11353d1a71715f")
DATA_GIST_ID = os.environ.get("LIFE_DATA_GIST_ID", "4e7fd6c8ddd0302da0e1cb7a235bdaa7")
CONTENT_FILENAME = "\u2800"
PT = timezone(timedelta(hours=-8))

CC_BAR_WIDTH = 19
CC_STALE_HOURS = 5
CC_GRID_ROWS = 4
CC_GRID_COLS = 20
CC_LEVELS = {0: "⬜", 1: "🟩", 2: "🟩"}


def gh_api(method, path, **fields):
    cmd = ["gh", "api", "--method", method, path]
    for k, v in fields.items():
        cmd += ["-f", f"{k}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return r.stdout


def read_data():
    try:
        raw = gh_api("GET", f"/gists/{DATA_GIST_ID}")
        gist = json.loads(raw)
        f = gist.get("files", {}).get("tracker_data.json")
        if f and f.get("content"):
            return json.loads(f["content"])
    except Exception:
        pass
    return {
        "cc": {"pct": 0, "ts": None, "dates": []},
        "meat": {"entries": [], "goal_date": None, "goal_label": None},
        "zone5": {"sessions": [], "total_days": 0, "total_cal": 0, "goal": 365},
        "sanity": {"check1": False, "check2": False, "last_run": None},
        "cold_shower": {"dates": []},
    }


def write_data(data):
    gh_api("PATCH", f"/gists/{DATA_GIST_ID}",
           **{f"files[tracker_data.json][content]": json.dumps(data)})


def write_content(content):
    gh_api("PATCH", f"/gists/{CONTENT_GIST_ID}",
           **{f"files[{CONTENT_FILENAME}][content]": content,
              "description": " "})


def zone5_line(data):
    z = data.get("zone5", {})
    total = z.get("total_days", 0)
    goal = z.get("goal", 365)
    sessions = z.get("sessions", [])
    today = datetime.now(PT).date()
    session_dates = sorted(set(s["date"] for s in sessions), reverse=True)
    streak = 0
    check = today
    for d in session_dates:
        if d == check.strftime("%Y-%m-%d"):
            streak += 1
            check -= timedelta(days=1)
        elif d == (check - timedelta(days=1)).strftime("%Y-%m-%d"):
            check -= timedelta(days=1)
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return f"😮\u200d💨 {total}/{goal} 🔥{streak}"


def sanity_line(data):
    s = data.get("sanity", {})
    c1 = "✅" if s.get("check1") else "⬜"
    c2 = "✅" if s.get("check2") else "⬜"
    last = s.get("last_run", "")
    time_str = ""
    if last:
        try:
            dt = datetime.fromisoformat(last)
            time_str = f" {dt.strftime('%b%d %H:%M').lstrip('0')}"
        except Exception:
            pass
    return f"🧠 {c1}{c2} hourly ·{time_str}"


def meat_line(data):
    m = data.get("meat", {})
    entries = m.get("entries", [])
    today = datetime.now(PT).date()
    if entries:
        last_entry = max(entries, key=lambda e: e["date"])
        last_date = datetime.strptime(last_entry["date"], "%Y-%m-%d").date()
        days_clean = (today - last_date).days
    else:
        days_clean = 0
    import random
    quips = {
        range(0, 3): ["🐣 baby steps", "🍼 just started"],
        range(3, 7): ["🐔 cluckin along", "🥬 leaf me alone"],
        range(7, 14): ["🐄 safe for 1wk", "🌱 turning green"],
        range(14, 21): ["🦬 could eat one rn", "🥦 veggie warrior"],
        range(21, 30): ["🏔️ beast mode", "🐃 shaking rn"],
        range(30, 60): ["🦁 apex herbivore", "🌿 photosynthesis soon"],
        range(60, 90): ["🧘 transcended", "🐄 worship me now"],
        range(90, 180): ["🌳 became a tree", "🐃 sleep safe tonight"],
        range(180, 366): ["👽 post-human", "🏛️ meat is a myth"],
    }
    quip = ""
    for r, opts in quips.items():
        if days_clean in r:
            random.seed(days_clean)
            quip = random.choice(opts)
            break
    line = f"🥩 {days_clean}d clean"
    if quip:
        line += f" · {quip}"
    goal_date = m.get("goal_date")
    goal_label = m.get("goal_label", "")
    if goal_date:
        gd = datetime.strptime(goal_date, "%Y-%m-%d").date()
        moon = "🌑" if "moon" in (goal_label or "").lower() else "🎯"
        dt_str = gd.strftime("%b %d").lstrip("0")
        if gd > today:
            days_left = (gd - today).days
            line += f" → {moon} {dt_str} ({days_left}d)"
        else:
            line += f" {moon} ✅ {dt_str}"
    return line


def cold_shower_line(data):
    cs = data.get("cold_shower", {})
    dates = sorted(set(cs.get("dates", [])), reverse=True)
    today = datetime.now(PT).date()
    streak = 0
    check = today
    for d in dates:
        if d == check.strftime("%Y-%m-%d"):
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return f"🥶 {streak}d streak ❄️ coldest tap only"


def cc_bar(data):
    cc = data.get("cc", {})
    pct = cc.get("pct", 0)
    ts_str = cc.get("ts")
    if ts_str:
        try:
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=PT)
            if (datetime.now(PT) - ts).total_seconds() > CC_STALE_HOURS * 3600:
                pct = 0
                cc["pct"] = 0
        except Exception:
            pct = 0
    pct = max(0, min(100, pct))
    filled = round(pct / 100 * CC_BAR_WIDTH)
    empty = CC_BAR_WIDTH - filled
    return f"💻{'🟦' * filled}{'⬜' * empty}"


def cc_grid(data):
    cc = data.get("cc", {})
    dates = cc.get("dates", [])
    counts = dict(Counter(dates))
    today = datetime.now(PT).date()
    total_days = CC_GRID_ROWS * CC_GRID_COLS
    start_date = today - timedelta(days=total_days - 1)
    lines = []
    for row in range(CC_GRID_ROWS):
        cells = ""
        for d in range(CC_GRID_COLS):
            day_idx = row * CC_GRID_COLS + d
            date = start_date + timedelta(days=day_idx)
            if date > today:
                cells += "⬜"
            else:
                n = counts.get(date.strftime("%Y-%m-%d"), 0)
                cells += CC_LEVELS[min(n, 2)]
        lines.append(cells)
    lines.reverse()
    return "\n".join(lines)


def main():
    data = read_data()
    now = datetime.now(PT)

    # Log steak sandwich with Curtis at Whole Foods on 2026-03-08
    meat = data.setdefault("meat", {"entries": [], "goal_date": None, "goal_label": None})
    steak_entry = {"date": "2026-03-08", "item": "steak sandwich", "where": "Whole Foods", "with": "Curtis"}
    if not any(e.get("date") == "2026-03-08" and e.get("item") == "steak sandwich" for e in meat["entries"]):
        meat["entries"].append(steak_entry)

    # Auto-reset sanity checks each hour
    data.setdefault("sanity", {})
    data["sanity"]["check1"] = False
    data["sanity"]["check2"] = False
    data["sanity"]["last_run"] = now.isoformat()

    line1 = zone5_line(data)
    line2 = sanity_line(data)
    line3 = meat_line(data)
    line4 = cold_shower_line(data)
    line5 = cc_bar(data)
    timestamp = now.strftime("Updated %b %d %-I:%M%p PST").replace("AM", "am").replace("PM", "pm")

    preview = f"{line1}\n{line2}\n{line3}\n{line4}\n{line5}"
    grid = cc_grid(data)
    content = f"{preview}\n{timestamp}\n{grid}"

    write_data(data)
    write_content(content)
    print(content)
    print("\nupdated gist")


if __name__ == "__main__":
    main()
