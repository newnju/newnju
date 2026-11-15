#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generates the animated profile widgets for the GitHub profile README.

Every widget is a self-contained SVG that relies only on SMIL, so it renders
on github.com (which sanitises but does allow <animate>/<animateTransform>)
and keeps animating without any third-party image host.

Run:  python scripts/generate_animated.py
Out:  assets/<name>.svg
"""

import html
import json
import math
import os
import random
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

USERNAME = "newnju"

# tokyonight-ish palette, matching the rest of the profile
BG = "#0d1117"
CARD = "#161b22"
BORDER = "#30363d"
TXT = "#c9d1d9"
MUT = "#8b949e"
BLUE = "#58a6ff"
CYAN = "#36BCF7"
GREEN = "#3fb950"
TEAL = "#2BD9A8"
PURPLE = "#bc8cff"
YELLOW = "#e3b341"
RED = "#f85149"
ORANGE = "#db6d28"
PINK = "#f778ba"

FONT = "Segoe UI, Helvetica, Arial, sans-serif"
MONO = "Consolas, Menlo, monospace"


def open_svg(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}">'
    )


def card(w, h, rx=16, fill=CARD, stroke=BORDER):
    return (
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
    )


def write(name, content):
    path = ASSETS_DIR / name
    # newline="\n" keeps output byte-identical on Windows and Linux runners,
    # so the daily job does not churn every file through CRLF/LF flips.
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Generated: {path.relative_to(ASSETS_DIR.parent)} ({len(content):,} bytes)")


# --------------------------------------------------------------------------
# 1. aurora banner - layered flowing gradient ribbons
# --------------------------------------------------------------------------
def aurora():
    w, h = 1000, 220
    s = open_svg(w, h)
    s += (
        "<defs>"
        '<linearGradient id="aubg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{BG}"/>'
        '<stop offset="0.55" stop-color="#10162a"/>'
        '<stop offset="1" stop-color="#0b1a24"/>'
        "</linearGradient>"
        '<linearGradient id="rib1" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{TEAL}" stop-opacity="0.15"/>'
        f'<stop offset="0.35" stop-color="{CYAN}" stop-opacity="0.75"/>'
        f'<stop offset="0.7" stop-color="{PURPLE}" stop-opacity="0.7"/>'
        f'<stop offset="1" stop-color="{PINK}" stop-opacity="0.15"/>'
        "</linearGradient>"
        '<linearGradient id="rib2" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{BLUE}" stop-opacity="0.1"/>'
        f'<stop offset="0.5" stop-color="{GREEN}" stop-opacity="0.6"/>'
        f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0.1"/>'
        "</linearGradient>"
        '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.30"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0"/>'
        "</radialGradient>"
        "</defs>"
    )
    s += f'<rect width="{w}" height="{h}" fill="url(#aubg)"/>'
    s += (
        f'<ellipse cx="{w / 2}" cy="150" rx="380" ry="120" fill="url(#glow)">'
        '<animate attributeName="cx" values="300;700;300" dur="16s" repeatCount="indefinite"/>'
        "</ellipse>"
    )

    def ribbon(amp, base, period, width, bottom, grad, dur, opacity):
        d = f"M0 {base}"
        x = 0
        up = True
        while x < width + period:
            nx = x + period / 2
            cy = base - amp if up else base + amp
            d += f" Q {x + period / 4} {cy} {nx} {base}"
            x = nx
            up = not up
        d += f" L {width + period} {bottom} L 0 {bottom} Z"
        return (
            f'<path d="{d}" fill="url(#{grad})" opacity="{opacity}">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 0" to="-{period} 0" dur="{dur}" repeatCount="indefinite"/>'
            "</path>"
        )

    s += ribbon(40, 120, 330, w, h + 40, "rib1", "13s", 0.55)
    s += ribbon(28, 145, 250, w, h + 40, "rib2", "9s", 0.45)
    s += ribbon(18, 165, 190, w, h + 40, "rib1", "7s", 0.30)

    random.seed(11)
    for _ in range(42):
        x = random.randint(0, w)
        y = random.randint(0, 150)
        r = random.choice([1, 1.2, 1.6, 2])
        dur = round(random.uniform(2.0, 5.0), 2)
        s += (
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" opacity="0.7">'
            f'<animate attributeName="opacity" values="0.05;0.85;0.05" '
            f'dur="{dur}s" repeatCount="indefinite"/></circle>'
        )

    s += (
        f'<text x="{w / 2}" y="78" text-anchor="middle" font-size="34" '
        f'font-weight="700" fill="{TXT}">@{USERNAME}'
        '<animate attributeName="opacity" values="0.7;1;0.7" dur="4s" repeatCount="indefinite"/></text>'
    )
    s += (
        f'<text x="{w / 2}" y="112" text-anchor="middle" font-size="16" fill="{MUT}">'
        "code &#183; compile &#183; repeat</text>"
    )
    s += "</svg>"
    return s


# --------------------------------------------------------------------------
# 2. skill radar - rotating sweep over a hexagon of language share
# --------------------------------------------------------------------------
def skill_radar():
    """Hexagonal radar of real language share with a rotating sweep."""
    w, h = 460, 400
    cx, cy, radius = w / 2, 190, 120
    # real share over own repos
    data = [
        ("JavaScript", 6),
        ("Python", 3),
        ("TypeScript", 3),
        ("Astro", 2),
        ("HTML", 1),
        ("CSS", 1),
    ]
    total = sum(v for _, v in data)
    colors = [YELLOW, BLUE, CYAN, PURPLE, ORANGE, TEAL]

    s = open_svg(w, h)
    s += (
        "<defs>"
        '<radialGradient id="sweep" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.45"/>'
        f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>'
        "</radialGradient>"
        '<linearGradient id="poly" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.55"/>'
        f'<stop offset="1" stop-color="{PURPLE}" stop-opacity="0.35"/>'
        "</linearGradient>"
        "</defs>"
    )
    s += card(w, h)

    n = len(data)

    def pt(i, r):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        return cx + r * math.cos(ang), cy + r * math.sin(ang)

    # grid rings
    for ring in (0.33, 0.66, 1.0):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, radius * ring) for i in range(n)))
        s += f'<polygon points="{pts}" fill="none" stroke="{BORDER}" stroke-width="1"/>'

    # spokes + labels
    for i, (name, val) in enumerate(data):
        x, y = pt(i, radius)
        lx, ly = pt(i, radius + 26)
        s += f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{BORDER}" stroke-width="1"/>'
        share = round(val / total * 100)
        s += (
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="12" '
            f'fill="{colors[i]}">{html.escape(name)}</text>'
        )
        s += (
            f'<text x="{lx:.1f}" y="{ly + 14:.1f}" text-anchor="middle" font-size="10" '
            f'fill="{MUT}">{share}%</text>'
        )

    # data polygon
    pts = []
    for i, (_, val) in enumerate(data):
        r = radius * (val / max(v for _, v in data))
        pts.append(pt(i, r))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    s += f'<polygon points="{poly}" fill="url(#poly)" stroke="{CYAN}" stroke-width="2"/>'
    for x, y in pts:
        s += (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{TXT}">'
            '<animate attributeName="r" values="3.5;5.5;3.5" dur="2.4s" repeatCount="indefinite"/></circle>'
        )

    # rotating sweep
    s += (
        f'<g opacity="0.9">'
        f'<path d="M{cx},{cy} L{cx},{cy - radius} A{radius},{radius} 0 0 1 '
        f'{cx + radius * 0.35:.1f},{cy - radius * 0.94:.1f} Z" fill="url(#sweep)"/>'
        f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - radius}" stroke="{CYAN}" stroke-width="1.5">'
        '<animateTransform attributeName="transform" type="rotate" '
        f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="4.5s" repeatCount="indefinite"/></line>'
        "</g>"
    )

    s += (
        f'<text x="{cx}" y="{h - 26}" text-anchor="middle" font-size="13" fill="{MUT}">'
        f"language share &#183; {total} own repos</text>"
    )
    s += "</svg>"
    return s


# --------------------------------------------------------------------------
# 3. marquee ticker - scrolling repo chips
# --------------------------------------------------------------------------
def ticker():
    """Infinite horizontal scroll of repo chips."""
    repos = [
        "jingtun", "droidseal", "newnju.github.io", "from-stars-to-pr-replication",
        "internfinding", "jiaowolian", "speech-to-text", "seekdb", "hh", "pdf",
    ]
    w, h = 900, 46
    chip_w = 190
    gap = 14
    total = len(repos) * (chip_w + gap)

    def chip(rep, x):
        return (
            f'<g transform="translate({x},8)">'
            f'<rect width="{chip_w}" height="30" rx="15" fill="{CARD}" stroke="{BORDER}"/>'
            f'<circle cx="16" cy="15" r="4" fill="{GREEN}"/>'
            f'<text x="30" y="20" font-family="{MONO}" font-size="13" fill="{TXT}">'
            f"{html.escape(rep)}</text></g>"
        )

    s = open_svg(w, h)
    s += f"<defs><clipPath id='tkclip'><rect width='{w}' height='{h}' rx='12'/></clipPath></defs>"
    s += f'<rect width="{w}" height="{h}" rx="12" fill="{BG}" stroke="{BORDER}"/>'
    s += '<g clip-path="url(#tkclip)">'
    # one strip holds both copies; the strip slides left by exactly one period
    s += (
        '<g><animateTransform attributeName="transform" type="translate" '
        f'from="0 0" to="-{total} 0" dur="28s" repeatCount="indefinite"/>'
    )
    for i, rep in enumerate(repos):
        s += chip(rep, i * (chip_w + gap))
    # second copy is offset by one period so the loop is seamless
    for i, rep in enumerate(repos):
        s += chip(rep, total + i * (chip_w + gap))
    s += "</g></g>"
    s += "</svg>"
    return s


# --------------------------------------------------------------------------
# 4. pulse - heartbeat waveform, live contribution pulse
# --------------------------------------------------------------------------
def pulse():
    """ECG-style waveform that loops."""
    w, h = 800, 150
    s = open_svg(w, h)
    s += (
        "<defs>"
        '<linearGradient id="pg" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{TEAL}"/>'
        f'<stop offset="0.5" stop-color="{CYAN}"/>'
        f'<stop offset="1" stop-color="{PURPLE}"/>'
        "</linearGradient>"
        "</defs>"
    )
    s += card(w, h)
    s += (
        f'<text x="24" y="30" font-size="14" font-weight="700" fill="{MUT}">'
        "&#9881; contribution pulse</text>"
    )

    mid = 90
    pts = []
    x = 30
    while x < w - 20:
        # one heartbeat cycle
        for dx, dy in ((0, 0), (18, 0), (26, -6), (34, 0), (42, 0),
                       (48, 34), (54, -46), (60, 34), (66, 0), (74, 0), (82, -14),
                       (90, 0), (100, 0)):
            pts.append((x + dx, mid + dy))
        x += 118
    path = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    s += (
        f'<path d="{path}" fill="none" stroke="url(#pg)" stroke-width="2.5" '
        'stroke-linejoin="round" stroke-linecap="round">'
        '<animate attributeName="stroke-dashoffset" values="1200;0" dur="3s" '
        'repeatCount="indefinite"/></path>'
    )
    # travelling dot
    s += (
        f'<circle r="5" fill="{TXT}">'
        '<animateMotion dur="3s" repeatCount="indefinite" path="'
        + path
        + '"/></circle>'
    )
    s += "</svg>"
    return s


# --------------------------------------------------------------------------
# 5. spotlight - cycling featured-repo cards
# --------------------------------------------------------------------------
def spotlight():
    """Cross-fading cards for a few real repos."""
    cards = [
        ("jingtun", "Chrome MV3 media sniffer for HLS / DASH", "JavaScript", CYAN),
        ("droidseal", "One-command end-to-end release security", "TypeScript", BLUE),
        ("newnju.github.io", "Jekyll + Pages site, PWA offline, view transitions", "JavaScript", GREEN),
        ("internfinding", "Internship information organiser", "TypeScript", PURPLE),
    ]
    w, h = 780, 170
    s = open_svg(w, h)
    s += card(w, h)
    dur = len(cards) * 3.0
    for i, (name, desc, lang, color) in enumerate(cards):
        begin = i * 3.0
        key = (
            f"0;{begin / dur:.4f};{(begin + 0.12) / dur:.4f};"
            f"{(begin + 2.7) / dur:.4f};{(begin + 3.0) / dur:.4f};1"
        )
        op = f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{key}" dur="{dur}s" repeatCount="indefinite"/>'
        tr = (
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 0;0 0;0 0;0 0" dur="{dur}s" repeatCount="indefinite"/>'
        )
        s += f'<g opacity="0">{op}{tr}'
        s += (
            f'<rect x="24" y="26" width="{w - 48}" height="118" rx="12" fill="#0b0f1a" stroke="{BORDER}"/>'
            f'<rect x="24" y="26" width="4" height="118" rx="2" fill="{color}"/>'
        )
        s += (
            f'<text x="46" y="60" font-size="18" font-weight="700" fill="{color}">'
            f"{html.escape(name)}</text>"
        )
        s += (
            f'<text x="46" y="88" font-size="13" fill="{TXT}">{html.escape(desc)}</text>'
        )
        s += (
            f'<text x="46" y="116" font-size="11" font-family="{MONO}" fill="{MUT}">'
            f"&#9679; {html.escape(lang)}</text>"
        )
        s += "</g>"
    s += "</svg>"
    return s


# --------------------------------------------------------------------------
# 6. contribution heatmap - 26 weeks of real activity
# --------------------------------------------------------------------------
def heatmap():
    """Compact contribution heatmap driven by the public events API."""
    import requests

    weeks, days = 26, 7
    cell, gap = 13, 3
    step = cell + gap
    w = weeks * step + 70
    h = days * step + 64

    counts = {}
    try:
        for page in (1, 2, 3):
            r = requests.get(
                f"https://api.github.com/users/{USERNAME}/events/public?per_page=100&page={page}",
                timeout=30,
                headers={"Accept": "application/vnd.github+json"},
            )
            if r.status_code != 200:
                break
            events = r.json()
            if not events:
                break
            for ev in events:
                ts = ev.get("created_at")
                if not ts:
                    continue
                day = ts[:10]
                counts[day] = counts.get(day, 0) + 1
    except Exception:
        pass

    # build a date grid ending today
    from datetime import date, timedelta

    today = date.today()
    start = today - timedelta(weeks=weeks - 1)
    start = start - timedelta(days=start.weekday())

    s = open_svg(w, h)
    s += card(w, h)
    s += (
        f'<text x="22" y="30" font-size="14" font-weight="700" fill="{MUT}">'
        f"&#128202; last {weeks} weeks</text>"
    )
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    last_month = -1
    for wk in range(weeks):
        col_x = 70 + wk * step
        d = start + timedelta(weeks=wk)
        if d.month != last_month:
            s += (
                f'<text x="{col_x}" y="48" font-size="10" fill="{MUT}">'
                f"{month_names[d.month - 1]}</text>"
            )
            last_month = d.month
        for dow in range(days):
            day = d + timedelta(days=dow)
            if day > today:
                continue
            key = day.isoformat()
            n = counts.get(key, 0)
            if n >= 6:
                col = GREEN
            elif n >= 3:
                col = "#238636"
            elif n >= 1:
                col = "#196c2e"
            else:
                col = "#161b22"
            y = 58 + dow * step
            s += (
                f'<rect x="{col_x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
                f'fill="{col}" stroke="{BORDER}" stroke-width="0.5"/>'
            )
    s += (
        f'<text x="22" y="{h - 22}" font-size="11" fill="{MUT}">'
        f"{sum(counts.values())} public events</text>"
    )
    s += "</svg>"
    return s


def _api(path):
    """Fetch JSON from the GitHub API, tolerating network failure."""
    import requests

    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.get(f"https://api.github.com{path}", headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def _own_repos():
    """All non-fork repos owned by the account, across pagination."""
    repos = []
    for page in (1, 2, 3):
        batch = _api(f"/users/{USERNAME}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
    return [r for r in repos if not r.get("fork")]


def stats_cards():
    """Live account statistics as animated cards."""
    profile = _api(f"/users/{USERNAME}") or {}
    repos = _own_repos()
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    forks = sum(r.get("forks_count", 0) for r in repos)
    created = (profile.get("created_at") or "")[:4]
    years = 0
    if created:
        from datetime import date

        try:
            years = date.today().year - int(created)
        except ValueError:
            years = 0

    cells = [
        ("Repos", len(repos), CYAN),
        ("Stars", stars, YELLOW),
        ("Forks", forks, PURPLE),
        ("Followers", profile.get("followers", 0), GREEN),
        ("Following", profile.get("following", 0), TEAL),
        ("Years", years, ORANGE),
    ]
    w, h = 800, 220
    cw, ch, gap = 240, 84, 20
    s = open_svg(w, h)
    s += card(w, h)
    s += (
        f'<text x="24" y="34" font-size="15" font-weight="700" fill="{MUT}">'
        f"&#128200; account stats</text>"
    )
    for i, (label, value, color) in enumerate(cells):
        col = i % 3
        row = i // 3
        x = 24 + col * (cw + gap)
        y = 52 + row * (ch + 16)
        s += (
            f'<g transform="translate({x},{y})">'
            f'<rect width="{cw}" height="{ch}" rx="12" fill="#0b0f1a" stroke="{BORDER}"/>'
            f'<rect x="0" y="0" width="4" height="{ch}" rx="2" fill="{color}"/>'
            f'<text x="18" y="38" font-size="30" font-weight="700" fill="{color}">{value}</text>'
            f'<text x="18" y="64" font-size="12" fill="{MUT}">{label}</text>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 -4;0 0" dur="3s" begin="{i * 0.18}s" repeatCount="indefinite"/>'
            "</g>"
        )
    s += "</svg>"
    return s


def top_langs():
    """Horizontal language bars with real share, animated width."""
    repos = _own_repos()
    counts = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            counts[lang] = counts.get(lang, 0) + 1
    if not counts:
        counts = {"JavaScript": 1}
    ordered = sorted(counts.items(), key=lambda kv: -kv[1])[:6]
    total = sum(counts.values())
    palette = [YELLOW, BLUE, CYAN, PURPLE, ORANGE, TEAL]

    w, h = 800, 40 + len(ordered) * 44 + 12
    s = open_svg(w, h)
    s += card(w, h)
    s += (
        f'<text x="24" y="30" font-size="15" font-weight="700" fill="{MUT}">'
        f"&#128200; language mix &#183; {total} repos</text>"
    )
    bar_x, bar_max = 190, 520
    for i, (lang, n) in enumerate(ordered):
        y = 50 + i * 44
        share = n / total
        bw = max(6.0, bar_max * share)
        color = palette[i % len(palette)]
        s += (
            f'<text x="24" y="{y + 20}" font-size="13" fill="{TXT}">{html.escape(lang)}</text>'
        )
        s += (
            f'<rect x="{bar_x}" y="{y}" width="{bar_max}" height="26" rx="13" fill="#0b0f1a" stroke="{BORDER}"/>'
            f'<rect x="{bar_x}" y="{y}" width="{bw:.1f}" height="26" rx="13" fill="{color}">'
            f'<animate attributeName="width" from="0" to="{bw:.1f}" dur="1.1s" '
            f'begin="{i * 0.12}s" fill="freeze"/></rect>'
            f'<text x="{bar_x + 12}" y="{y + 18}" font-size="12" font-weight="700" fill="#0d1117">'
            f"{n}</text>"
        )
        s += (
            f'<text x="{bar_x + bar_max + 14}" y="{y + 18}" font-size="12" fill="{MUT}">'
            f"{round(share * 100)}%</text>"
        )
    s += "</svg>"
    return s


def pypi_downloads():
    """PyPI download stats, including a real total.

    PyPI's own JSON API returns ``downloads: -1`` (stats disabled) and
    shields.io's ``pypi/dt`` badge therefore renders "404: badge not found".
    pypistats.org still publishes per-day figures, so we sum them ourselves
    to produce an honest total for the retention window it covers.
    """
    from datetime import date, timedelta

    import requests

    pkg = "droidseal"
    daily = {}
    try:
        r = requests.get(
            f"https://pypistats.org/api/packages/{pkg}/overall?mirrors=false",
            timeout=30,
        )
        if r.status_code == 200:
            for row in r.json().get("data", []):
                daily[row["date"]] = int(row.get("downloads") or 0)
    except Exception:
        daily = {}

    w, h = 800, 250
    s = open_svg(w, h)
    s += card(w, h)
    s += (
        f'<text x="24" y="34" font-size="15" font-weight="700" fill="{MUT}">'
        f"&#128230; pypi downloads &#183; {html.escape(pkg)}</text>"
    )

    if not daily:
        s += (
            f'<text x="24" y="110" font-size="14" fill="{MUT}">'
            f"download stats unavailable right now</text>"
        )
        s += "</svg>"
        return s

    today = date.today()
    days = 60
    start = today - timedelta(days=days - 1)
    series = [daily.get((start + timedelta(days=i)).isoformat(), 0) for i in range(days)]

    total = sum(daily.values())
    total30 = sum(
        v for d, v in daily.items()
        if d >= (today - timedelta(days=29)).isoformat()
    )
    peak_day, peak_val = max(daily.items(), key=lambda kv: kv[1]) if daily else ("-", 0)

    # big total + sub-label
    s += (
        f'<text x="24" y="100" font-size="48" font-weight="700" fill="{BLUE}">'
        f"{total:,}"
        f'<animate attributeName="opacity" values="0.55;1;0.55" dur="3.2s" repeatCount="indefinite"/>'
        f"</text>"
    )
    s += (
        f'<text x="24" y="124" font-size="13" fill="{MUT}">total downloads '
        f"(pypistats retention window)</text>"
    )

    # right-hand chips
    chips = [
        (f"{total30:,}", "last 30 days", TEAL),
        (f"{peak_val:,}", f"peak day", YELLOW),
        (f"{len(daily)}", "days tracked", PURPLE),
    ]
    for i, (val, label, color) in enumerate(chips):
        cx = 470 + i * 108
        s += (
            f'<g transform="translate({cx},58)">'
            f'<rect width="96" height="52" rx="10" fill="#0b0f1a" stroke="{BORDER}"/>'
            f'<text x="12" y="24" font-size="19" font-weight="700" fill="{color}">{val}</text>'
            f'<text x="12" y="42" font-size="10" fill="{MUT}">{label}</text>'
            f"</g>"
        )

    # 60-day bar chart
    x0, x1 = 24, 776
    y_top, y_base = 152, 228
    plot_w = x1 - x0
    slot = plot_w / days
    bar_w = slot * 0.66
    maxv = max(series) or 1

    s += (
        f'<line x1="{x0}" y1="{y_base}" x2="{x1}" y2="{y_base}" '
        f'stroke="{BORDER}" stroke-width="1"/>'
    )
    for i, v in enumerate(series):
        bh = (v / maxv) * (y_base - y_top) if v else 0
        x = x0 + i * slot
        y = y_base - bh
        color = YELLOW if v == maxv and v > 0 else BLUE
        s += (
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{max(bh, 0.6):.1f}" '
            f'rx="1.5" fill="{color}" opacity="0.9">'
            f'<animate attributeName="height" from="0" to="{max(bh, 0.6):.1f}" '
            f'dur="0.7s" begin="{i * 0.012:.3f}s" fill="freeze"/>'
            f'<animate attributeName="y" from="{y_base}" to="{y:.1f}" '
            f'dur="0.7s" begin="{i * 0.012:.3f}s" fill="freeze"/>'
            f"</rect>"
        )
    s += (
        f'<text x="{x0}" y="{y_base + 18}" font-size="10" fill="{MUT}">'
        f"{start.isoformat()}</text>"
    )
    s += (
        f'<text x="{x1}" y="{y_base + 18}" text-anchor="end" font-size="10" fill="{MUT}">'
        f"today</text>"
    )
    s += "</svg>"
    return s


def main():
    write("aurora.svg", aurora())
    write("skill-radar.svg", skill_radar())
    write("ticker.svg", ticker())
    write("pulse.svg", pulse())
    write("spotlight.svg", spotlight())
    write("heatmap.svg", heatmap())
    write("stats.svg", stats_cards())
    write("top-languages.svg", top_langs())
    write("pypi-downloads.svg", pypi_downloads())
    print("done.")


if __name__ == "__main__":
    main()
