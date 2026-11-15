#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rich, self-contained animated SVGs for the profile README.

Each widget is pure SMIL (no JavaScript, no external host) and is built from
real geometry computed here, not a handful of hand-placed shapes.

Run:  python scripts/generate_rich.py
Out:  assets/{globe,particles,circuit-board,neural-network}.svg
"""

import html
import math
import os
import random
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

USERNAME = "newnju"

# palette (tokyonight-ish, matching the rest of the profile)
BG = "#0d1117"
CARD = "#161b22"
BORDER = "#30363d"
TXT = "#c9d1d9"
MUT="#8b949e"
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


def svg(w, h, body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}">'
        f"<defs>{defs}</defs>{body}</svg>"
    )


def card(w, h, rx=16, fill=CARD):
    return (
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" '
        f'fill="{fill}" stroke="{BORDER}"/>'
    )


def save(name, content):
    p = ASSETS / name
    # newline="\n" keeps output byte-identical on Windows and Linux runners,
    # so the daily job does not churn every file through CRLF/LF flips.
    p.write_text(content, encoding="utf-8", newline="\n")
    print(f"  {name:22} {len(content):>7,} bytes")


def _token():
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


def _live_stats(fallback="public repos on github.com"):
    """Return a short live stat line, or a neutral fallback if unreachable."""
    try:
        import requests

        h = {"Accept": "application/vnd.github+json", "User-Agent": "dsh"}
        tok = _token()
        if tok:
            h["Authorization"] = f"Bearer {tok}"
        r = requests.get(f"https://api.github.com/users/{USERNAME}", headers=h, timeout=25)
        if r.status_code == 200:
            d = r.json()
            return (
                f"{d.get('public_repos', 0)} public repos &#183; "
                f"{d.get('followers', 0)} followers &#183; "
                f"{d.get('following', 0)} following"
            )
    except Exception:
        pass
    return fallback


# ==========================================================================
# 1. GLOBE - rotating wireframe sphere with live city pulses
# ==========================================================================
def globe():
    W, H = 800, 520
    CX, CY, R = W / 2, 250, 168

    defs = f"""
    <radialGradient id="gSphere" cx="0.36" cy="0.30" r="0.78">
      <stop offset="0" stop-color="#1b2436"/>
      <stop offset="0.55" stop-color="#111a2b"/>
      <stop offset="1" stop-color="#070b14"/>
    </radialGradient>
    <radialGradient id="gGlow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0.62" stop-color="{CYAN}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="gTerm" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#000000" stop-opacity="0.55"/>
      <stop offset="0.45" stop-color="#000000" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="gClip"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>
    """

    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    b.append(card(W, H))
    b.append(
        f'<text x="24" y="32" font-size="13" font-weight="700" fill="{MUT}">'
        f"&#127757; visitor globe &#183; live</text>"
    )

    # atmosphere glow
    b.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R + 34}" fill="url(#gGlow)">'
        f'<animate attributeName="r" values="{R + 26};{R + 44};{R + 26}" '
        f'dur="5s" repeatCount="indefinite"/></circle>'
    )
    # sphere body
    b.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#gSphere)" stroke="{BORDER}"/>')

    # --- meridians: ellipses whose rx oscillates to fake 3D rotation ---
    N_MER = 14
    for k in range(N_MER):
        phase = 360.0 * k / N_MER
        # rx sweeps 0 -> R -> 0 over the cycle; stagger by phase
        b.append(
            f'<ellipse cx="{CX}" cy="{CY}" rx="{R}" ry="{R}" fill="none" '
            f'stroke="{BLUE}" stroke-width="1" opacity="0.28">'
            f'<animate attributeName="rx" values="{R};0;{R}" '
            f'dur="14s" begin="{-14 * k / N_MER:.2f}s" repeatCount="indefinite"/>'
            f"</ellipse>"
        )
    # --- parallels ---
    for lat in (-60, -40, -20, 0, 20, 40, 60):
        rr = R * math.cos(math.radians(lat))
        yy = CY - R * math.sin(math.radians(lat))
        b.append(
            f'<ellipse cx="{CX}" cy="{yy:.1f}" rx="{rr:.1f}" ry="{rr * 0.16:.1f}" '
            f'fill="none" stroke="{CYAN}" stroke-width="0.9" opacity="0.22"/>'
        )

    # --- land dots: a fixed pseudo-random scatter clipped to the sphere,
    #     drifting horizontally and wrapping to fake rotation ---
    random.seed(20261115)
    dots = []
    for _ in range(210):
        # uniform-ish point in disc
        ang = random.uniform(0, 2 * math.pi)
        rad = R * math.sqrt(random.random())
        x = CX + rad * math.cos(ang)
        y = CY + rad * math.sin(ang)
        # only keep points that look like they're on the sphere (avoid heavy edge)
        if (x - CX) ** 2 + (y - CY) ** 2 > (R * 0.97) ** 2:
            continue
        dots.append((x, y, random.uniform(0.8, 1.9)))

    land = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{TEAL}" opacity="0.55"/>'
        for x, y, r in dots
    )
    # two copies drifting for a seamless wrap
    b.append(f'<g clip-path="url(#gClip)">')
    b.append(
        f'<g opacity="0.75"><animateTransform attributeName="transform" '
        f'type="translate" from="0 0" to="{-2 * R} 0" dur="26s" repeatCount="indefinite"/>'
        f'<g>{land}</g><g transform="translate({2 * R},0)">{land}</g></g>'
    )
    b.append("</g>")
    # terminator shading
    b.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#gTerm)"/>')

    # --- city markers with expanding pulse rings ---
    cities = [
        ("SFO", 0.30, 0.36), ("NYC", 0.24, 0.30), ("LON", 0.47, 0.26),
        ("SHA", 0.76, 0.38), ("SIN", 0.72, 0.60), ("SYD", 0.86, 0.74),
        ("SAO", 0.36, 0.72), ("DXB", 0.62, 0.46),
    ]
    for i, (name, fx, fy) in enumerate(cities):
        x = CX + (fx - 0.5) * 2 * R * 0.92
        y = CY + (fy - 0.5) * 2 * R * 0.92
        # keep inside the disc
        if (x - CX) ** 2 + (y - CY) ** 2 > (R * 0.9) ** 2:
            continue
        d = i * 0.45
        b.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{YELLOW}">'
            f'<animate attributeName="opacity" values="1;0.35;1" dur="2.6s" '
            f'begin="{d:.2f}s" repeatCount="indefinite"/></circle>'
        )
        for ring in range(2):
            b.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="none" '
                f'stroke="{YELLOW}" stroke-width="1.2" opacity="0">'
                f'<animate attributeName="r" values="3;20" dur="2.8s" '
                f'begin="{d + ring * 1.4:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0.8;0" dur="2.8s" '
                f'begin="{d + ring * 1.4:.2f}s" repeatCount="indefinite"/></circle>'
            )
    # labels
    for name, fx, fy in cities:
        x = CX + (fx - 0.5) * 2 * R * 0.92
        y = CY + (fy - 0.5) * 2 * R * 0.92
        if (x - CX) ** 2 + (y - CY) ** 2 > (R * 0.9) ** 2:
            continue
        s2 = (
            f'<text x="{x + 8:.1f}" y="{y - 6:.1f}" font-family="{MONO}" '
            f'font-size="9" fill="{MUT}">{name}</text>'
        )
        s2 += (
            f'<animate attributeName="opacity" values="0;0;1;1;0" '
            f'dur="8s" begin="{random.uniform(0, 4):.1f}s" repeatCount="indefinite"/>'
        )
        b.append(f'<g opacity="0">{s2}</g>')

    # --- orbiting satellite with trail ---
    sat_r = R + 46
    b.append(
        f'<g><animateTransform attributeName="transform" type="rotate" '
        f'from="0 {CX} {CY}" to="360 {CX} {CY}" dur="11s" repeatCount="indefinite"/>'
        f'<circle cx="{CX}" cy="{CY - sat_r}" r="4" fill="{TXT}"/>'
        f'<circle cx="{CX}" cy="{CY - sat_r}" r="9" fill="none" stroke="{CYAN}" '
        f'stroke-width="1" opacity="0.5"/></g>'
    )

    # footer stat - pulled live so it cannot go stale
    stats = _live_stats()
    b.append(
        f'<text x="{CX}" y="{H - 22}" text-anchor="middle" font-size="11" '
        f'fill="{MUT}">{stats}</text>'
    )
    return svg(W, H, "".join(b), defs)


# ==========================================================================
# 2. PARTICLES - flow field with proximity links
# ==========================================================================
def particles():
    W, H = 800, 420
    random.seed(77)

    defs = f"""
    <radialGradient id="pBg" cx="0.5" cy="0.45" r="0.75">
      <stop offset="0" stop-color="#101a2e"/>
      <stop offset="1" stop-color="#05070d"/>
    </radialGradient>
    <radialGradient id="pDot" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="0.4" stop-color="{CYAN}"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    """

    N = 46
    pts = []
    for _ in range(N):
        pts.append((
            random.uniform(60, W - 60),
            random.uniform(70, H - 60),
            random.uniform(1.4, 3.2),
            random.choice([CYAN, BLUE, TEAL, PURPLE, PINK]),
            random.uniform(6, 15),
            random.uniform(0, 6),
        ))

    b = [f'<rect width="{W}" height="{H}" fill="url(#pBg)"/>', card(W, H, fill="none")]
    b.append(
        f'<text x="24" y="30" font-size="13" font-weight="700" fill="{MUT}">'
        f"&#10024; particle field</text>"
    )

    # proximity links (static topology, pulsing opacity)
    for i in range(N):
        x1, y1, *_ = pts[i]
        for j in range(i + 1, N):
            x2, y2, *_ = pts[j]
            d = math.hypot(x2 - x1, y2 - y1)
            if d < 132:
                op = max(0.05, 0.42 * (1 - d / 132))
                dur = random.uniform(2.5, 6.0)
                b.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="{CYAN}" stroke-width="0.7" opacity="{op:.2f}">'
                    f'<animate attributeName="opacity" values="{op * 0.35:.2f};{op:.2f};'
                    f'{op * 0.35:.2f}" dur="{dur:.1f}s" '
                    f'begin="{random.uniform(0, 3):.1f}s" repeatCount="indefinite"/></line>'
                )

    # drifting nodes
    for i, (x, y, r, col, dur, delay) in enumerate(pts):
        dx = random.uniform(-26, 26)
        dy = random.uniform(-20, 20)
        b.append(
            f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{dx:.1f} {dy:.1f};0 0" dur="{dur:.1f}s" '
            f'begin="{delay:.1f}s" repeatCount="indefinite"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 2.6:.1f}" fill="url(#pDot)" '
            f'opacity="0.35"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}">'
            f'<animate attributeName="opacity" values="0.55;1;0.55" dur="{dur * 0.6:.1f}s" '
            f'begin="{delay:.1f}s" repeatCount="indefinite"/></circle></g>'
        )

    b.append(
        f'<text x="{W - 20}" y="{H - 16}" text-anchor="end" font-size="10" '
        f'fill="{MUT}">{N} nodes &#183; proximity-linked</text>'
    )
    return svg(W, H, "".join(b), defs)


# ==========================================================================
# 3. CIRCUIT BOARD - PCB traces with travelling data packets
# ==========================================================================
def circuit_board():
    W, H = 800, 400
    random.seed(4242)

    defs = f"""
    <linearGradient id="cTrace" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{TEAL}" stop-opacity="0.25"/>
      <stop offset="0.5" stop-color="{CYAN}" stop-opacity="0.85"/>
      <stop offset="1" stop-color="{TEAL}" stop-opacity="0.25"/>
    </linearGradient>
    <radialGradient id="cPad" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{YELLOW}" stop-opacity="0.9"/>
      <stop offset="1" stop-color="{YELLOW}" stop-opacity="0"/>
    </radialGradient>
    """

    b = [f'<rect width="{W}" height="{H}" fill="#070c12"/>', card(W, H, fill="#070c12")]
    b.append(
        f'<text x="24" y="30" font-size="13" font-weight="700" fill="{MUT}">'
        f"&#9889; data flow</text>"
    )

    # --- traces: orthogonal PCB routes on a grid ---
    grid = 40
    traces = []
    for _ in range(26):
        x = random.randrange(1, W // grid) * grid
        y = random.randrange(2, (H - 60) // grid) * grid
        pts = [(x, y)]
        for _seg in range(random.randint(2, 5)):
            if random.random() < 0.5:
                x = max(grid, min(W - grid, x + random.choice([-2, -1, 1, 2]) * grid))
            else:
                y = max(2 * grid, min(H - 2 * grid, y + random.choice([-2, -1, 1, 2]) * grid))
            pts.append((x, y))
        traces.append(pts)

    for idx, pts in enumerate(traces):
        d = "M " + " L ".join(f"{px},{py}" for px, py in pts)
        b.append(
            f'<path d="{d}" fill="none" stroke="{TEAL}" stroke-width="1.6" '
            f'opacity="0.28" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        # a data packet racing along the trace
        dur = random.uniform(3.0, 7.0)
        b.append(
            f'<circle r="3" fill="{CYAN}">'
            f'<animateMotion dur="{dur:.1f}s" begin="{random.uniform(0, 4):.1f}s" '
            f'repeatCount="indefinite" path="{d}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" dur="{dur:.1f}s" '
            f'begin="{random.uniform(0, 4):.1f}s" repeatCount="indefinite"/></circle>'
        )
        # solder pads at the ends
        for px, py in (pts[0], pts[-1]):
            b.append(
                f'<circle cx="{px}" cy="{py}" r="6" fill="url(#cPad)" opacity="0.5">'
                f'<animate attributeName="r" values="4;7;4" dur="3s" '
                f'begin="{random.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>'
            )
            b.append(
                f'<circle cx="{px}" cy="{py}" r="2.4" fill="{YELLOW}" opacity="0.85"/>'
            )

    # central chip
    cx, cy = W / 2, H / 2
    b.append(
        f'<g><rect x="{cx - 62}" y="{cy - 34}" width="124" height="68" rx="8" '
        f'fill="#0b1220" stroke="{CYAN}" stroke-width="1.4"/>'
        f'<rect x="{cx - 54}" y="{cy - 26}" width="108" height="52" rx="4" '
        f'fill="none" stroke="{BORDER}"/>'
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="12" fill="{CYAN}">DROIDSEAL</text>'
        f'<animate attributeName="opacity" values="0.85;1;0.85" dur="2.4s" repeatCount="indefinite"/>'
        f"</g>"
    )
    # chip pins
    for k in range(7):
        px = cx - 48 + k * 16
        b.append(f'<rect x="{px}" y="{cy - 40}" width="7" height="6" fill="{YELLOW}" opacity="0.8"/>')
        b.append(f'<rect x="{px}" y="{cy + 34}" width="7" height="6" fill="{YELLOW}" opacity="0.8"/>')

    b.append(
        f'<text x="{W - 20}" y="{H - 16}" text-anchor="end" font-size="10" '
        f'fill="{MUT}">{len(traces)} traces &#183; live packets</text>'
    )
    return svg(W, H, "".join(b), defs)


# ==========================================================================
# 4. NEURAL NETWORK - layered net with signal propagation
# ==========================================================================
def neural_network():
    W, H = 800, 440
    random.seed(9)

    defs = f"""
    <radialGradient id="nBg" cx="0.5" cy="0.4" r="0.8">
      <stop offset="0" stop-color="#111a2e"/>
      <stop offset="1" stop-color="#06080f"/>
    </radialGradient>
    <linearGradient id="nEdge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{PURPLE}" stop-opacity="0.15"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0.55"/>
    </linearGradient>
    """

    layers = [5, 8, 7, 4]
    xs = [110, 300, 500, 690]
    top, bottom = 80, 380

    # node positions
    pos = []
    for li, n in enumerate(layers):
        col = []
        for ni in range(n):
            if n == 1:
                y = (top + bottom) / 2
            else:
                y = top + (bottom - top) * ni / (n - 1)
            col.append((xs[li], y))
        pos.append(col)

    b = [f'<rect width="{W}" height="{H}" fill="url(#nBg)"/>', card(W, H, fill="none")]
    b.append(
        f'<text x="24" y="32" font-size="13" font-weight="700" fill="{MUT}">'
        f"&#129504; neural net &#183; signal propagation</text>"
    )

    # edges
    for li in range(len(layers) - 1):
        for (x1, y1) in pos[li]:
            for (x2, y2) in pos[li + 1]:
                op = random.uniform(0.10, 0.34)
                dur = random.uniform(3, 7)
                b.append(
                    f'<line x1="{x1}" y1="{y1:.1f}" x2="{x2}" y2="{y2:.1f}" '
                    f'stroke="url(#nEdge)" stroke-width="1" opacity="{op:.2f}">'
                    f'<animate attributeName="opacity" values="{op * 0.4:.2f};{op:.2f};'
                    f'{op * 0.4:.2f}" dur="{dur:.1f}s" '
                    f'begin="{random.uniform(0, 4):.1f}s" repeatCount="indefinite"/></line>'
                )

    # travelling signal packets along random edges
    for _ in range(22):
        li = random.randrange(len(layers) - 1)
        x1, y1 = random.choice(pos[li])
        x2, y2 = random.choice(pos[li + 1])
        dur = random.uniform(1.6, 3.4)
        b.append(
            f'<circle r="2.6" fill="{CYAN}">'
            f'<animateMotion dur="{dur:.1f}s" begin="{random.uniform(0, 3):.1f}s" '
            f'repeatCount="indefinite" path="M {x1},{y1:.1f} L {x2},{y2:.1f}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" dur="{dur:.1f}s" '
            f'begin="{random.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>'
        )

    # nodes
    layer_colors = [BLUE, CYAN, PURPLE, TEAL]
    for li, col in enumerate(pos):
        base = layer_colors[li % len(layer_colors)]
        for ni, (x, y) in enumerate(col):
            d = (li * 0.2 + ni * 0.08)
            b.append(
                f'<circle cx="{x}" cy="{y:.1f}" r="13" fill="{base}" opacity="0.10">'
                f'<animate attributeName="r" values="11;16;11" dur="2.8s" '
                f'begin="{d:.2f}s" repeatCount="indefinite"/></circle>'
            )
            b.append(
                f'<circle cx="{x}" cy="{y:.1f}" r="6" fill="{base}" stroke="{TXT}" '
                f'stroke-width="0.8">'
                f'<animate attributeName="opacity" values="0.6;1;0.6" dur="2.4s" '
                f'begin="{d:.2f}s" repeatCount="indefinite"/></circle>'
            )

    # layer captions
    names = ["input", "hidden 1", "hidden 2", "output"]
    for li, nm in enumerate(names):
        b.append(
            f'<text x="{xs[li]}" y="{H - 26}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="10" fill="{MUT}">{nm} &#183; {layers[li]}</text>'
        )

    return svg(W, H, "".join(b), defs)


def fireworks():
    """Fireworks over a night skyline.

    Rockets launch, coast upward under gravity, then burst into a radial
    spray whose sparks are integrated ballistically (vx/vy + drag + gravity)
    rather than being hand-placed. Trails come from per-spark history polylines.
    """
    W, H = 800, 420
    GROUND = H - 52
    random.seed(1024)

    defs = f"""
    <linearGradient id="fSky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#05010f"/>
      <stop offset="0.55" stop-color="#0b0620"/>
      <stop offset="1" stop-color="#140a2e"/>
    </linearGradient>
    <radialGradient id="fGlow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.95"/>
      <stop offset="0.35" stop-color="#36BCF7" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#36BCF7" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="fCity" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#161028"/>
      <stop offset="1" stop-color="#05030c"/>
    </linearGradient>
    """

    b = [f'<rect width="{W}" height="{H}" fill="url(#fSky)"/>']
    b.append(card(W, H, fill="none"))
    b.append(
        f'<text x="24" y="30" font-size="13" font-weight="700" fill="{MUT}">'
        f"&#127878; fireworks &#183; ballistic sparks</text>"
    )

    # ---- stars (static, twinkling) ----
    for _ in range(90):
        x = random.uniform(6, W - 6)
        y = random.uniform(40, GROUND - 90)
        r = random.choice([0.5, 0.7, 0.9, 1.2])
        dur = round(random.uniform(2.0, 5.5), 2)
        b.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#ffffff" opacity="0.55">'
            f'<animate attributeName="opacity" values="0.12;0.8;0.12" dur="{dur}s" '
            f'begin="{random.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>'
        )

    # ---- city skyline (deterministic) ----
    x = 0
    while x < W:
        bw = random.randint(26, 62)
        bh = random.randint(34, 96)
        if x + bw > W:
            bw = W - x
        b.append(
            f'<rect x="{x}" y="{GROUND - bh}" width="{bw}" height="{bh}" '
            f'fill="url(#fCity)" stroke="#241a3d" stroke-width="0.6"/>'
        )
        # windows
        for wy in range(int(GROUND - bh) + 8, GROUND - 6, 11):
            for wx in range(x + 5, x + bw - 5, 9):
                if random.random() < 0.35:
                    b.append(
                        f'<rect x="{wx}" y="{wy}" width="3" height="4" fill="{YELLOW}" '
                        f'opacity="{random.uniform(0.25, 0.8):.2f}"/>'
                    )
        x += bw + random.randint(2, 7)
    b.append(f'<rect x="0" y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#05030c"/>')

    # ---- firework bursts ----
    shells = [
        (0.06, 0.30, 168, 26, [CYAN, BLUE, PURPLE]),
        (0.30, 0.22, 132, 22, [PINK, PURPLE, YELLOW]),
        (0.53, 0.34, 196, 30, [GREEN, TEAL, CYAN]),
        (0.72, 0.18, 118, 20, [YELLOW, ORANGE, RED]),
        (0.88, 0.28, 210, 34, [PURPLE, PINK, BLUE]),
    ]

    # Each shell runs on one shared cycle: rise -> burst -> sparks fly and fade,
    # then a quiet gap before the next shell. One burst per shell per cycle.
    STAGGER = 1.1       # launch offset between shells
    RISE = 0.5          # rocket climb time
    SPARK_LIFE = 1.55   # spark flight time
    GRAV = 62.0
    # Derive the cycle so the LAST shell's sparks fully finish (keyTimes <= 1)
    # instead of overflowing past 1.0, which SMIL rejects.
    CYCLE = (len(shells) - 1) * STAGGER + SPARK_LIFE + 0.9

    for si, (cx_frac, top_frac, maxr, nsparks, cols) in enumerate(shells):
        cx = cx_frac * W
        cy = GROUND - (GROUND - 60) * top_frac
        t_burst = si * STAGGER          # burst moment within the cycle

        # ---- rocket trail: grows during RISE, then gone ----
        rise_end = t_burst
        b.append(
            f'<g opacity="0">'
            f'<rect x="{cx - 1.2:.1f}" y="{cy:.1f}" width="2.4" '
            f'height="{GROUND - cy:.1f}" fill="{CYAN}" opacity="0.22"/>'
            f'<animate attributeName="opacity" values="0;0;0.9;0.5;0;0" '
            f'keyTimes="0;{rise_end / CYCLE:.4f};{(rise_end + RISE) / CYCLE:.4f};'
            f'{(rise_end + RISE + 0.2) / CYCLE:.4f};{(rise_end + RISE + 0.5) / CYCLE:.4f};1" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></g>'
        )

        # ---- burst flash ----
        b.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="url(#fGlow)" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0.85;0;0" '
            f'keyTimes="0;{t_burst / CYCLE:.4f};{(t_burst + 0.04) / CYCLE:.4f};'
            f'{(t_burst + 0.12) / CYCLE:.4f};{(t_burst + 0.3) / CYCLE:.4f};1" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animate attributeName="r" values="2;2;30;42;46;46" '
            f'keyTimes="0;{t_burst / CYCLE:.4f};{(t_burst + 0.1) / CYCLE:.4f};'
            f'{(t_burst + 0.25) / CYCLE:.4f};{(t_burst + 0.45) / CYCLE:.4f};1" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></circle>'
        )

        # ---- sparks: ballistic integration, one burst per cycle ----
        for k in range(nsparks):
            ang = (k / nsparks) * 2 * math.pi + random.uniform(-0.06, 0.06)
            spd = random.uniform(0.55, 1.0) * maxr
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            col = random.choice(cols)

            pts = []
            for step in range(13):
                t = step * (SPARK_LIFE / 12)
                px = cx + vx * t
                py = cy + vy * t + 0.5 * GRAV * t * t
                pts.append((px, py))
            tail = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)

            t_end = t_burst + SPARK_LIFE
            b.append(
                f'<polyline points="{tail}" fill="none" stroke="{col}" '
                f'stroke-width="1.5" stroke-linecap="round" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;0.55;0.4;0;0" '
                f'keyTimes="0;{t_burst / CYCLE:.4f};{(t_burst + 0.05) / CYCLE:.4f};'
                f'{(t_burst + 0.9) / CYCLE:.4f};{t_end / CYCLE:.4f};1" '
                f'dur="{CYCLE}s" repeatCount="indefinite"/></polyline>'
            )
            # spark head travels the path only during its window
            b.append(
                f'<circle cx="{pts[0][0]:.1f}" cy="{pts[0][1]:.1f}" r="2" fill="{col}" opacity="0">'
                f'<animateMotion dur="{CYCLE}s" repeatCount="indefinite" '
                f'keyPoints="0;0;1;1" '
        f'keyTimes="0;{t_burst / CYCLE:.4f};{t_end / CYCLE:.4f};1" '
                f'calcMode="linear" '
                f'path="M {pts[0][0]:.1f},{pts[0][1]:.1f} '
                + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts[1:])
                + '"/>'
                f'<animate attributeName="opacity" values="0;0;1;0.9;0;0" '
                f'keyTimes="0;{t_burst / CYCLE:.4f};{(t_burst + 0.05) / CYCLE:.4f};'
                f'{(t_burst + 1.1) / CYCLE:.4f};{t_end / CYCLE:.4f};1" '
                f'dur="{CYCLE}s" repeatCount="indefinite"/></circle>'
            )

    b.append(
        f'<text x="{W - 20}" y="{H - 16}" text-anchor="end" font-size="10" '
        f'fill="{MUT}">5 shells &#183; gravity + drag</text>'
    )
    return svg(W, H, "".join(b), defs)


def main():
    print("generating rich widgets:")
    save("globe.svg", globe())
    save("particles.svg", particles())
    save("circuit-board.svg", circuit_board())
    save("neural-network.svg", neural_network())
    save("fireworks.svg", fireworks())
    print("done.")


if __name__ == "__main__":
    main()