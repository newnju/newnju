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
def _token():
    """Resolve a GitHub token: env first, then the local git credential store.

    GitHub's GraphQL API rejects unauthenticated requests, so unlike the REST
    helpers this genuinely needs a token. In GitHub Actions GITHUB_TOKEN is
    already exported; locally we fall back to whatever `git credential fill`
    returns for github.com.
    """
    tok = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if tok:
        return tok
    try:
        import subprocess

        out = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True, text=True, timeout=20,
        ).stdout
        for line in out.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1]
    except Exception:
        pass
    return None


def _graphql(query):
    """POST a GraphQL query, tolerating network/auth failure."""
    import requests

    token = _token()
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.post(
            "https://api.github.com/graphql",
            headers=headers,
            json={"query": query},
            timeout=40,
        )
        if r.status_code == 200:
            body = r.json()
            if not body.get("errors"):
                return body.get("data")
    except Exception:
        pass
    return None


def heatmap():
    """GitHub-style contribution heatmap (53 weeks) from real contribution data.

    The public events API only covers ~90 days and counts *events*, not
    contributions, so it produced a sparse, misleading grid. The GraphQL
    contributionsCollection returns the same calendar GitHub itself renders:
    a full 53-week year with per-day contributionCount.
    """
    from datetime import date, timedelta

    counts = {}
    total = 0

    data = _graphql(
        """
        query {
          user(login: "%s") {
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays { date contributionCount }
                }
              }
            }
          }
        }
        """
        % USERNAME
    )
    cal = ((data or {}).get("user") or {}).get("contributionsCollection", {}).get(
        "contributionCalendar"
    ) or {}

    weeks_data = cal.get("weeks") or []
    for wk in weeks_data:
        for day in wk.get("contributionDays", []):
            counts[day["date"]] = day.get("contributionCount", 0)
    total = cal.get("totalContributions") or sum(counts.values())

    # Fallback: synthesise a 53-week grid of empty days so the widget keeps a
    # sane fixed size instead of collapsing to a 1-column sliver (which would
    # make `step` enormous and blow the canvas up to thousands of px tall).
    if not weeks_data:
        from datetime import date as _d, timedelta as _td

        today = _d.today()
        start = today - _td(weeks=52)
        start = start - _td(days=start.weekday())
        weeks_data = [
            {
                "contributionDays": [
                    {
                        "date": (start + _td(weeks=w, days=dd)).isoformat(),
                        "contributionCount": 0,
                    }
                    for dd in range(7)
                    if (start + _td(weeks=w, days=dd)) <= today
                ]
            }
            for w in range(53)
        ]
        counts = {}
        total = 0

    # ---- geometry: size the grid to a fixed 800px width ----
    left_gutter = 34
    right_pad = 6
    weeks = max(len(weeks_data), 1)
    avail = 800 - left_gutter - right_pad
    step = avail / weeks
    cell = max(6.0, step - 3)
    top = 56
    row_step = step
    grid_h = 7 * row_step
    h = int(top + grid_h + 40)

    s = open_svg(800, h)
    s += card(800, h)
    s += (
        f'<text x="16" y="24" font-size="12" font-weight="700" fill="{MUT}">'
        f"{total:,} contributions in the last year</text>"
    )

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    last_month = -1

    def level_color(n):
        if n <= 0:
            return "#161b22"
        if n <= 2:
            return "#0e4429"
        if n <= 5:
            return "#006d32"
        if n <= 9:
            return "#26a641"
        return "#39d353"

    for wi, wk in enumerate(weeks_data):
        days = wk.get("contributionDays", [])
        if not days:
            continue
        col_x = left_gutter + wi * step
        first = date.fromisoformat(days[0]["date"])
        if first.month != last_month:
            s += (
                f'<text x="{col_x:.1f}" y="45" font-size="9" fill="{MUT}">'
                f"{month_names[first.month - 1]}</text>"
            )
            last_month = first.month
        for di, day in enumerate(days):
            n = day.get("contributionCount", 0)
            y = top + di * row_step
            s += (
                f'<rect x="{col_x:.1f}" y="{y:.1f}" width="{cell:.1f}" '
                f'height="{cell:.1f}" rx="2" fill="{level_color(n)}">'
                f"<title>{day['date']}: {n} contribution"
                f"{'' if n == 1 else 's'}</title>"
                f"</rect>"
            )

    # legend
    lx = 800 - 16 - (5 * 12 + 46)
    ly = h - 16
    s += (
        f'<text x="{lx - 8:.1f}" y="{ly + 8}" text-anchor="end" '
        f'font-size="9" fill="{MUT}">Less</text>'
    )
    for i in range(5):
        s += (
            f'<rect x="{lx + i * 12:.1f}" y="{ly}" width="9" height="9" rx="2" '
            f'fill="{level_color([0, 1, 3, 6, 10][i])}"/>'
        )
    s += (
        f'<text x="{lx + 5 * 12 + 4:.1f}" y="{ly + 8}" font-size="9" '
        f'fill="{MUT}">More</text>'
    )

    s += "</svg>"
    return s


def _api(path):
    """Fetch JSON from the GitHub API, tolerating network failure."""
    import requests

    headers = {"Accept": "application/vnd.github+json"}
    token = _token()
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
    """Live account statistics as animated cards.

    Layout note: a child <animateTransform attributeName="transform"> *replaces*
    its element's transform attribute rather than composing with it. The
    previous version put the bob animation directly on the positioned <g>, so
    every card was yanked back to translate(0,0) and all six stacked on the
    same spot. The position now lives on an outer <g> and only an inner <g>
    animates.
    """
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
        ("Repos", len(repos), CYAN, "&#128194;"),
        ("Stars", stars, YELLOW, "&#11088;"),
        ("Forks", forks, PURPLE, "&#127860;"),
        ("Followers", profile.get("followers", 0), GREEN, "&#128101;"),
        ("Following", profile.get("following", 0), TEAL, "&#128100;"),
        ("Years", years, ORANGE, "&#128197;"),
    ]

    w, h = 800, 230
    pad = 24
    gap_x, gap_y = 16, 14
    cw = (w - 2 * pad - 2 * gap_x) // 3
    ch = 73
    top = 50

    s = open_svg(w, h)
    s += card(w, h)
    s += (
        f'<text x="{pad}" y="32" font-size="15" font-weight="700" fill="{MUT}">'
        f"&#128200; account stats</text>"
    )
    s += (
        f'<text x="{w - pad}" y="32" text-anchor="end" font-size="11" '
        f'fill="{MUT}">@{html.escape(USERNAME)}</text>'
    )

    for i, (label, value, color, icon) in enumerate(cells):
        col = i % 3
        row = i // 3
        x = pad + col * (cw + gap_x)
        y = top + row * (ch + gap_y)

        # outer g = fixed position (never animated)
        s += f'<g transform="translate({x},{y})">'
        s += (
            f'<rect width="{cw}" height="{ch}" rx="12" fill="#0b0f1a" '
            f'stroke="{BORDER}"/>'
        )
        # colour accent on the left edge
        s += f'<rect x="0" y="10" width="3" height="{ch - 20}" rx="1.5" fill="{color}"/>'

        # inner g = the only thing that animates
        s += (
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 -3;0 0" dur="3.6s" begin="{i * 0.15:.2f}s" '
            f'repeatCount="indefinite"/>'
        )
        s += (
            f'<text x="16" y="24" font-size="11" fill="{MUT}">{icon} {label}</text>'
        )
        # count-up feel: digits fade/slide in once, then hold
        s += (
            f'<text x="16" y="58" font-size="27" font-weight="700" fill="{color}">'
            f"{value:,}"
            f'<animate attributeName="opacity" values="0;1" dur="0.5s" '
            f'begin="{0.1 + i * 0.08:.2f}s" fill="freeze"/>'
            f"</text>"
        )
        # pulsing status dot, top-right of the card
        s += (
            f'<circle cx="{cw - 16}" cy="18" r="3" fill="{color}">'
            f'<animate attributeName="opacity" values="1;0.25;1" dur="2.4s" '
            f'begin="{i * 0.2:.2f}s" repeatCount="indefinite"/>'
            f"</circle>"
        )
        s += "</g></g>"

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


def package_downloads():
    """Total downloads for npm (left) and PyPI (right), side by side.

    Accuracy notes, because both sources have traps:

    * PyPI's own JSON API reports ``downloads: -1`` (stats disabled), and
      shields.io's ``pypi/dt`` badge is therefore permanently "404: badge not
      found". pypistats.org publishes per-day figures for two categories:
      ``without_mirrors`` (PyPI's official metric, the one shields.io uses for
      ``pypi/dm``) and ``with_mirrors`` (adds unofficial mirrors). We use
      ``without_mirrors`` and label it as such.
    * pypistats only retains a limited window, so a raw sum is a *window* total
      unless the window already covers the package's whole life. We therefore
      fetch PyPI's first upload time and only call the sum a lifetime total when
      the data starts at or before that date; otherwise we say so explicitly.
    * npm's ``downloads/range`` endpoint 404s for this package, but
      ``downloads/point/last-year`` works. Since npm counts from the package's
      first publish (2026-08-15) and the last-year window starts 2025-11-15,
      that value is the true lifetime total. We assert that containment rather
      than assuming it.
    """
    from datetime import date, timedelta

    import requests

    pkg = "droidseal"
    npm_total = None
    npm_note = "npm registry"
    pypi_daily = {}
    pypi_lifetime = None
    pypi_note = ""

    # ---- npm ----
    try:
        reg = requests.get(f"https://registry.npmjs.org/{pkg}", timeout=30)
        first_publish = None
        if reg.status_code == 200:
            times = reg.json().get("time", {})
            stamps = sorted(
                v for k, v in times.items() if k not in ("created", "modified")
            )
            if stamps:
                first_publish = stamps[0][:10]
        pt = requests.get(
            f"https://api.npmjs.org/downloads/point/last-year/{pkg}", timeout=30
        )
        if pt.status_code == 200:
            d = pt.json()
            npm_total = int(d.get("downloads") or 0)
            # only claim "lifetime" when the window truly covers first publish
            if first_publish and d.get("start") and d["start"] <= first_publish:
                npm_note = f"lifetime (since {first_publish})"
            else:
                npm_note = f"last 12 months (from {d.get('start')})"
    except Exception:
        npm_total = None

    # ---- PyPI ----
    try:
        pj = requests.get(f"https://pypi.org/pypi/{pkg}/json", timeout=30)
        first_upload = None
        if pj.status_code == 200:
            rel = pj.json().get("releases", {})
            stamps = sorted(
                f["upload_time"]
                for files in rel.values()
                for f in files
                if f.get("upload_time")
            )
            if stamps:
                first_upload = stamps[0][:10]

        ps = requests.get(
            f"https://pypistats.org/api/packages/{pkg}/overall?mirrors=false",
            timeout=30,
        )
        if ps.status_code == 200:
            for row in ps.json().get("data", []):
                pypi_daily[row["date"]] = int(row.get("downloads") or 0)
            if pypi_daily:
                earliest = min(pypi_daily)
                if first_upload and earliest <= first_upload:
                    pypi_lifetime = sum(pypi_daily.values())
                    pypi_note = f"lifetime (since {first_upload}), mirrors excluded"
                else:
                    pypi_lifetime = sum(pypi_daily.values())
                    pypi_note = (
                        f"partial: data starts {earliest}, "
                        f"package from {first_upload}"
                    )
    except Exception:
        pypi_lifetime = None

    # ---- render ----
    w, h = 800, 300
    s = open_svg(w, h)
    s += card(w, h)
    s += (
        f'<text x="24" y="32" font-size="15" font-weight="700" fill="{MUT}">'
        f"&#128230; total downloads &#183; {html.escape(pkg)}</text>"
    )

    # divider between the two columns
    s += (
        f'<line x1="400" y1="50" x2="400" y2="284" '
        f'stroke="{BORDER}" stroke-width="1" stroke-dasharray="4 4"/>'
    )

    columns = [
        ("npm", npm_total, "npm downloads", "CB3837", npm_note, 24),
        ("pypi", pypi_lifetime, "pypi downloads", "3775A9", pypi_note, 424),
    ]

    for label, total, sub, color, note, x in columns:
        s += (
            f'<text x="{x}" y="70" font-size="13" font-weight="700" '
            f'fill="{color}">{label.upper()}</text>'
        )
        if total is None:
            s += (
                f'<text x="{x}" y="126" font-size="34" font-weight="700" fill="{MUT}">'
                f"unavailable</text>"
            )
            continue

        s += (
            f'<text x="{x}" y="130" font-size="46" font-weight="700" fill="{color}">'
            f"{total:,}"
            f'<animate attributeName="opacity" values="0.6;1;0.6" dur="3.4s" repeatCount="indefinite"/>'
            f"</text>"
        )
        s += (
            f'<text x="{x}" y="152" font-size="12" fill="{MUT}">{sub}</text>'
        )

        # note, wrapped to two lines of ~34 chars
        words = note.split()
        line1, line2 = "", ""
        for wd in words:
            if len(line1) + len(wd) + 1 <= 34:
                line1 = (line1 + " " + wd).strip()
            else:
                line2 = (line2 + " " + wd).strip()
        s += (
            f'<text x="{x}" y="172" font-size="10" fill="{MUT}">'
            f"{html.escape(line1)}</text>"
        )
        if line2:
            s += (
                f'<text x="{x}" y="186" font-size="10" fill="{MUT}">'
                f"{html.escape(line2)}</text>"
            )

    # ---- combined bar: npm + pypi, each bar scaled to its own max ----
    s += (
        f'<text x="24" y="216" font-size="11" font-weight="700" fill="{MUT}">'
        f"last 60 days</text>"
    )
    today = date.today()
    days = 60
    start = today - timedelta(days=days - 1)
    x0, x1 = 24, 776
    y_top, y_base = 228, 280
    plot_w = x1 - x0
    slot = plot_w / days
    bar_w = slot * 0.62

    # npm has no per-day data available (range endpoint 404s), so draw the
    # pypi daily series across the full width and state that clearly.
    if pypi_daily:
        series = [
            pypi_daily.get((start + timedelta(days=i)).isoformat(), 0)
            for i in range(days)
        ]
        maxv = max(series) or 1
        s += (
            f'<line x1="{x0}" y1="{y_base}" x2="{x1}" y2="{y_base}" '
            f'stroke="{BORDER}" stroke-width="1"/>'
        )
        for i, v in enumerate(series):
            bh = (v / maxv) * (y_base - y_top) if v else 0
            bx = x0 + i * slot
            by = y_base - bh
            s += (
                f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" '
                f'height="{max(bh, 0.6):.1f}" rx="1.5" fill="#3775A9" opacity="0.92">'
                f'<animate attributeName="height" from="0" to="{max(bh, 0.6):.1f}" '
                f'dur="0.7s" begin="{i * 0.011:.3f}s" fill="freeze"/>'
                f'<animate attributeName="y" from="{y_base}" to="{by:.1f}" '
                f'dur="0.7s" begin="{i * 0.011:.3f}s" fill="freeze"/>'
                f"</rect>"
            )
        s += (
            f'<text x="{x0}" y="{y_base + 14}" font-size="10" fill="{MUT}">'
            f"{start.isoformat()}</text>"
        )
        s += (
            f'<text x="{x1}" y="{y_base + 14}" text-anchor="end" font-size="10" '
            f'fill="{MUT}">today</text>'
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
    write("package-downloads.svg", package_downloads())
    print("done.")


if __name__ == "__main__":
    main()
