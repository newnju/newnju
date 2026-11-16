#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cinematic scene widgets for the profile README.

The five widgets here were the thinnest of the set: each was drawn in a 200-320
unit viewBox and then upscaled ~3x to 800px, so every stroke was blurry and the
motion was a handful of circles sliding around. These are authored natively at
their display size, with real geometry (orbital mechanics, ballistic plumes,
lunar terminator, phased radar) computed here rather than hand-placed.

Every widget is pure SMIL and self-contained, so it renders on github.com
without a third-party image host.

Run:  python scripts/generate_scenes.py
Out:  assets/{rocket,solar,atom,radar,moon}.svg

SMIL gotchas honoured here:
  * a child <animateTransform> *replaces* the element's transform attribute,
    so animated elements are always wrapped in a positioning <g>
  * keyTimes must be monotonic and end at <= 1.0
"""

import html
import math
import random
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# palette, matching the rest of the profile
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
    # newline="\n" keeps output byte-identical on Windows and Linux runners.
    p.write_text(content, encoding="utf-8", newline="\n")
    print(f"  {name:16} {len(content):>8,} bytes")


def esc(s):
    return html.escape(s, quote=True)


def kt(values, dur):
    """Build a strictly-increasing keyTimes list in [0,1] from times in seconds.

    SMIL rejects any keyTimes list that is not non-decreasing, or that ends
    above 1.0, and a rejected list silently kills the whole animation. Two
    hazards make naive arithmetic unsafe:

      * rounding to 4 decimals can collapse two distinct stops onto the same
        value (0.00004 and 0 both render as "0.0000")
      * a final stop can land a hair under 1.0 and then be followed by the
        trailing 1 the caller appends

    So: quantise first, then walk the list forward and backward to force a
    strictly increasing sequence that still starts at 0 and ends at 1.
    """
    q = [min(1.0, max(0.0, round(v / dur, 4))) for v in values]
    # forward pass: make every stop strictly greater than its predecessor
    for i in range(1, len(q)):
        if q[i] <= q[i - 1]:
            q[i] = min(1.0, round(q[i - 1] + 1e-4, 4))
    # backward pass: if that pushed the tail past 1.0, pull earlier stops down
    for i in range(len(q) - 2, -1, -1):
        if q[i] >= q[i + 1]:
            q[i] = max(0.0, round(q[i + 1] - 1e-4, 4))
    q[-1] = 1.0
    q[0] = 0.0
    for i in range(1, len(q)):
        if q[i] <= q[i - 1]:
            q[i] = round(q[i - 1] + 1e-4, 4)
    return ";".join(f"{t:.4f}" for t in q)


# ---------------------------------------------------------------------------
# 1. rocket - night launch: ignition, hold-down, tower clear, exhaust plume
# ---------------------------------------------------------------------------
def rocket():
    W, H = 800, 470
    GROUND = 392
    PAD = 404
    CX = 400
    # rocket local origin = base of the engine bell
    CYCLE = 9.0
    IGNITE = 1.35
    LIFTOFF = 2.45

    b = []
    defs = [
        '<linearGradient id="rSky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#05070f"/>'
        f'<stop offset="0.62" stop-color="#0b1220"/>'
        f'<stop offset="1" stop-color="#141d2e"/>'
        '</linearGradient>',
        '<radialGradient id="rFlame" cx="0.5" cy="0.18" r="0.85">'
        f'<stop offset="0" stop-color="#fffdf0" stop-opacity="0.98"/>'
        f'<stop offset="0.32" stop-color="#ffd76a" stop-opacity="0.9"/>'
        f'<stop offset="0.62" stop-color="#ff8a2b" stop-opacity="0.6"/>'
        f'<stop offset="1" stop-color="#f85149" stop-opacity="0"/>'
        '</radialGradient>',
        '<radialGradient id="rPadGlow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="#ffb347" stop-opacity="0.55"/>'
        f'<stop offset="1" stop-color="#ffb347" stop-opacity="0"/>'
        '</radialGradient>',
        '<linearGradient id="rBody" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#8b96a8"/>'
        f'<stop offset="0.34" stop-color="#f2f5f9"/>'
        f'<stop offset="0.62" stop-color="#c9d2de"/>'
        f'<stop offset="1" stop-color="#6f7b8d"/>'
        '</linearGradient>',
        '<linearGradient id="rPlume" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#fff8dc" stop-opacity="0.95"/>'
        f'<stop offset="0.45" stop-color="#ffb347" stop-opacity="0.55"/>'
        f'<stop offset="1" stop-color="#f85149" stop-opacity="0"/>'
        '</linearGradient>',
    ]

    # ---- sky + stars -----------------------------------------------------
    b.append(f'<rect width="{W}" height="{H}" fill="url(#rSky)"/>')
    random.seed(11)
    for _ in range(96):
        x = random.uniform(0, W)
        y = random.uniform(0, GROUND - 40)
        r = random.choice([0.6, 0.8, 1.0, 1.3, 1.6])
        dur = random.uniform(2.4, 6.5)
        base = random.uniform(0.25, 0.8)
        b.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#eaf2ff" '
            f'opacity="{base:.2f}">'
            f'<animate attributeName="opacity" values="{base:.2f};'
            f'{min(1.0, base + 0.35):.2f};{base:.2f}" dur="{dur:.2f}s" '
            f'repeatCount="indefinite"/></circle>'
        )

    # ---- launch tower ----------------------------------------------------
    TX = CX + 74
    tw = 26
    b.append(f'<g stroke="#4a5568" stroke-width="2" opacity="0.85">')
    for i in range(9):
        y0 = GROUND - 12 - i * 26
        b.append(f'<line x1="{TX}" y1="{y0}" x2="{TX + tw}" y2="{y0 - 26}"/>')
        b.append(f'<line x1="{TX + tw}" y1="{y0}" x2="{TX}" y2="{y0 - 26}"/>')
    b.append(f'<line x1="{TX}" y1="{GROUND - 8}" x2="{TX}" y2="{GROUND - 8 - 9 * 26}"/>')
    b.append(f'<line x1="{TX + tw}" y1="{GROUND - 8}" x2="{TX + tw}" y2="{GROUND - 8 - 9 * 26}"/>')
    b.append('</g>')
    # tower service arms
    arm_times = [0, IGNITE, IGNITE + 0.5, CYCLE]
    for i, ay in enumerate((GROUND - 40, GROUND - 132, GROUND - 208)):
        b.append(
            f'<rect x="{CX + 26}" y="{ay}" width="{TX - CX - 22}" height="5" '
            f'rx="2" fill="#5a6678" opacity="0.8">'
            f'<animate attributeName="opacity" values="0.8;0.8;0.15;0.15" '
            f'keyTimes="{kt(arm_times, CYCLE)}" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></rect>'
        )
    # lightning mast
    b.append(f'<line x1="{TX + tw / 2}" y1="{GROUND - 242}" x2="{TX + tw / 2}" '
             f'y2="{GROUND - 300}" stroke="#4a5568" stroke-width="2"/>')
    b.append(f'<circle cx="{TX + tw / 2}" cy="{GROUND - 302}" r="3" fill="{RED}">'
             f'<animate attributeName="opacity" values="1;0.15;1" dur="1.1s" '
             f'repeatCount="indefinite"/></circle>')

    # ---- lightning / pad glow -------------------------------------------
    glow_times = [0, IGNITE - 0.15, IGNITE, IGNITE + 0.5, LIFTOFF, CYCLE]
    b.append(f'<ellipse cx="{CX}" cy="{GROUND + 6}" rx="190" ry="46" '
             f'fill="url(#rPadGlow)" opacity="0">'
             f'<animate attributeName="opacity" values="0;0;0.55;0.95;0.8;0" '
             f'keyTimes="{kt(glow_times, CYCLE)}" '
             f'dur="{CYCLE}s" repeatCount="indefinite"/></ellipse>')

    # ---- exhaust plume (drawn under the rocket) -------------------------
    pl = []
    plume_times = [0, IGNITE - 0.2, IGNITE, IGNITE + 0.45, LIFTOFF + 1.1, CYCLE]
    outer_times = [0, IGNITE - 0.2, IGNITE, IGNITE + 0.18, IGNITE + 0.42,
                   IGNITE + 0.66, IGNITE + 0.9, CYCLE]
    inner_times = [0, IGNITE - 0.2, IGNITE, IGNITE + 0.16, IGNITE + 0.4,
                   IGNITE + 0.64, IGNITE + 0.88, CYCLE]
    pl.append(
        f'<g opacity="0" id="plume">'
        f'<animate attributeName="opacity" values="0;0;1;1;0.9;0" '
        f'keyTimes="{kt(plume_times, CYCLE)}" '
        f'dur="{CYCLE}s" repeatCount="indefinite"/>'
        # outer plume
        f'<path d="M -19,6 Q -30,74 0,132 Q 30,74 19,6 Z" fill="url(#rPlume)">'
        f'<animateTransform attributeName="transform" type="scale" '
        f'values="1 0.05;1 0.05;1 1.05;1 0.92;1 1.12;1 0.95;1 1.05;1 0.05" '
        f'keyTimes="{kt(outer_times, CYCLE)}" '
        f'dur="{CYCLE}s" repeatCount="indefinite"/></path>'
        # inner core
        f'<path d="M -10,6 Q -16,50 0,88 Q 16,50 10,6 Z" fill="#fffdf0" '
        f'opacity="0.95">'
        f'<animateTransform attributeName="transform" type="scale" '
        f'values="1 0.05;1 0.05;1 1.1;1 0.86;1 1.18;1 0.9;1 1.08;1 0.05" '
        f'keyTimes="{kt(inner_times, CYCLE)}" '
        f'dur="{CYCLE}s" repeatCount="indefinite"/></path>'
        # shock diamonds
        f'<g fill="#fffbe8" opacity="0.85">'
        + "".join(
            f'<ellipse cx="0" cy="{18 + i * 17}" rx="{4.2 - i * 0.5}" ry="2.6">'
            f'<animate attributeName="opacity" values="0.9;0.25;0.9" '
            f'dur="{0.42 + i * 0.05:.2f}s" repeatCount="indefinite"/></ellipse>'
            for i in range(5)
        )
        + '</g>'
        f'<circle cx="0" cy="8" r="26" fill="url(#rFlame)"/>'
        f'</g>'
    )
    b.append("".join(pl))

    # ---- smoke: billows that build at ignition and roll outward ---------
    random.seed(23)
    for i in range(26):
        ang = random.uniform(-math.pi, 0)
        dist = random.uniform(0, 1)
        r0 = random.uniform(10, 26)
        x0 = CX + math.cos(ang) * dist * 26
        y0 = GROUND + 4 + math.sin(ang) * 6
        delay = IGNITE + random.uniform(-0.1, 1.5)
        dur = CYCLE
        peak = random.uniform(0.16, 0.34)
        op_times = [0, delay, delay + 0.7, delay + 2.4, delay + 4.2, CYCLE]
        tr_times = [0, delay, delay + 0.8, delay + 2.6, delay + 4.4, CYCLE]
        r_times = [0, delay, delay + 0.8, delay + 2.6, delay + 4.4, CYCLE]
        b.append(
            f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="{r0:.1f}" fill="#c8d3e0" '
            f'opacity="0">'
            f'<animate attributeName="opacity" values="0;0;{peak:.2f};'
            f'{peak * 0.7:.2f};0;0" '
            f'keyTimes="{kt(op_times, dur)}" '
            f'dur="{dur}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 0;{math.cos(ang) * 46:.1f} {-26 - dist * 30:.1f};'
            f'{math.cos(ang) * 92:.1f} {-58 - dist * 52:.1f};'
            f'{math.cos(ang) * 124:.1f} {-74 - dist * 62:.1f};0 0" '
            f'keyTimes="{kt(tr_times, dur)}" '
            f'dur="{dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="r" values="{r0:.1f};{r0:.1f};'
            f'{r0 * 2.3:.1f};{r0 * 3.6:.1f};{r0 * 4.4:.1f};{r0:.1f}" '
            f'keyTimes="{kt(r_times, dur)}" '
            f'dur="{dur}s" repeatCount="indefinite"/></circle>'
        )

    # ---- the vehicle -----------------------------------------------------
    rk = []
    rk.append(
        # engine bell
        f'<path d="M -17,2 L 17,2 L 11,-20 L -11,-20 Z" fill="#5c6675" '
        f'stroke="#39424f" stroke-width="1"/>'
        # body
        f'<rect x="-21" y="-162" width="42" height="142" rx="4" '
        f'fill="url(#rBody)"/>'
        # nose cone
        f'<path d="M -21,-162 L 0,-220 L 21,-162 Z" fill="url(#rBody)"/>'
        # nose tip
        f'<path d="M -5,-206 L 0,-220 L 5,-206 Z" fill="{RED}" opacity="0.9"/>'
        # body bands
        f'<rect x="-21" y="-150" width="42" height="4" fill="{RED}" opacity="0.85"/>'
        f'<rect x="-21" y="-70" width="42" height="5" fill="#2b3340" opacity="0.8"/>'
        # flag / livery
        f'<rect x="-13" y="-136" width="26" height="15" rx="2" fill="#1f6feb" '
        f'opacity="0.9"/>'
        f'<path d="M -13,-128.5 L 13,-128.5" stroke="#fff" stroke-width="1.6" '
        f'opacity="0.85"/>'
        # porthole
        f'<circle cx="0" cy="-96" r="9.5" fill="#0e1622" stroke="#aab6c6" '
        f'stroke-width="2"/>'
        f'<circle cx="0" cy="-96" r="6" fill="{CYAN}" opacity="0.55">'
        f'<animate attributeName="opacity" values="0.35;0.7;0.35" dur="3.2s" '
        f'repeatCount="indefinite"/></circle>'
        # interstage ring
        f'<rect x="-22" y="-58" width="44" height="5" rx="2" fill="#39424f"/>'
        # fins
        f'<path d="M -21,-46 L -42,6 L -21,-4 Z" fill="#b9c4d2" '
        f'stroke="#7d8896" stroke-width="1"/>'
        f'<path d="M 21,-46 L 42,6 L 21,-4 Z" fill="#b9c4d2" '
        f'stroke="#7d8896" stroke-width="1"/>'
        # raceway
        f'<rect x="15" y="-158" width="3.4" height="132" fill="#8c98a8" '
        f'opacity="0.75"/>'
    )
    # ascent: hold-down -> accelerate -> off the top
    dy = [
        (0.0, 0), (IGNITE / CYCLE, 0), (LIFTOFF / CYCLE, 0),
        (0.30, -6), (0.40, -74), (0.52, -238), (0.64, -486),
        (0.74, -760), (0.82, -980), (1.0, -980),
    ]
    dy_s = ";".join(
        f"0 {v:.0f}" for _, v in dy
    )
    kt_s = ";".join(f"{t:.4f}" for t, _ in dy)
    # fade out as it clears the top so the loop reset is invisible
    op = [
        (0.0, 1), (0.70, 1), (0.78, 0.0), (1.0, 0.0),
    ]
    op_s = ";".join(f"{v:.2f}" for _, v in op)
    okt_s = ";".join(f"{t:.4f}" for t, _ in op)

    b.append(
        f'<g transform="translate({CX},{GROUND})">'
        f'<g opacity="1">'
        f'<animate attributeName="opacity" values="{op_s}" keyTimes="{okt_s}" '
        f'dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="{dy_s}" keyTimes="{kt_s}" dur="{CYCLE}s" '
        f'repeatCount="indefinite"/>'
        + "".join(rk)
        + '</g></g>'
    )

    # ---- ground / pad ----------------------------------------------------
    b.append(f'<rect x="0" y="{GROUND}" width="{W}" height="{H - GROUND}" '
             f'fill="#0a0f18"/>')
    b.append(f'<rect x="0" y="{GROUND}" width="{W}" height="2" fill="#26303f"/>')
    # flame trench
    b.append(f'<path d="M {CX - 34},{GROUND} L {CX + 34},{GROUND} '
             f'L {CX + 22},{H} L {CX - 22},{H} Z" fill="#05080e"/>')
    # pad deck
    b.append(f'<rect x="{CX - 96}" y="{GROUND - 4}" width="192" height="8" '
             f'rx="2" fill="#1b2330"/>')

    # ---- HUD -------------------------------------------------------------
    t = LIFTOFF
    b.append(
        f'<text x="24" y="34" font-family="{MONO}" font-size="12" '
        f'fill="{MUT}" letter-spacing="1.6">LAUNCH COMPLEX</text>'
        f'<text x="24" y="58" font-family="{MONO}" font-size="15" '
        f'fill="{TXT}">T+ {t:04.1f}s</text>'
    )
    # status line that swaps at ignition / liftoff
    for txt, t0, t1, col in (
        ("PRE-LAUNCH", 0.0, IGNITE, MUT),
        ("IGNITION", IGNITE, LIFTOFF, YELLOW),
        ("LIFTOFF", LIFTOFF, CYCLE * 0.86, GREEN),
    ):
        status_times = [0, t0, t0 + 0.06, t1, t1 + 0.06, CYCLE]
        b.append(
            f'<text x="24" y="80" font-family="{MONO}" font-size="12" '
            f'fill="{col}" letter-spacing="1.2" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="{kt(status_times, CYCLE)}" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/>{esc(txt)}</text>'
        )
    # altitude tape
    b.append(f'<g opacity="0.55">')
    for i in range(9):
        y = 118 + i * 26
        b.append(f'<line x1="{W - 92}" y1="{y}" x2="{W - 74}" y2="{y}" '
                 f'stroke="{MUT}" stroke-width="1"/>')
        b.append(f'<text x="{W - 68}" y="{y + 4}" font-family="{MONO}" '
                 f'font-size="9" fill="{MUT}">{i * 200}</text>')
    b.append('</g>')
    b.append(f'<text x="{W - 24}" y="{H - 18}" text-anchor="end" '
             f'font-family="{MONO}" font-size="10" fill="{MUT}">'
             f'gravity turn &#183; 9.0s cycle</text>')

    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 2. solar - orrery: real relative periods, eccentricity, moons, asteroid belt
# ---------------------------------------------------------------------------
# Orbital periods are real; on-screen durations are a log-compressed map of
# them so Mercury visibly races while Neptune still completes a lap.
P_MIN, P_MAX = 0.241, 164.8
D_MIN, D_MAX = 3.4, 34.0
_D_EXP = math.log(D_MAX / D_MIN) / math.log(P_MAX / P_MIN)


def d_for(period_years):
    """Map a real orbital period (years) to an on-screen duration (seconds)."""
    return D_MIN * (period_years / P_MIN) ** _D_EXP


def solar():
    W, H = 800, 520
    CX, CY = 400, 258
    CYCLE = 26.0

    b = []
    defs = [
        '<radialGradient id="sSun" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="#fffdf2"/>'
        f'<stop offset="0.45" stop-color="#ffe07a"/>'
        f'<stop offset="0.78" stop-color="#ffb02e"/>'
        f'<stop offset="1" stop-color="#f07f16" stop-opacity="0.15"/>'
        '</radialGradient>',
        '<radialGradient id="sCorona" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0.42" stop-color="#ffcf5c" stop-opacity="0.5"/>'
        f'<stop offset="0.72" stop-color="#ff9d2e" stop-opacity="0.14"/>'
        f'<stop offset="1" stop-color="#ff7b00" stop-opacity="0"/>'
        '</radialGradient>',
        '<radialGradient id="sGlow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="#7f5bff" stop-opacity="0.22"/>'
        f'<stop offset="1" stop-color="#7f5bff" stop-opacity="0"/>'
        '</radialGradient>',
    ]

    b.append(f'<rect width="{W}" height="{H}" fill="#05070e"/>')
    # faint galactic band
    b.append(f'<ellipse cx="{CX}" cy="{CY}" rx="430" ry="150" '
             f'fill="url(#sGlow)" transform="rotate(-16 {CX} {CY})"/>')

    random.seed(7)
    for _ in range(120):
        x = random.uniform(0, W)
        y = random.uniform(0, H)
        r = random.choice([0.5, 0.7, 0.9, 1.2])
        o = random.uniform(0.15, 0.6)
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#dce8ff" '
                 f'opacity="{o:.2f}"/>')

    # ---- planetary data (compressed radii, true relative periods) --------
    # (name, orbit rx, squash, period-years, radius, colour, start-angle)
    planets = [
        ("Mercury", 62, 0.30, 0.241, 3.2, "#b7a99a", 20),
        ("Venus", 86, 0.30, 0.615, 5.4, "#e6c07a", 137),
        ("Earth", 112, 0.30, 1.000, 5.7, "#4f9cf0", 248),
        ("Mars", 140, 0.30, 1.881, 4.4, "#e06a4a", 312),
        ("Jupiter", 196, 0.32, 11.86, 12.6, "#d9a066", 74),
        ("Saturn", 252, 0.32, 29.45, 10.8, "#e3cf9a", 191),
        ("Uranus", 306, 0.33, 84.02, 7.4, "#8fd6d8", 285),
        ("Neptune", 356, 0.33, 164.8, 7.2, "#5b7cfa", 18),
    ]
    # keep the inner system readable while preserving ordering
    pmin, pmax = 0.241, 164.8
    dmin, dmax = 3.4, 34.0
    for i, (nm, rx, sq, per, rad, col, a0) in enumerate(planets):
        dur = d_for(per)
        ry = rx * sq
        # orbit path
        b.append(
            f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry:.1f}" '
            f'fill="none" stroke="#2a3444" stroke-width="1" opacity="0.75"/>'
        )
        # planet + its own spin marker, moved along the ellipse
        b.append(
            f'<g transform="translate({CX},{CY})">'
            f'<g>'
            f'<animateMotion dur="{dur:.2f}s" repeatCount="indefinite" '
            f'begin="{-a0 / 360 * dur:.2f}s" '
            f'path="M {rx},0 A {rx} {ry:.1f} 0 1 1 {-rx},0 '
            f'A {rx} {ry:.1f} 0 1 1 {rx},0"/>'
            # body
            f'<circle cx="0" cy="0" r="{rad}" fill="{col}"/>'
            # terminator shading
            f'<path d="M 0,{-rad} A {rad} {rad} 0 0 1 0,{rad} '
            f'A {rad * 0.72:.2f} {rad} 0 0 0 0,{-rad} Z" fill="#000" '
            f'opacity="0.34"/>'
            # a surface tick so the spin reads
            f'<rect x="-0.9" y="{-rad}" width="1.8" height="{rad * 0.55:.1f}" '
            f'fill="#000" opacity="0.22">'
            f'<animateTransform attributeName="transform" type="rotate" '
            f'from="0" to="360" dur="{max(1.6, rad * 0.34):.2f}s" '
            f'repeatCount="indefinite"/></rect>'
            f'</g></g>'
        )
        # label
        b.append(
            f'<text x="{CX + rx + 8:.0f}" y="{CY - 6}" font-family="{MONO}" '
            f'font-size="8.5" fill="{MUT}" opacity="0.0">'
            f'<animate attributeName="opacity" values="0;0;0.75;0.75" '
            f'keyTimes="0;0.06;0.12;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'{esc(nm)}</text>'
        )

    # ---- Saturn's rings --------------------------------------------------
    # A separate group on the same orbit and period as Saturn, so the rings
    # stay locked to the planet. Tilted by the orbit's own squash.
    sat = [p for p in planets if p[0] == "Saturn"][0]
    sat_dur = d_for(sat[3])
    b.append(
        f'<g transform="translate({CX},{CY})">'
        f'<g>'
        f'<animateMotion dur="{sat_dur:.2f}s" repeatCount="indefinite" '
        f'begin="{-sat[6] / 360 * sat_dur:.2f}s" '
        f'path="M {sat[1]},0 A {sat[1]} {sat[1] * sat[2]:.1f} 0 1 1 {-sat[1]},0 '
        f'A {sat[1]} {sat[1] * sat[2]:.1f} 0 1 1 {sat[1]},0"/>'
        f'<g transform="rotate(-18) skewX(-14)">'
        f'<ellipse cx="0" cy="0" rx="{sat[4] * 2.05:.1f}" ry="{sat[4] * 0.62:.1f}" '
        f'fill="none" stroke="#e3cf9a" stroke-width="{sat[4] * 0.30:.1f}" '
        f'opacity="0.55"/>'
        f'<ellipse cx="0" cy="0" rx="{sat[4] * 1.62:.1f}" ry="{sat[4] * 0.49:.1f}" '
        f'fill="none" stroke="#c9b887" stroke-width="{sat[4] * 0.16:.1f}" '
        f'opacity="0.4"/>'
        f'</g></g></g>'
    )

    # ---- asteroid belt ---------------------------------------------------
    random.seed(31)
    for _ in range(110):
        a = random.uniform(0, 2 * math.pi)
        rr = random.uniform(160, 182)
        x = CX + math.cos(a) * rr
        y = CY + math.sin(a) * rr * 0.31
        s = random.uniform(0.7, 1.9)
        dur = random.uniform(11, 16)
        b.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s:.1f}" fill="#9aa7b8" '
            f'opacity="{random.uniform(0.3, 0.75):.2f}">'
            f'<animate attributeName="opacity" values="{random.uniform(0.2, 0.5):.2f};'
            f'{random.uniform(0.6, 0.95):.2f};{random.uniform(0.2, 0.5):.2f}" '
            f'dur="{dur:.1f}s" repeatCount="indefinite"/></circle>'
        )

    # ---- sun -------------------------------------------------------------
    b.append(f'<circle cx="{CX}" cy="{CY}" r="118" fill="url(#sCorona)">'
             f'<animate attributeName="r" values="112;126;112" dur="5.5s" '
             f'repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0.75;1;0.75" dur="5.5s" '
             f'repeatCount="indefinite"/></circle>')
    b.append(f'<circle cx="{CX}" cy="{CY}" r="34" fill="url(#sSun)"/>')
    # granulation
    random.seed(3)
    for _ in range(18):
        a = random.uniform(0, 2 * math.pi)
        rr = random.uniform(0, 27)
        x = CX + math.cos(a) * rr
        y = CY + math.sin(a) * rr
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{random.uniform(1.4, 3.6):.1f}" '
                 f'fill="#fff3c4" opacity="{random.uniform(0.15, 0.4):.2f}">'
                 f'<animate attributeName="opacity" '
                 f'values="{random.uniform(0.1, 0.3):.2f};{random.uniform(0.35, 0.6):.2f};'
                 f'{random.uniform(0.1, 0.3):.2f}" dur="{random.uniform(2.2, 5):.1f}s" '
                 f'repeatCount="indefinite"/></circle>')
    # prominences
    for i in range(5):
        a = i * (2 * math.pi / 5) + 0.4
        x1 = CX + math.cos(a) * 33
        y1 = CY + math.sin(a) * 33
        x2 = CX + math.cos(a + 0.24) * 33
        y2 = CY + math.sin(a + 0.24) * 33
        b.append(
            f'<path d="M {x1:.1f},{y1:.1f} Q {CX + math.cos(a + 0.12) * 58:.1f},'
            f'{CY + math.sin(a + 0.12) * 58:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="#ff9d3c" stroke-width="2" '
            f'stroke-linecap="round" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.75;0.15;0.6;0" '
            f'dur="{random.uniform(3.4, 6.2):.1f}s" begin="{i * 0.7:.1f}s" '
            f'repeatCount="indefinite"/></path>'
        )

    # ---- HUD -------------------------------------------------------------
    b.append(f'<text x="24" y="34" font-family="{MONO}" font-size="11" '
             f'fill="{MUT}" letter-spacing="1.6">ORRERY</text>')
    b.append(f'<text x="24" y="54" font-family="{MONO}" font-size="9.5" '
             f'fill="{MUT}" opacity="0.8">periods to scale &#183; radii compressed</text>')
    b.append(f'<text x="{W - 24}" y="{H - 16}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9.5" fill="{MUT}">'
             f'8 planets &#183; 110 belt objects</text>')
    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 3. atom - nucleus with nucleon jitter, four shells, photon emission
# ---------------------------------------------------------------------------
def atom():
    W, H = 800, 520
    CX, CY = 400, 258
    CYCLE = 11.0

    b = []
    defs = [
        '<radialGradient id="aNuc" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="#ffd9a0" stop-opacity="0.55"/>'
        f'<stop offset="0.6" stop-color="#ff8a3c" stop-opacity="0.18"/>'
        f'<stop offset="1" stop-color="#ff6a00" stop-opacity="0"/>'
        '</radialGradient>',
        '<radialGradient id="aCloud" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="#58a6ff" stop-opacity="0.16"/>'
        f'<stop offset="1" stop-color="#58a6ff" stop-opacity="0"/>'
        '</radialGradient>',
    ]

    b.append(f'<rect width="{W}" height="{H}" fill="#06080f"/>')
    b.append(f'<circle cx="{CX}" cy="{CY}" r="250" fill="url(#aCloud)"/>')

    # ---- electron shells -------------------------------------------------
    shells = [
        (78, 2, 3.6, BLUE),
        (124, 4, 5.4, CYAN),
        (172, 6, 7.6, PURPLE),
        (222, 8, 10.2, TEAL),
    ]
    random.seed(17)
    for si, (r, nelec, dur, col) in enumerate(shells):
        # shell ring, drawn as a slightly squashed ellipse for depth
        b.append(
            f'<ellipse cx="{CX}" cy="{CY}" rx="{r}" ry="{r * 0.94:.1f}" '
            f'fill="none" stroke="{col}" stroke-width="1" opacity="0.22" '
            f'stroke-dasharray="3 5"/>'
        )
        # standing-wave hint along the shell
        b.append(
            f'<ellipse cx="{CX}" cy="{CY}" rx="{r}" ry="{r * 0.94:.1f}" '
            f'fill="none" stroke="{col}" stroke-width="2.4" opacity="0.12" '
            f'stroke-dasharray="{2 * math.pi * r / (nelec * 2):.1f} '
            f'{2 * math.pi * r / (nelec * 2):.1f}">'
            f'<animate attributeName="stroke-dashoffset" from="0" '
            f'to="{-2 * math.pi * r / nelec:.1f}" dur="{dur:.1f}s" '
            f'repeatCount="indefinite"/></ellipse>'
        )
        # electrons, each phase-offset around the shell
        for k in range(nelec):
            a0 = 360.0 * k / nelec + si * 23
            b.append(
                f'<g transform="translate({CX},{CY})">'
                f'<g>'
                f'<animateTransform attributeName="transform" type="rotate" '
                f'from="{a0:.1f}" to="{a0 + 360:.1f}" dur="{dur:.1f}s" '
                f'repeatCount="indefinite"/>'
                f'<circle cx="{r}" cy="0" r="9" fill="{col}" opacity="0.14"/>'
                f'<circle cx="{r}" cy="0" r="4.6" fill="{col}"/>'
                f'<circle cx="{r - 1.3:.1f}" cy="-1.3" r="1.6" fill="#ffffff" '
                f'opacity="0.85"/>'
                f'</g></g>'
            )
        # label
        b.append(
            f'<text x="{CX + 6}" y="{CY - r - 6}" font-family="{MONO}" '
            f'font-size="9" fill="{col}" opacity="0.55">n={si + 1}</text>'
        )

    # ---- photon emission: a quantum drops and spits a photon ------------
    for i in range(3):
        t0 = 1.2 + i * 3.4
        # electron that jumps
        b.append(
            f'<g transform="translate({CX},{CY})">'
            f'<g>'
            f'<animateTransform attributeName="transform" type="rotate" '
            f'from="{200 + i * 40}" to="{200 + i * 40 + 360}" '
            f'dur="{9.0 + i:.1f}s" repeatCount="indefinite"/>'
            f'<circle cx="172" cy="0" r="4.6" fill="{PURPLE}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0.15;0.15;0" '
            f'keyTimes="0;{(t0 - 0.5) / CYCLE:.3f};{t0 / CYCLE:.3f};'
            f'{(t0 + 0.28) / CYCLE:.3f};{(t0 + 0.4) / CYCLE:.3f};'
            f'{(t0 + 1.6) / CYCLE:.3f};1" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></circle>'
            f'</g></g>'
        )
        # photon: a wavy packet flying outward
        pl = []
        for s in range(16):
            x = 236 + s * 15
            y = math.sin(s * 0.9) * 5
            pl.append(f"{x:.1f},{CY + y:.1f}" if s == 0 else f"{x:.1f},{CY + y:.1f}")
        b.append(
            f'<circle cx="{CX + 236}" cy="{CY}" r="3.4" fill="#fff8d0" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0.9;0;0" '
            f'keyTimes="0;{t0 / CYCLE:.3f};{(t0 + 0.06) / CYCLE:.3f};'
            f'{(t0 + 0.5) / CYCLE:.3f};{(t0 + 0.9) / CYCLE:.3f};1" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 0;250 -40;250 -40" '
            f'keyTimes="0;{t0 / CYCLE:.3f};{(t0 + 0.9) / CYCLE:.3f};1" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></circle>'
        )

    # ---- nucleus: packed nucleons with independent jitter ----------------
    b.append(f'<circle cx="{CX}" cy="{CY}" r="72" fill="url(#aNuc)">'
             f'<animate attributeName="r" values="68;76;68" dur="4.2s" '
             f'repeatCount="indefinite"/></circle>')
    random.seed(41)
    nucleons = []
    for i in range(22):
        # sunflower packing inside r=26
        rr = 26 * math.sqrt((i + 0.5) / 22)
        aa = i * 2.39996
        nucleons.append((math.cos(aa) * rr, math.sin(aa) * rr))
    for i, (nx, ny) in enumerate(nucleons):
        prot = i % 2 == 0
        col = "#ff8a5c" if prot else "#8fa4bd"
        jx = random.uniform(1.4, 3.2)
        jy = random.uniform(1.4, 3.2)
        jd = random.uniform(0.9, 1.9)
        b.append(
            f'<g transform="translate({CX + nx:.2f},{CY + ny:.2f})">'
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{jx:.1f} {-jy:.1f};{-jx:.1f} {jy:.1f};0 0" '
            f'dur="{jd:.2f}s" repeatCount="indefinite"/>'
            f'<circle cx="0" cy="0" r="7.4" fill="{col}" opacity="0.95"/>'
            f'<circle cx="-2.2" cy="-2.4" r="2.6" fill="#ffffff" opacity="0.33"/>'
            f'</g></g>'
        )

    # ---- HUD -------------------------------------------------------------
    b.append(f'<text x="24" y="34" font-family="{MONO}" font-size="11" '
             f'fill="{MUT}" letter-spacing="1.6">ATOMIC MODEL</text>')
    b.append(f'<text x="24" y="54" font-family="{MONO}" font-size="9.5" '
             f'fill="{MUT}" opacity="0.8">22 nucleons &#183; 20 electrons</text>')
    # legend
    for i, (lbl, col) in enumerate((("proton", "#ff8a5c"), ("neutron", "#8fa4bd"))):
        x = 24 + i * 96
        b.append(f'<circle cx="{x + 5}" cy="{H - 26}" r="4.5" fill="{col}"/>')
        b.append(f'<text x="{x + 15}" y="{H - 22}" font-family="{MONO}" '
                 f'font-size="9" fill="{MUT}">{lbl}</text>')
    b.append(f'<text x="{W - 24}" y="{H - 22}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9.5" fill="{MUT}">'
             f'4 shells &#183; photon emission</text>')
    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 4. radar - plan-position indicator: phosphor sweep, contacts, velocity
# ---------------------------------------------------------------------------
def radar():
    W, H = 800, 520
    CX, CY = 400, 262
    R = 208
    SWEEP = 4.2

    b = []
    defs = [
        '<radialGradient id="dScope" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="#062515"/>'
        f'<stop offset="0.72" stop-color="#04180d"/>'
        f'<stop offset="1" stop-color="#020c07"/>'
        '</radialGradient>',
        '<radialGradient id="dVig" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0.55" stop-color="#000" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#000" stop-opacity="0.55"/>'
        '</radialGradient>',
        '<linearGradient id="dTrail" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{GREEN}" stop-opacity="0.34"/>'
        f'<stop offset="1" stop-color="{GREEN}" stop-opacity="0"/>'
        '</linearGradient>',
    ]

    b.append(f'<rect width="{W}" height="{H}" fill="#040a07"/>')
    b.append(f'<circle cx="{CX}" cy="{CY}" r="{R + 26}" fill="url(#dScope)"/>')

    # ---- scope furniture -------------------------------------------------
    b.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" '
             f'stroke="{GREEN}" stroke-width="1.6" opacity="0.55"/>')
    for frac in (0.25, 0.5, 0.75):
        b.append(f'<circle cx="{CX}" cy="{CY}" r="{R * frac:.1f}" fill="none" '
                 f'stroke="{GREEN}" stroke-width="0.9" opacity="0.22"/>')
    # cross-hairs
    b.append(f'<g stroke="{GREEN}" stroke-width="0.9" opacity="0.2">'
             f'<line x1="{CX - R}" y1="{CY}" x2="{CX + R}" y2="{CY}"/>'
             f'<line x1="{CX}" y1="{CY - R}" x2="{CX}" y2="{CY + R}"/>'
             f'</g>')
    # bearing ticks every 5 degrees, longer every 30
    ticks = []
    for deg in range(0, 360, 5):
        a = math.radians(deg - 90)
        major = deg % 30 == 0
        r1 = R - (14 if major else 7)
        x1 = CX + math.cos(a) * r1
        y1 = CY + math.sin(a) * r1
        x2 = CX + math.cos(a) * R
        y2 = CY + math.sin(a) * R
        ticks.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{GREEN}" stroke-width="{1.4 if major else 0.8}" '
            f'opacity="{0.5 if major else 0.26}"/>'
        )
        if deg % 90 == 0:
            lr = R + 15
            lx = CX + math.cos(a) * lr
            ly = CY + math.sin(a) * lr + 3.5
            lbl = {0: "000", 90: "090", 180: "180", 270: "270"}[deg]
            ticks.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                f'font-family="{MONO}" font-size="9" fill="{MUT}">{lbl}</text>'
            )
    b.append("".join(ticks))

    # ---- phosphor sweep with a decaying trail ---------------------------
    b.append(f'<g transform="translate({CX},{CY})">')
    b.append(f'<g>')
    b.append(f'<animateTransform attributeName="transform" type="rotate" '
             f'from="0" to="360" dur="{SWEEP}s" repeatCount="indefinite"/>')
    NW = 14
    for i in range(NW):
        a0 = -i * (360.0 / NW) * 0.30
        a1 = a0 - (360.0 / NW) * 0.30
        p0 = (math.cos(math.radians(a0 - 90)) * R, math.sin(math.radians(a0 - 90)) * R)
        p1 = (math.cos(math.radians(a1 - 90)) * R, math.sin(math.radians(a1 - 90)) * R)
        op = 0.30 * (1 - i / NW) ** 1.5
        b.append(
            f'<path d="M 0,0 L {p0[0]:.1f},{p0[1]:.1f} '
            f'A {R} {R} 0 0 1 {p1[0]:.1f},{p1[1]:.1f} Z" '
            f'fill="{GREEN}" opacity="{op:.3f}"/>'
        )
    # leading edge
    b.append(f'<line x1="0" y1="0" x2="0" y2="{-R}" stroke="{TEAL}" '
             f'stroke-width="2" opacity="0.75"/>')
    b.append(f'<line x1="0" y1="0" x2="0" y2="{-R}" stroke="#eafff4" '
             f'stroke-width="0.9" opacity="0.9"/>')
    b.append('</g></g>')

    # ---- contacts --------------------------------------------------------
    # (bearing deg, range frac, closing speed, label, kind)
    contacts = [
        (38, 0.72, +1, "UNK-2041", "air"),
        (127, 0.44, -1, "UNK-1187", "air"),
        (211, 0.86, +1, "UNK-3390", "air"),
        (296, 0.58, -1, "UNK-0925", "air"),
        (334, 0.28, +1, "UNK-7712", "air"),
        (82, 0.93, 0, "SURF-04", "sea"),
    ]
    for bi, (brg, rf, closing, lbl, kind) in enumerate(contacts):
        rr = R * rf
        a = math.radians(brg - 90)
        # drift the contact slowly along its bearing as the sweep finds it
        x = CX + math.cos(a) * rr
        y = CY + math.sin(a) * rr
        # time within the sweep at which the beam crosses this bearing
        hit = (brg / 360.0) * SWEEP
        # blip: bright when painted, then decays until the next pass
        decay = 0.55
        blip_t = [0, max(0.0, hit - 0.05), hit, hit + decay * 0.4,
                  hit + decay, SWEEP]
        halo_t = [0, max(0.0, hit - 0.05), hit, hit + 0.3, SWEEP]
        lbl_t = [0, max(0.0, hit - 0.05), hit, hit + 0.35, hit + decay, SWEEP]
        b.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{TEAL}" '
            f'opacity="0">'
            f'<animate attributeName="opacity" '
            f'values="0;0;1;0.75;0.05;0" '
            f'keyTimes="{kt(blip_t, SWEEP)}" '
            f'dur="{SWEEP}s" repeatCount="indefinite"/>'
            f'<animate attributeName="r" values="2.6;2.6;4.6;3.6;2.6;2.6" '
            f'keyTimes="{kt(blip_t, SWEEP)}" '
            f'dur="{SWEEP}s" repeatCount="indefinite"/></circle>'
        )
        # halo
        b.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="none" '
            f'stroke="{TEAL}" stroke-width="1" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.55;0;0" '
            f'keyTimes="{kt(halo_t, SWEEP)}" '
            f'dur="{SWEEP}s" repeatCount="indefinite"/>'
            f'<animate attributeName="r" values="4;4;15;22;22" '
            f'keyTimes="{kt(halo_t, SWEEP)}" '
            f'dur="{SWEEP}s" repeatCount="indefinite"/></circle>'
        )
        # velocity leader
        if closing:
            vx = -math.cos(a) * 22 * closing
            vy = -math.sin(a) * 22 * closing
            b.append(
                f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + vx:.1f}" y2="{y + vy:.1f}" '
                f'stroke="{TEAL}" stroke-width="1.2" opacity="0.5" '
                f'stroke-linecap="round"/>'
            )
        # label only on the two strongest paints
        if bi < 3:
            b.append(
                f'<text x="{x + 9:.1f}" y="{y - 7:.1f}" font-family="{MONO}" '
                f'font-size="8" fill="{TEAL}" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;0.8;0.45;0;0" '
                f'keyTimes="{kt(lbl_t, SWEEP)}" '
                f'dur="{SWEEP}s" repeatCount="indefinite"/>{esc(lbl)}</text>'
            )

    # ---- receiver noise --------------------------------------------------
    random.seed(53)
    for _ in range(70):
        a = random.uniform(0, 2 * math.pi)
        rr = R * math.sqrt(random.uniform(0.02, 1.0))
        x = CX + math.cos(a) * rr
        y = CY + math.sin(a) * rr
        b.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{random.uniform(0.5, 1.1):.1f}" '
            f'fill="{GREEN}" opacity="0">'
            f'<animate attributeName="opacity" '
            f'values="0;{random.uniform(0.05, 0.3):.2f};0" '
            f'dur="{random.uniform(1.4, 4.5):.1f}s" '
            f'begin="{random.uniform(0, 4):.1f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    # ---- scope glass + HUD ----------------------------------------------
    b.append(f'<circle cx="{CX}" cy="{CY}" r="{R + 26}" fill="url(#dVig)"/>')
    b.append(f'<circle cx="{CX}" cy="{CY}" r="3" fill="{TEAL}" opacity="0.9"/>')
    b.append(f'<text x="24" y="34" font-family="{MONO}" font-size="11" '
             f'fill="{GREEN}" letter-spacing="1.6" opacity="0.85">PPI SCOPE</text>')
    b.append(f'<text x="24" y="54" font-family="{MONO}" font-size="9.5" '
             f'fill="{MUT}">range 40 km &#183; {SWEEP}s sweep</text>')
    b.append(f'<text x="{W - 24}" y="{H - 16}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9.5" fill="{MUT}">'
             f'6 contacts &#183; phosphor decay</text>')
    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 5. moon - Earth-Moon system with a real terminator and crater relief
# ---------------------------------------------------------------------------
def _shadow_polygon(R, p, n_limb=22, n_term=15):
    """Outline of the unlit region at phase p (0=new, 0.5=full, 1=new).

    Built as a polygon rather than an arc path so it can be interpolated with
    calcMode="linear": an <animate> on a path 'd' cannot change the sweep flag,
    and the terminator has to switch limbs half-way through the cycle.
    """
    pts = []
    if p <= 0.5:
        # dark limb is the left half, traversed bottom -> top
        for i in range(n_limb + 1):
            a = math.radians(90 + 180.0 * i / n_limb)
            pts.append((R * math.cos(a), R * math.sin(a)))
        rx = R * math.cos(2 * math.pi * p)
        # terminator returns top -> bottom
        for i in range(1, n_term + 1):
            t = i / n_term
            pts.append((rx * math.sin(math.pi * t), -R * math.cos(math.pi * t)))
    else:
        # dark limb is the right half, traversed top -> bottom
        for i in range(n_limb + 1):
            a = math.radians(-90 + 180.0 * i / n_limb)
            pts.append((R * math.cos(a), R * math.sin(a)))
        rx = R * math.cos(2 * math.pi * (p - 0.5))
        for i in range(1, n_term + 1):
            t = i / n_term
            pts.append((rx * math.sin(math.pi * t), R * math.cos(math.pi * t)))
    return pts


def moon():
    W, H = 800, 520
    CX, CY = 400, 250
    ORX, ORY = 236, 126      # lunar orbit, seen at an inclination
    R = 56                   # lunar radius (drawn large so phases read)
    CYCLE = 24.0             # one synodic month

    b = []
    defs = [
        '<radialGradient id="mMoon" cx="0.38" cy="0.34" r="0.72">'
        f'<stop offset="0" stop-color="#f4f1e8"/>'
        f'<stop offset="0.55" stop-color="#d8d3c6"/>'
        f'<stop offset="1" stop-color="#a9a396"/>'
        '</radialGradient>',
        '<radialGradient id="mEarth" cx="0.36" cy="0.32" r="0.75">'
        f'<stop offset="0" stop-color="#6fc3ff"/>'
        f'<stop offset="0.5" stop-color="#2b7fd4"/>'
        f'<stop offset="1" stop-color="#123a68"/>'
        '</radialGradient>',
        '<radialGradient id="mEarthGlow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0.5" stop-color="#4fa8ff" stop-opacity="0.4"/>'
        f'<stop offset="1" stop-color="#4fa8ff" stop-opacity="0"/>'
        '</radialGradient>',
        '<radialGradient id="mShadow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="#02040a" stop-opacity="0.93"/>'
        f'<stop offset="1" stop-color="#02040a" stop-opacity="0.99"/>'
        '</radialGradient>',
    ]

    b.append(f'<rect width="{W}" height="{H}" fill="#04060d"/>')

    # ---- starfield -------------------------------------------------------
    random.seed(67)
    for _ in range(140):
        x = random.uniform(0, W)
        y = random.uniform(0, H)
        r = random.choice([0.5, 0.7, 0.9, 1.2, 1.5])
        o = random.uniform(0.15, 0.7)
        dur = random.uniform(2.8, 7.5)
        b.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#e8f0ff" '
            f'opacity="{o:.2f}">'
            f'<animate attributeName="opacity" values="{o:.2f};'
            f'{min(1.0, o + 0.3):.2f};{o:.2f}" dur="{dur:.2f}s" '
            f'repeatCount="indefinite"/></circle>'
        )

    # ---- lunar orbit -----------------------------------------------------
    b.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{ORX}" ry="{ORY}" '
             f'fill="none" stroke="#2b3547" stroke-width="1" '
             f'stroke-dasharray="4 6" opacity="0.8"/>')
    # direction arrowheads on the orbit
    for k in range(4):
        a = math.radians(45 + k * 90)
        x = CX + math.cos(a) * ORX
        y = CY + math.sin(a) * ORY
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="#3d4a60"/>')

    # ---- Earth -----------------------------------------------------------
    b.append(f'<circle cx="{CX}" cy="{CY}" r="76" fill="url(#mEarthGlow)">'
             f'<animate attributeName="r" values="72;82;72" dur="6.5s" '
             f'repeatCount="indefinite"/></circle>')
    b.append(f'<circle cx="{CX}" cy="{CY}" r="34" fill="url(#mEarth)"/>')
    # continents (stylised, clipped to the disc)
    b.append(f'<clipPath id="mEarthClip"><circle cx="{CX}" cy="{CY}" r="34"/></clipPath>')
    cont = [
        f'M {CX - 22},{CY - 14} q 9,-7 17,-2 q 6,4 1,10 q -7,7 -14,2 q -6,-4 -4,-10 Z',
        f'M {CX + 2},{CY + 2} q 10,-3 13,5 q 2,8 -6,11 q -9,2 -10,-6 q -1,-7 3,-10 Z',
        f'M {CX - 12},{CY + 12} q 7,-2 8,5 q 0,6 -6,6 q -6,-1 -5,-6 q 0,-4 3,-5 Z',
    ]
    for i, d in enumerate(cont):
        b.append(f'<path d="{d}" fill="#3f9a5c" opacity="0.85" '
                 f'clip-path="url(#mEarthClip)">'
                 f'<animate attributeName="opacity" values="0.7;0.95;0.7" '
                 f'dur="{5 + i}s" repeatCount="indefinite"/></path>')
    # cloud swirls
    for i in range(5):
        a = random.uniform(0, 2 * math.pi)
        rr = random.uniform(8, 30)
        x = CX + math.cos(a) * rr
        y = CY + math.sin(a) * rr
        b.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{random.uniform(5, 11):.1f}" '
                 f'ry="{random.uniform(2, 4):.1f}" fill="#ffffff" opacity="0.3" '
                 f'clip-path="url(#mEarthClip)">'
                 f'<animate attributeName="opacity" values="0.12;0.4;0.12" '
                 f'dur="{random.uniform(4, 8):.1f}s" repeatCount="indefinite"/>'
                 f'</ellipse>')
    # night-side shading
    b.append(f'<circle cx="{CX}" cy="{CY}" r="34" fill="#02040a" opacity="0.42" '
             f'clip-path="url(#mEarthClip)"/>')
    b.append(f'<circle cx="{CX}" cy="{CY}" r="34" fill="none" '
             f'stroke="#8fd0ff" stroke-width="1" opacity="0.45"/>')

    # ---- the Moon, riding the orbit -------------------------------------
    # local origin = moon centre; the phase shadow is drawn in local coords
    pts = _shadow_polygon(R, 0.0)
    shadow_pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    key_phases = [i / 24.0 for i in range(25)]
    shadow_vals = []
    for p in key_phases:
        pp = _shadow_polygon(R, p)
        shadow_vals.append(" ".join(f"{x:.2f},{y:.2f}" for x, y in pp))

    craters = []
    random.seed(83)
    for _ in range(16):
        a = random.uniform(0, 2 * math.pi)
        rr = R * 0.82 * math.sqrt(random.uniform(0, 1))
        x = math.cos(a) * rr
        y = math.sin(a) * rr
        cr = random.uniform(2.2, 7.2)
        craters.append((x, y, cr))
    # maria: a few large dark patches
    maria = [(-14, -12, 15), (10, 6, 12), (-4, 18, 9)]

    moon_body = [
        f'<circle cx="0" cy="0" r="{R}" fill="url(#mMoon)"/>',
    ]
    for mx, my, mr in maria:
        moon_body.append(
            f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="#8f8a7d" opacity="0.3"/>'
        )
    for x, y, cr in craters:
        moon_body.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{cr:.1f}" fill="#b3ac9d" '
            f'opacity="0.55"/>'
        )
        # rim highlight
        moon_body.append(
            f'<path d="M {x - cr:.1f},{y:.1f} A {cr:.1f} {cr:.1f} 0 0 1 '
            f'{x + cr:.1f},{y:.1f}" fill="none" stroke="#f2eee2" '
            f'stroke-width="1.1" opacity="0.5"/>'
        )
    # the unlit region
    moon_body.append(
        f'<polygon points="{shadow_pts}" fill="url(#mShadow)" opacity="0.97">'
        f'<animate attributeName="points" values="{";".join(shadow_vals)}" '
        f'calcMode="linear" dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'</polygon>'
    )
    # earthshine on the dark limb
    moon_body.append(
        f'<circle cx="0" cy="0" r="{R}" fill="#5f7fa8" opacity="0.05"/>'
    )
    # limb
    moon_body.append(
        f'<circle cx="0" cy="0" r="{R}" fill="none" stroke="#f0ece0" '
        f'stroke-width="0.9" opacity="0.4"/>'
    )

    b.append(f'<g transform="translate({CX},{CY})">')
    # libration: a slow wobble composed *outside* the motion group, because a
    # child animateTransform would replace the parent's transform attribute.
    b.append('<g>')
    b.append('<animateTransform attributeName="transform" type="rotate" '
             'values="-3.2;2.6;-1.4;3.0;-3.2" '
             'keyTimes="0;0.27;0.52;0.78;1" '
             f'dur="{CYCLE}s" repeatCount="indefinite" additive="sum"/>')
    b.append(f'<g>')
    b.append(f'<animateMotion dur="{CYCLE}s" repeatCount="indefinite" '
             f'path="M {ORX},0 A {ORX} {ORY} 0 1 1 {-ORX},0 '
             f'A {ORX} {ORY} 0 1 1 {ORX},0"/>')
    b.append("".join(moon_body))
    b.append('</g>')
    b.append('</g>')
    b.append('</g>')

    # ---- phase caption ---------------------------------------------------
    # Eight labels, each shown for its own window; the cycle wraps, so the
    # last window simply ends at 1.0 instead of repeating "New Moon".
    phase_names = [
        (0.000, "New Moon"), (0.125, "Waxing Crescent"),
        (0.250, "First Quarter"), (0.375, "Waxing Gibbous"),
        (0.500, "Full Moon"), (0.625, "Waning Gibbous"),
        (0.750, "Last Quarter"), (0.875, "Waning Crescent"),
    ]
    for i, (p, nm) in enumerate(phase_names):
        w0 = p
        w1 = phase_names[i + 1][0] if i + 1 < len(phase_names) else 1.0
        ramp = 0.010
        times = [w0 * CYCLE, (w0 + ramp) * CYCLE,
                 max((w0 + ramp) * CYCLE, (w1 - ramp) * CYCLE),
                 w1 * CYCLE, CYCLE]
        b.append(
            f'<text x="{CX}" y="{H - 44}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="12" fill="{TXT}" '
            f'letter-spacing="1.4" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;1;0;0" '
            f'keyTimes="{kt(times, CYCLE)}" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/>{esc(nm)}</text>'
        )

    # ---- HUD -------------------------------------------------------------
    b.append(f'<text x="24" y="34" font-family="{MONO}" font-size="11" '
             f'fill="{MUT}" letter-spacing="1.6">EARTH &#183; MOON</text>')
    b.append(f'<text x="24" y="54" font-family="{MONO}" font-size="9.5" '
             f'fill="{MUT}" opacity="0.85">synodic month &#183; '
             f'true terminator</text>')
    # illumination readout: a percentage counter that tracks the terminator
    illum_steps = 24
    for i in range(illum_steps):
        p = i / illum_steps
        pct = (1 - math.cos(2 * math.pi * p)) / 2 * 100
        t0 = p * CYCLE
        t1 = (i + 1) / illum_steps * CYCLE
        a = max(0.0, t0 / CYCLE)
        bb = min(1.0, t1 / CYCLE)
        if bb <= a:
            continue
        b.append(
            f'<text x="{W - 24}" y="54" text-anchor="end" '
            f'font-family="{MONO}" font-size="9.5" fill="{TEAL}" '
            f'opacity="0">{pct:.0f}% lit'
            f'<animate attributeName="opacity" values="0;1;1;0" '
            f'keyTimes="{kt([0, t0, t1, CYCLE], CYCLE)}" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></text>'
        )
    # illumination bar
    b.append(f'<rect x="{W - 148}" y="{H - 30}" width="124" height="5" '
             f'rx="2.5" fill="#1b2330"/>')
    b.append(f'<rect x="{W - 148}" y="{H - 30}" width="0" height="5" rx="2.5" '
             f'fill="{TEAL}" opacity="0.8">'
             f'<animate attributeName="width" values="0;6;23;41;58;74;87;96;100;'
             f'96;87;74;58;41;23;6;0" '
             f'keyTimes="{kt([i / 16 * CYCLE for i in range(17)], CYCLE)}" '
             f'dur="{CYCLE}s" repeatCount="indefinite"/></rect>')
    b.append(f'<text x="{W - 24}" y="{H - 16}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9.5" fill="{MUT}">'
             f'16 craters &#183; 3 maria &#183; libration</text>')
    return svg(W, H, "".join(b), "".join(defs))


def main():
    print("generating scene widgets:")
    save("rocket.svg", rocket())
    save("solar.svg", solar())
    save("atom.svg", atom())
    # radar.svg is intentionally not written: the user removed it from the
    # README, and leaving the generator wired would resurrect the asset.
    save("moon.svg", moon())
    print("done.")


if __name__ == "__main__":
    main()