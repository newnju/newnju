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

# Registry brand hues, expressed with the profile's own palette tokens so the
# panel sits in the same colour family as every other widget.
# NOTE: these must carry the leading '#' — a bare "CB3837" is an invalid SVG
# paint and silently renders BLACK, which is what made the totals unreadable.
NPM_C = RED      # npm's brand is red; matches the profile's red token
PYPI_C = BLUE    # PyPI's brand is blue; matches the profile's blue token
NPM_DEEP = "#B8402F"
PYPI_DEEP = "#2F6B99"

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
    position now lives on an outer <g> and only an inner <g> animates.

    Visual note: each card is a small glass tile — vertical gradient surface,
    a tinted glow in the accent colour, an icon chip, and an accent underline
    that draws itself in. A single sheen sweeps the whole panel so the grid
    reads as one surface rather than six loose boxes.
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
        ("Repos", len(repos), CYAN, "non-fork"),
        ("Stars", stars, YELLOW, "earned"),
        ("Forks", forks, PURPLE, "times forked"),
        ("Followers", profile.get("followers", 0), GREEN, "people"),
        ("Following", profile.get("following", 0), TEAL, "people"),
        ("Years", years, ORANGE, "on GitHub"),
    ]

    # A dashboard row rather than six boxed tiles. The previous version gave
    # every number the same weight inside a 241x84 card with a 27px figure,
    # so each tile was two-thirds empty and nothing read as the headline.
    # Here the numbers are the interface: 40px, tabular, one accent each,
    # separated by hairlines, with the proportions stated underneath.
    w, h = 800, 268
    pad = 30
    col_w = (w - 2 * pad) / len(cells)
    rule_y = 58
    label_y = 96
    num_y = 150
    uline_y = 162
    sub_y = 182
    bar_y = 210

    s = open_svg(w, h)
    s += card(w, h)
    s += (
        "<defs>"
        '<linearGradient id="stSheen" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.05"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
        "</linearGradient>"
        "</defs>"
    )

    # header
    s += (
        f'<text x="{pad}" y="36" font-size="15" font-weight="700" fill="{TXT}" '
        f'letter-spacing="0.3">&#128200; account stats</text>'
    )
    s += (
        f'<text x="{w - pad}" y="36" text-anchor="end" font-size="10.5" '
        f'fill="{MUT}">@{html.escape(USERNAME)} &#183; since {created or "?"}'
        f'</text>'
    )
    s += (
        f'<rect x="{pad}" y="{rule_y}" width="{w - 2 * pad}" height="1" '
        f'fill="{BORDER}" opacity="0.8"/>'
    )

    for i, (label, value, color, sub) in enumerate(cells):
        x = pad + i * col_w
        # hairline separator between columns (not after the last one)
        if i:
            s += (
                f'<line x1="{x:.1f}" y1="{rule_y + 14}" x2="{x:.1f}" '
                f'y2="{sub_y - 10}" stroke="{BORDER}" stroke-width="1" '
                f'opacity="0.55"/>'
            )

        s += f'<g transform="translate({x:.1f},0)">'
        # label
        s += (
            f'<text x="0" y="{label_y}" font-size="9.5" fill="{MUT}" '
            f'letter-spacing="1.3">{label.upper()}</text>'
        )
        # the number - the focal point of the panel
        s += (
            f'<text x="-1" y="{num_y}" font-size="40" font-weight="700" '
            f'fill="{color}" style="font-variant-numeric:tabular-nums">'
            f"{value:,}"
            f'<animate attributeName="opacity" values="0;1" dur="0.45s" '
            f'begin="{0.08 + i * 0.07:.2f}s" fill="freeze"/></text>'
        )
        # accent rule that draws itself in
        s += (
            f'<rect x="0" y="{uline_y}" width="0" height="2.5" rx="1.25" '
            f'fill="{color}" opacity="0.9">'
            f'<animate attributeName="width" from="0" to="{col_w - 26:.1f}" '
            f'dur="0.8s" begin="{0.2 + i * 0.08:.2f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.2 0.8 0.3 1" keyTimes="0;1"/>'
            f"</rect>"
        )
        # what the number actually counts
        s += (
            f'<text x="0" y="{sub_y}" font-size="9" fill="{MUT}" opacity="0.8">'
            f'{html.escape(sub)}</text>'
        )
        s += "</g>"

    # ---- composition: own repos vs forks --------------------------------
    # _own_repos() strips forks, so the account-wide total comes from the
    # profile and the fork share is the remainder.
    total_repos = int(profile.get("public_repos") or len(repos)) or len(repos)
    own_n = len(repos)
    fork_n = max(0, total_repos - own_n)
    if total_repos:
        own_pct = own_n / total_repos * 100
        fork_pct = fork_n / total_repos * 100
        s += (
            f'<rect x="{pad}" y="{bar_y}" width="{w - 2 * pad}" height="7" rx="3.5" '
            f'fill="#0b0f1a"/>'
        )
        # fork share first (the bulk), then the own share on top of it
        s += (
            f'<rect x="{pad}" y="{bar_y}" width="0" height="7" rx="3.5" '
            f'fill="{PURPLE}" opacity="0.5">'
            f'<animate attributeName="width" from="0" '
            f'to="{w - 2 * pad:.1f}" dur="0.9s" begin="0.3s" fill="freeze" '
            f'calcMode="spline" keySplines="0.2 0.8 0.3 1" keyTimes="0;1"/>'
            f'</rect>'
        )
        s += (
            f'<rect x="{pad}" y="{bar_y}" width="0" height="7" rx="3.5" '
            f'fill="{CYAN}">'
            f'<animate attributeName="width" from="0" '
            f'to="{own_pct / 100 * (w - 2 * pad):.1f}" '
            f'dur="0.9s" begin="0.45s" fill="freeze" '
            f'calcMode="spline" keySplines="0.2 0.8 0.3 1" keyTimes="0;1"/>'
            f'</rect>'
        )
        s += (
            f'<text x="{pad}" y="{bar_y + 22}" font-size="9" fill="{MUT}">'
            f'<tspan fill="{CYAN}" font-weight="700">{own_n}</tspan> own'
            f'</text>'
            f'<text x="{w - pad}" y="{bar_y + 22}" text-anchor="end" '
            f'font-size="9" fill="{MUT}">'
            f'{fork_n} forked &#183; {total_repos} total</text>'
        )

    # one sheen sweeping the whole panel
    s += (
        f'<g clip-path="inset(0 round 16px)" opacity="0.9">'
        f'<rect x="-260" y="0" width="220" height="{h}" fill="url(#stSheen)" '
        f'transform="skewX(-18)">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0;1180 0;1180 0" keyTimes="0;0.55;1" dur="9s" '
        f'repeatCount="indefinite" additive="sum"/>'
        f'</rect></g>'
    )

    s += "</svg>"
    return s


def top_langs():
    """Language mix: a donut summary plus gradient bars with real share.

    The previous version was a plain list of flat rectangles, which read as a
    progress-bar form rather than a data graphic. Now the composition is stated
    twice — once as a proportional ring, once as ranked bars — so the eye gets
    both the whole and the parts.
    """
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

    top = 56
    row_h = 40
    body_h = len(ordered) * row_h
    w, h = 800, top + body_h + 56
    s = open_svg(w, h)
    s += card(w, h)
    s += (
        "<defs>"
        '<linearGradient id="tlSheen" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.16"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
        "</linearGradient>"
        "</defs>"
    )

    # header
    s += (
        f'<text x="24" y="32" font-size="15" font-weight="700" fill="{TXT}" '
        f'letter-spacing="0.3">&#128200; language mix</text>'
    )
    s += (
        f'<text x="{w - 24}" y="32" text-anchor="end" font-size="10.5" '
        f'fill="{MUT}">{total} repositories &#183; primary language</text>'
    )
    s += f'<rect x="24" y="42" width="{w - 48}" height="1" fill="{BORDER}" opacity="0.7"/>'

    # ---- donut summary ---------------------------------------------------
    dcx, dcy, dr = 128, top + body_h / 2 + 6, 62
    sw = 19
    circ = 2 * math.pi * dr
    acc = 0.0
    # track
    s += (
        f'<circle cx="{dcx}" cy="{dcy}" r="{dr}" fill="none" '
        f'stroke="#0b0f1a" stroke-width="{sw}"/>'
    )
    for i, (lang, n) in enumerate(ordered):
        frac = n / total
        dash = frac * circ
        gap = circ - dash
        rot = -90 + acc * 360
        s += (
            f'<circle cx="{dcx}" cy="{dcy}" r="{dr}" fill="none" '
            f'stroke="{palette[i % len(palette)]}" stroke-width="{sw}" '
            f'stroke-dasharray="{dash:.2f} {gap:.2f}" '
            f'transform="rotate({rot:.2f} {dcx} {dcy})" opacity="0.92">'
            f'<animate attributeName="stroke-dasharray" '
            f'from="0 {circ:.2f}" to="{dash:.2f} {gap:.2f}" '
            f'dur="1.0s" begin="{i * 0.11:.2f}s" fill="freeze"/>'
            f"</circle>"
        )
        acc += frac
    # centre label
    s += (
        f'<text x="{dcx}" y="{dcy - 2}" text-anchor="middle" font-size="30" '
        f'font-weight="700" fill="{TXT}">{total}'
        f'<animate attributeName="opacity" values="0;1" dur="0.6s" '
        f'begin="0.15s" fill="freeze"/></text>'
    )
    s += (
        f'<text x="{dcx}" y="{dcy + 16}" text-anchor="middle" font-size="9.5" '
        f'fill="{MUT}" letter-spacing="1">REPOSITORIES</text>'
    )

    # ---- ranked bars -----------------------------------------------------
    bar_x = 248
    bar_max = 470
    for i, (lang, n) in enumerate(ordered):
        y = top + 10 + i * row_h
        share = n / total
        bw = max(8.0, bar_max * share)
        color = palette[i % len(palette)]
        # label
        s += (
            f'<text x="{bar_x - 14}" y="{y + 17}" text-anchor="end" '
            f'font-size="12.5" fill="{TXT}">{html.escape(lang)}</text>'
        )
        # track
        s += (
            f'<rect x="{bar_x}" y="{y}" width="{bar_max}" height="22" rx="11" '
            f'fill="#0b0f1a" stroke="{BORDER}" stroke-width="0.8"/>'
        )
        # fill with a vertical gradient of its own colour
        s += (
            f'<g clip-path="inset(0 round 11px)">'
            f'<rect x="{bar_x}" y="{y}" width="0" height="22" rx="11" fill="{color}" '
            f'opacity="0.92">'
            f'<animate attributeName="width" from="0" to="{bw:.1f}" '
            f'dur="1.1s" begin="{i * 0.12:.2f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.2 0.8 0.3 1" keyTimes="0;1"/>'
            f"</rect>"
            f'<rect x="{bar_x}" y="{y}" width="{bw:.1f}" height="10" rx="5" '
            f'fill="#ffffff" opacity="0.14">'
            f'<animate attributeName="width" from="0" to="{bw:.1f}" '
            f'dur="1.1s" begin="{i * 0.12:.2f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.2 0.8 0.3 1" keyTimes="0;1"/>'
            f"</rect>"
            f"</g>"
        )
        # count inside the bar
        if bw > 40:
            s += (
                f'<text x="{bar_x + 12}" y="{y + 15.5}" font-size="11" '
                f'font-weight="700" fill="#0d1117" opacity="0">{n}'
                f'<animate attributeName="opacity" values="0;1" dur="0.4s" '
                f'begin="{0.6 + i * 0.12:.2f}s" fill="freeze"/></text>'
            )
        # share at the right
        s += (
            f'<text x="{bar_x + bar_max + 12}" y="{y + 15.5}" font-size="11.5" '
            f'fill="{MUT}">{share * 100:.0f}%</text>'
        )

    # ---- stacked composition strip --------------------------------------
    sy = h - 32
    s += f'<rect x="24" y="{sy}" width="{w - 48}" height="7" rx="3.5" fill="#0b0f1a"/>'
    acc = 0.0
    for i, (lang, n) in enumerate(ordered):
        frac = n / total
        x = 24 + acc * (w - 48)
        wd = frac * (w - 48)
        s += (
            f'<rect x="{x:.2f}" y="{sy}" width="0" height="7" rx="3.5" '
            f'fill="{palette[i % len(palette)]}">'
            f'<animate attributeName="width" from="0" to="{wd:.2f}" '
            f'dur="0.9s" begin="{0.3 + i * 0.1:.2f}s" fill="freeze"/></rect>'
        )
        acc += frac
    s += (
        f'<text x="24" y="{sy + 20}" font-size="8.5" fill="{MUT}" '
        f'opacity="0.7">every repository, one stripe each</text>'
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

    # ---- render ----------------------------------------------------------
    # The two totals are the point of this panel, so each gets a proper
    # readout: the number, its share of the combined total, a 7-day trend
    # delta where per-day data exists, and a mini share bar. The combined
    # figure sits in the header so the panel answers "how much in total" first.
    w, h = 800, 372
    s = open_svg(w, h)
    s += card(w, h)
    s += (
        "<defs>"
        '<linearGradient id="pdPyBar" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{PYPI_C}" stop-opacity="0.95"/>'
        f'<stop offset="1" stop-color="{PYPI_C}" stop-opacity="0.28"/>'
        "</linearGradient>"
        '<linearGradient id="pdNpmChip" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{NPM_C}" stop-opacity="0.22"/>'
        f'<stop offset="1" stop-color="{NPM_C}" stop-opacity="0"/>'
        "</linearGradient>"
        '<linearGradient id="pdPyChip" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{PYPI_C}" stop-opacity="0.22"/>'
        f'<stop offset="1" stop-color="{PYPI_C}" stop-opacity="0"/>'
        "</linearGradient>"
        "</defs>"
    )
    # ---- header with the combined total ----------------------------------
    known = [v for v in (npm_total, pypi_lifetime) if v]
    combined = sum(known) if len(known) == 2 else None

    s += (
        f'<text x="24" y="32" font-size="15" font-weight="700" fill="{TXT}" '
        f'letter-spacing="0.3">&#128230; total downloads</text>'
    )
    s += (
        f'<text x="{24 + 152:.0f}" y="32" font-size="10.5" fill="{MUT}" '
        f'font-family="{MONO}">&#183; {html.escape(pkg)}</text>'
    )
    if combined is not None:
        s += (
            f'<text x="{w - 24}" y="32" text-anchor="end" font-size="10.5" '
            f'fill="{MUT}">combined</text>'
            f'<text x="{w - 24}" y="52" text-anchor="end" font-size="20" '
            f'font-weight="700" fill="{TXT}" '
            f'style="font-variant-numeric:tabular-nums">{combined:,}'
            f'<animate attributeName="opacity" values="0;1" dur="0.5s" '
            f'begin="0.1s" fill="freeze"/></text>'
        )
    s += f'<rect x="24" y="62" width="{w - 48}" height="1" fill="{BORDER}" opacity="0.7"/>'

    # divider between the two columns
    s += (
        f'<line x1="400" y1="76" x2="400" y2="246" '
        f'stroke="{BORDER}" stroke-width="1" stroke-dasharray="4 4" opacity="0.8"/>'
    )

    # ---- 7-day trend for PyPI (npm exposes no daily series) --------------
    today = date.today()
    last7 = sum(
        pypi_daily.get((today - timedelta(days=k)).isoformat(), 0) for k in range(7)
    )
    prev7 = sum(
        pypi_daily.get((today - timedelta(days=k)).isoformat(), 0)
        for k in range(7, 14)
    )
    trend = None
    if prev7:
        trend = (last7 - prev7) / prev7 * 100

    columns = [
        ("npm", npm_total, "npm downloads", NPM_C, npm_note, 24, "pdNpmChip",
         None),
        ("pypi", pypi_lifetime, "pypi downloads", PYPI_C, pypi_note, 424,
         "pdPyChip", (last7, trend)),
    ]

    for label, total, sub, color, note, x, chip, extra in columns:
        # soft accent chip behind each column so the panel reads as two
        # tinted halves rather than plain text on a flat card
        s += (
            f'<rect x="{x - 14}" y="72" width="352" height="176" rx="12" '
            f'fill="url(#{chip})"/>'
        )
        s += (
            f'<circle cx="{x + 5}" cy="92" r="3.5" fill="{color}"/>'
            f'<text x="{x + 16}" y="96" font-size="12" font-weight="700" '
            f'fill="{color}" letter-spacing="0.6">{label.upper()}</text>'
        )
        if total is None:
            s += (
                f'<text x="{x}" y="146" font-size="28" font-weight="700" fill="{MUT}">'
                f"unavailable</text>"
            )
            continue

        # the number
        s += (
            f'<text x="{x}" y="152" font-size="44" font-weight="700" fill="{color}" '
            f'style="font-variant-numeric:tabular-nums">{total:,}'
            f'<animate attributeName="opacity" values="0;1" dur="0.5s" '
            f'begin="0.15s" fill="freeze"/></text>'
        )
        s += f'<text x="{x}" y="172" font-size="11.5" fill="{MUT}">{sub}</text>'

        # share of the combined total
        if combined:
            pct = total / combined * 100
            s += (
                f'<text x="{x}" y="192" font-size="10" fill="{MUT}">'
                f'share of combined</text>'
                f'<text x="{x + 96}" y="192" font-size="11" font-weight="700" '
                f'fill="{color}">{pct:.1f}%</text>'
            )
            track_w = 300
            s += (
                f'<rect x="{x}" y="198" width="{track_w}" height="6" rx="3" '
                f'fill="#0b0f1a"/>'
                f'<rect x="{x}" y="198" width="0" height="6" rx="3" fill="{color}">'
                f'<animate attributeName="width" from="0" '
                f'to="{track_w * pct / 100:.1f}" '
                f'dur="0.9s" begin="0.3s" fill="freeze" calcMode="spline" '
                f'keySplines="0.2 0.8 0.3 1" keyTimes="0;1"/></rect>'
            )

        # 7-day trend, where the source provides one
        if extra and extra[0]:
            l7, tr = extra
            if tr is None:
                txt, tcol = f"last 7d: {l7:,}", MUT
            else:
                txt = f"last 7d: {l7:,}  ({tr:+.0f}%)"
                tcol = GREEN if tr >= 0 else RED
            s += (
                f'<text x="{x}" y="222" font-size="10" fill="{tcol}">'
                f"{html.escape(txt)}</text>"
            )

        # note, wrapped to two lines
        words = note.split()
        line1, line2 = "", ""
        for wd in words:
            if len(line1) + len(wd) + 1 <= 36:
                line1 = (line1 + " " + wd).strip()
            else:
                line2 = (line2 + " " + wd).strip()
        s += (
            f'<text x="{x}" y="240" font-size="9.5" fill="{MUT}" opacity="0.85">'
            f"{html.escape(line1)}</text>"
        )
        if line2:
            s += (
                f'<text x="{x}" y="253" font-size="9.5" fill="{MUT}" opacity="0.85">'
                f"{html.escape(line2)}</text>"
            )

    # ---- daily chart -----------------------------------------------------
    s += (
        f'<rect x="24" y="262" width="{w - 48}" height="1" fill="{BORDER}" '
        f'opacity="0.7"/>'
    )
    s += (
        f'<text x="24" y="284" font-size="10.5" font-weight="700" fill="{MUT}" '
        f'letter-spacing="0.8">DAILY DOWNLOADS &#183; LAST 60 DAYS</text>'
    )
    days = 60
    start = today - timedelta(days=days - 1)
    x0, x1 = 24, 776
    y_top, y_base = 296, 352
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

        # The series is heavily skewed: one day carries 114 while a typical day
        # carries 2-3. On a linear scale every normal bar collapses to ~2% of
        # the plot height and the chart reads as empty. A square-root scale
        # keeps the ranking honest while making the small days visible.
        def h_of(v):
            return math.sqrt(max(v, 0) / maxv) * (y_base - y_top)

        # horizontal gridlines with value labels: without these the bars float
        # with no sense of scale
        for frac in (0.25, 0.5, 0.75, 1.0):
            gy = y_base - (y_base - y_top) * frac
            # invert the sqrt mapping so the label matches the bar height
            val = int(round(maxv * frac * frac))
            s += (
                f'<line x1="{x0}" y1="{gy:.1f}" x2="{x1}" y2="{gy:.1f}" '
                f'stroke="{BORDER}" stroke-width="0.8" stroke-dasharray="3 5" '
                f'opacity="0.55"/>'
            )
            s += (
                f'<text x="{x0 - 4}" y="{gy + 3:.1f}" text-anchor="end" '
                f'font-size="8" fill="{MUT}" opacity="0.75">{val}</text>'
            )
        # baseline
        s += (
            f'<line x1="{x0}" y1="{y_base}" x2="{x1}" y2="{y_base}" '
            f'stroke="{BORDER}" stroke-width="1.2"/>'
        )

        peak = max(range(len(series)), key=lambda i: series[i]) if series else 0
        for i, v in enumerate(series):
            bh = h_of(v) if v else 0
            bx = x0 + i * slot
            by = y_base - bh
            # peak day gets the brighter accent; the rest use the gradient
            if i == peak and v:
                fill = PYPI_C
                op = 1.0
            else:
                fill = "url(#pdPyBar)"
                op = 0.9
            s += (
                f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" '
                f'height="{max(bh, 0.8):.1f}" rx="1.5" fill="{fill}" opacity="{op}">'
                f'<animate attributeName="height" from="0" to="{max(bh, 0.8):.1f}" '
                f'dur="0.7s" begin="{i * 0.011:.3f}s" fill="freeze"/>'
                f'<animate attributeName="y" from="{y_base}" to="{by:.1f}" '
                f'dur="0.7s" begin="{i * 0.011:.3f}s" fill="freeze"/>'
                f"</rect>"
            )

        # highlight the peak with a marker + value
        if series and series[peak]:
            px = x0 + peak * slot + bar_w / 2
            py = y_base - h_of(series[peak])
            s += (
                f'<circle cx="{px:.1f}" cy="{py - 7:.1f}" r="2.6" fill="{PYPI_C}">'
                f'<animate attributeName="opacity" values="0.35;1;0.35" dur="2.2s" '
                f'repeatCount="indefinite"/></circle>'
                f'<text x="{px:.1f}" y="{py - 13:.1f}" text-anchor="middle" '
                f'font-size="9" font-weight="700" fill="{TXT}">{series[peak]}</text>'
            )

        s += (
            f'<text x="{x0}" y="{y_base + 14}" font-size="9" fill="{MUT}">'
            f"{start.isoformat()}</text>"
        )
        s += (
            f'<text x="{x1}" y="{y_base + 14}" text-anchor="end" font-size="9" '
            f'fill="{MUT}">today</text>'
        )
        # legend, so the single series is not mistaken for a combined total
        s += (
            f'<rect x="{x1 - 118}" y="{y_top - 22}" width="9" height="9" rx="2" '
            f'fill="{PYPI_C}"/>'
            f'<text x="{x1 - 104}" y="{y_top - 14}" font-size="9" fill="{MUT}">'
            f'PyPI / day</text>'
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
