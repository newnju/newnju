#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Second batch of scene widgets: coffee, pacman, octocat, day/night cycle.

Same rules as generate_scenes.py: pure SMIL, authored at the size they are
displayed at, geometry computed rather than hand-placed.

These four were the weak half of the "Music / Coffee / Pac-Man / Octocat /
Day-Night" group. music.svg was already fine, so it is left untouched; the
other four were each drawn in a 200-320 unit viewBox and upscaled roughly 3x
to 800px, with 4-10 animations apiece, so every edge was soft and the motion
was a couple of shapes sliding about.

Run:  python scripts/generate_scenes2.py
Out:  assets/{coffee,pacman,octocat,daynight}.svg
"""

import math
import random
from pathlib import Path

from generate_scenes import (ASSETS, BG, BORDER, CARD, CYAN, FONT, GREEN, MUT,
                             MONO, ORANGE, PINK, PURPLE, RED, TEAL, TXT, YELLOW,
                             BLUE, esc, kt, save, svg)

# brewed-coffee palette
CREMA = "#c68a4e"
CREMA_DK = "#8a5a2b"
CREAM = "#e8c9a0"
SAUCER = "#1b2431"


# ---------------------------------------------------------------------------
# 1. coffee - cup, crema, latte art, ripples, bubbles, steam
# ---------------------------------------------------------------------------
def coffee():
    W, H = 800, 520
    CX, CY = 400, 296           # rim centre
    RX, RY = 150, 52            # rim radii
    CYCLE = 9.0

    b = []
    defs = [
        '<radialGradient id="cRoom" cx="0.5" cy="0.42" r="0.72">'
        f'<stop offset="0" stop-color="#2a2118"/>'
        f'<stop offset="0.55" stop-color="#1a1410"/>'
        f'<stop offset="1" stop-color="#0b0908"/>'
        '</radialGradient>',
        '<radialGradient id="cCrema" cx="0.42" cy="0.36" r="0.72">'
        f'<stop offset="0" stop-color="{CREAM}"/>'
        f'<stop offset="0.42" stop-color="{CREMA}"/>'
        f'<stop offset="0.82" stop-color="{CREMA_DK}"/>'
        f'<stop offset="1" stop-color="#5c3a1a"/>'
        '</radialGradient>',
        '<linearGradient id="cCup" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#6d7683"/>'
        f'<stop offset="0.22" stop-color="#eef2f7"/>'
        f'<stop offset="0.55" stop-color="#cfd7e1"/>'
        f'<stop offset="0.82" stop-color="#9aa4b2"/>'
        f'<stop offset="1" stop-color="#5d6672"/>'
        '</linearGradient>',
        '<linearGradient id="cSaucer" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#2b3746"/>'
        f'<stop offset="1" stop-color="#141b25"/>'
        '</linearGradient>',
        '<radialGradient id="cGlow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="#ffb85c" stop-opacity="0.20"/>'
        f'<stop offset="1" stop-color="#ffb85c" stop-opacity="0"/>'
        '</radialGradient>',
    ]

    # ---- room / table ----------------------------------------------------
    b.append(f'<rect width="{W}" height="{H}" fill="url(#cRoom)"/>')
    b.append(f'<ellipse cx="{CX}" cy="{CY - 40}" rx="330" ry="230" '
             f'fill="url(#cGlow)"/>')
    # table edge
    b.append(f'<rect x="0" y="{H - 74}" width="{W}" height="74" '
             f'fill="#120e0b" opacity="0.85"/>')
    b.append(f'<rect x="0" y="{H - 74}" width="{W}" height="2" fill="#3a2c20"/>')

    # ---- saucer ----------------------------------------------------------
    b.append(f'<ellipse cx="{CX}" cy="{CY + 118}" rx="228" ry="62" '
             f'fill="#0a0d12" opacity="0.55"/>')
    b.append(f'<ellipse cx="{CX}" cy="{CY + 112}" rx="222" ry="58" '
             f'fill="url(#cSaucer)" stroke="#39465a" stroke-width="1.5"/>')
    b.append(f'<ellipse cx="{CX}" cy="{CY + 106}" rx="150" ry="38" '
             f'fill="#101720" opacity="0.85"/>')
    b.append(f'<ellipse cx="{CX}" cy="{CY + 104}" rx="150" ry="38" fill="none" '
             f'stroke="#2f3d4f" stroke-width="1.2" opacity="0.9"/>')

    # ---- cup body --------------------------------------------------------
    # front outer wall: left rim -> bottom -> right rim
    b.append(
        f'<path d="M {CX - RX},{CY} '
        f'C {CX - RX + 4},{CY + 74} {CX - 96},{CY + 112} {CX},{CY + 112} '
        f'C {CX + 96},{CY + 112} {CX + RX - 4},{CY + 74} {CX + RX},{CY} Z" '
        f'fill="url(#cCup)"/>'
    )
    # side shading
    b.append(
        f'<path d="M {CX - RX},{CY} '
        f'C {CX - RX + 4},{CY + 74} {CX - 96},{CY + 112} {CX},{CY + 112} '
        f'Z" fill="#000" opacity="0.16"/>'
    )
    # handle (behind rim, on the right)
    b.append(
        f'<path d="M {CX + RX - 12},{CY + 26} '
        f'C {CX + RX + 66},{CY + 22} {CX + RX + 78},{CY + 74} '
        f'{CX + RX + 40},{CY + 92} '
        f'C {CX + RX + 16},{CY + 102} {CX + RX - 2},{CY + 96} '
        f'{CX + RX - 10},{CY + 84}" '
        f'fill="none" stroke="#aeb8c6" stroke-width="17" stroke-linecap="round"/>'
        f'<path d="M {CX + RX - 12},{CY + 26} '
        f'C {CX + RX + 66},{CY + 22} {CX + RX + 78},{CY + 74} '
        f'{CX + RX + 40},{CY + 92}" '
        f'fill="none" stroke="#eef2f7" stroke-width="6" stroke-linecap="round" '
        f'opacity="0.55"/>'
    )
    # rim
    b.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" '
             f'fill="#c8d0da"/>')
    b.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{RX - 7}" ry="{RY - 5}" '
             f'fill="#8d96a3"/>')
    # coffee surface
    b.append(f'<ellipse cx="{CX}" cy="{CY + 2}" rx="{RX - 12}" ry="{RY - 9}" '
             f'fill="url(#cCrema)"/>')

    # ---- crema swirl -----------------------------------------------------
    b.append(f'<g opacity="0.5" transform="translate({CX},{CY + 2})">'
             f'<g>'
             f'<animateTransform attributeName="transform" type="rotate" '
             f'from="0" to="360" dur="34s" repeatCount="indefinite"/>'
             f'<ellipse cx="0" cy="0" rx="86" ry="29" fill="none" '
             f'stroke="{CREAM}" stroke-width="2" opacity="0.30" '
             f'stroke-dasharray="30 22"/>'
             f'<ellipse cx="0" cy="0" rx="56" ry="19" fill="none" '
             f'stroke="#f0d6b0" stroke-width="1.6" opacity="0.24" '
             f'stroke-dasharray="18 14"/>'
             f'</g></g>'
             f'<ellipse cx="{CX}" cy="{CY + 2}" rx="{RX - 12}" ry="{RY - 9}" '
             f'fill="none" stroke="#3a2410" stroke-width="2" opacity="0.5"/>'
             )
    # crema highlight
    b.append(f'<ellipse cx="{CX - 34}" cy="{CY - 12}" rx="52" ry="16" '
             f'fill="#fff" opacity="0.07"/>')

    # ---- latte art rosetta ----------------------------------------------
    art = [f'<g transform="translate({CX},{CY + 2})" opacity="0.62">']
    # stem
    art.append(f'<rect x="-1.6" y="-26" width="3.2" height="52" rx="1.6" '
               f'fill="{CREAM}" opacity="0.75"/>')
    # paired leaves, largest at the base
    for i in range(6):
        y = 22 - i * 9.2
        spread = 9 + i * 3.4
        leaf_h = 7.5 - i * 0.45
        for sgn in (-1, 1):
            art.append(
                f'<path d="M 0,{y:.1f} '
                f'C {sgn * spread * 0.55:.1f},{y - leaf_h:.1f} '
                f'{sgn * spread:.1f},{y - leaf_h * 0.5:.1f} '
                f'{sgn * spread:.1f},{y + 1.2:.1f} '
                f'C {sgn * spread * 0.6:.1f},{y + 2.6:.1f} '
                f'{sgn * spread * 0.25:.1f},{y + 1.8:.1f} 0,{y:.1f} Z" '
                f'fill="{CREAM}" opacity="{0.62 - i * 0.04:.2f}"/>'
            )
    art.append('</g>')
    b.append("".join(art))

    # ---- ripples ---------------------------------------------------------
    for i in range(3):
        t0 = 1.2 + i * 2.6
        b.append(
            f'<ellipse cx="{CX}" cy="{CY + 2}" rx="12" ry="4" fill="none" '
            f'stroke="{CREAM}" stroke-width="1.4" opacity="0">'
            f'<animate attributeName="rx" values="12;120" '
            f'begin="{t0:.1f}s" dur="3.4s" repeatCount="indefinite"/>'
            f'<animate attributeName="ry" values="4;40" '
            f'begin="{t0:.1f}s" dur="3.4s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.5;0.16;0" '
            f'begin="{t0:.1f}s" dur="3.4s" repeatCount="indefinite"/>'
            f'</ellipse>'
        )

    # ---- bubbles ---------------------------------------------------------
    random.seed(97)
    for _ in range(16):
        a = random.uniform(0, 2 * math.pi)
        rr = math.sqrt(random.uniform(0, 1))
        x = CX + math.cos(a) * rr * (RX - 30)
        y = CY + 2 + math.sin(a) * rr * (RY - 16)
        r0 = random.uniform(1.4, 3.6)
        dur = random.uniform(3.2, 6.4)
        delay = random.uniform(0, dur)
        b.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r0:.1f}" '
            f'fill="none" stroke="{CREAM}" stroke-width="1" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.55;0.5;0" '
            f'keyTimes="{kt([0, delay, delay + dur * 0.5, delay + dur], dur + delay)}" '
            f'dur="{dur + delay:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{y:.1f};{y - 14:.1f};{y - 22:.1f}" '
            f'begin="{delay:.2f}s" dur="{dur:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    # ---- steam -----------------------------------------------------------
    random.seed(41)
    for i in range(7):
        x0 = CX - 96 + i * 32
        amp = random.uniform(10, 20)
        rise = random.uniform(150, 205)
        dur = random.uniform(4.2, 6.8)
        delay = random.uniform(0, 4)
        wob = random.uniform(0.7, 1.3)
        # four keyframes of a rising S, returning to the start to close the loop
        frames = []
        for k, f in enumerate((0.0, 0.34, 0.68, 1.0)):
            y = CY - 34 - rise * f
            dx = math.sin(f * 6.0 * wob + i) * amp * (0.35 + f * 0.9)
            frames.append((x0 + dx, y))
        d = (f'M {frames[0][0]:.1f},{frames[0][1]:.1f} '
             + " ".join(
                 f'C {frames[k][0] + math.sin(k * 2.1 + i) * amp * 0.7:.1f},'
                 f'{frames[k][1] + rise * 0.11:.1f} '
                 f'{frames[k + 1][0] - math.cos(k * 1.7 + i) * amp * 0.7:.1f},'
                 f'{frames[k + 1][1] - rise * 0.10:.1f} '
                 f'{frames[k + 1][0]:.1f},{frames[k + 1][1]:.1f}'
                 for k in range(3))
             + ' ' + f'C {frames[3][0]:.1f},{frames[3][1] - 24:.1f} '
               f'{frames[0][0]:.1f},{frames[0][1] - 30:.1f} '
               f'{frames[0][0]:.1f},{frames[0][1]:.1f} Z')
        b.append(
            f'<path d="{d}" fill="none" stroke="#dfe7f2" '
            f'stroke-width="{2.6 - i * 0.12:.1f}" stroke-linecap="round" '
            f'opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.30;0.20;0.06;0;0" '
            f'keyTimes="{kt([0, delay, delay + 0.7, delay + 2.2, delay + 3.6, delay + 4.6, delay + 6], dur + 6)}" '
            f'dur="{dur + 6:.2f}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 6;0 0;0 -8;0 6" '
            f'keyTimes="0;0.35;0.7;1" dur="{dur:.2f}s" repeatCount="indefinite"/>'
            f'</path>'
        )

    # ---- HUD -------------------------------------------------------------
    b.append(f'<text x="26" y="36" font-family="{MONO}" font-size="11" '
             f'fill="{MUT}" letter-spacing="1.7">ESPRESSO</text>')
    b.append(f'<text x="26" y="56" font-family="{MONO}" font-size="9.5" '
             f'fill="{MUT}" opacity="0.85">25s shot &#183; 36 ml &#183; 9 bar</text>')
    # pressure gauge
    b.append(f'<circle cx="{W - 74}" cy="60" r="34" fill="#0d1117" '
             f'stroke="#39465a" stroke-width="2"/>')
    for k in range(9):
        ang = math.radians(-220 + k * 30)
        b.append(
            f'<line x1="{W - 74 + math.cos(ang) * 26:.1f}" '
            f'y1="{60 + math.sin(ang) * 26:.1f}" '
            f'x2="{W - 74 + math.cos(ang) * 31:.1f}" '
            f'y2="{60 + math.sin(ang) * 31:.1f}" '
            f'stroke="{MUT}" stroke-width="1.4" opacity="0.6"/>'
        )
    b.append(f'<g transform="translate({W - 74},60)">'
             f'<g>'
             f'<animateTransform attributeName="transform" type="rotate" '
             f'values="-118;-14;-14;-118" '
             f'keyTimes="{kt([0, 1.4, 7.2, CYCLE], CYCLE)}" '
             f'dur="{CYCLE}s" repeatCount="indefinite"/>'
             f'<line x1="0" y1="4" x2="0" y2="-24" stroke="{ORANGE}" '
             f'stroke-width="2.4" stroke-linecap="round"/>'
             f'</g>'
             f'<circle cx="0" cy="0" r="3.4" fill="{ORANGE}"/>'
             f'</g>')
    b.append(f'<text x="{W - 74}" y="112" text-anchor="middle" '
             f'font-family="{MONO}" font-size="9" fill="{MUT}">9 bar</text>')
    b.append(f'<text x="{W - 26}" y="{H - 22}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9.5" fill="{MUT}">'
             f'crema &#183; latte art &#183; 7 steam wisps</text>')
    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 2. pacman - a real maze: pellets vanish on contact, ghosts patrol
# ---------------------------------------------------------------------------
def pacman():
    W, H = 800, 520
    COLS, ROWS = 19, 11
    CELL = 36
    BX = (W - COLS * CELL) // 2
    BY = 82
    CYCLE = 11.0

    def cc(c, r):
        return (BX + c * CELL + CELL / 2, BY + r * CELL + CELL / 2)

    # ---- maze walls: pillars on even/even cells ------------------------
    walls = []
    for r in range(ROWS):
        for c in range(COLS):
            if c % 2 == 0 and r % 2 == 0:
                x = BX + c * CELL + 5
                y = BY + r * CELL + 5
                walls.append(
                    f'<rect x="{x}" y="{y}" width="{CELL - 10}" '
                    f'height="{CELL - 10}" rx="5" fill="#0a1230" '
                    f'stroke="#2b6cf0" stroke-width="2" opacity="0.9"/>'
                )
    # outer border
    walls.append(
        f'<rect x="{BX - 8}" y="{BY - 8}" width="{COLS * CELL + 16}" '
        f'height="{ROWS * CELL + 16}" rx="10" fill="none" '
        f'stroke="#2b6cf0" stroke-width="2.5" opacity="0.75"/>'
    )

    # ---- serpentine route through the corridors ------------------------
    # Walk each odd row end-to-end, then step DOWN one row at a time through
    # the connector cell. Emitting only the row cells would make pac-man jump
    # two cells (72px) at every turn, which reads as a teleport.
    route = []
    rows = (1, 3, 5, 7, 9)
    for idx, r in enumerate(rows):
        cs = range(1, COLS - 1) if idx % 2 == 0 else range(COLS - 2, 0, -1)
        for c in cs:
            route.append((c, r))
        if idx + 1 < len(rows):
            # connector cell on the way to the next row
            route.append((cs[-1], r + 1))
    pts = [cc(c, r) for c, r in route]

    # cumulative length, so pellets can vanish exactly as pac-man arrives
    seg = [0.0]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        seg.append(seg[-1] + math.hypot(x2 - x1, y2 - y1))
    total = seg[-1]
    speed = total / CYCLE

    path_d = f"M {pts[0][0]:.1f},{pts[0][1]:.1f} " + " ".join(
        f"L {x:.1f},{y:.1f}" for x, y in pts[1:])

    b = []
    defs = [
        '<radialGradient id="pGlow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="#ffd54a" stop-opacity="0.28"/>'
        f'<stop offset="1" stop-color="#ffd54a" stop-opacity="0"/>'
        '</radialGradient>',
    ]
    b.append(f'<rect width="{W}" height="{H}" fill="#05060f"/>')
    b.append(f'<ellipse cx="{W / 2}" cy="{H / 2}" rx="400" ry="250" '
             f'fill="url(#pGlow)" opacity="0.55"/>')
    b.append("".join(walls))

    # ---- pellets ---------------------------------------------------------
    for i, ((x, y), d) in enumerate(zip(pts, seg)):
        t_hit = d / speed
        if i == 0:
            continue
        if i % 7 == 0:
            # power pellet
            b.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{CREAM}" '
                f'opacity="0">'
                f'<animate attributeName="opacity" values="0;1;1;0;0" '
                f'keyTimes="{kt([0, t_hit, t_hit + 0.05, t_hit + 0.2, CYCLE], CYCLE)}" '
                f'dur="{CYCLE}s" repeatCount="indefinite"/>'
                f'</circle>'
            )
            b.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="none" '
                f'stroke="{CREAM}" stroke-width="1.6" opacity="0.55">'
                f'<animate attributeName="r" values="7;10;7" dur="0.9s" '
                f'repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0.55;0.15;0.55" '
                f'dur="0.9s" repeatCount="indefinite"/>'
                f'</circle>'
            )
        else:
            b.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.1" fill="#ffd9a0" '
                f'opacity="0">'
                f'<animate attributeName="opacity" values="0;0.95;0.95;0;0" '
                f'keyTimes="{kt([0, t_hit, t_hit + 0.04, t_hit + 0.14, CYCLE], CYCLE)}" '
                f'dur="{CYCLE}s" repeatCount="indefinite"/>'
                f'</circle>'
            )

    # ---- ghosts ----------------------------------------------------------
    ghost_specs = [
        ("#ff4d5e", 1, 1, 6, 3.6, 0.0),
        ("#ffb14d", 17, 3, 12, 4.2, 0.7),
        ("#4de0ff", 2, 7, 8, 4.8, 1.4),
        ("#ff8ad4", 16, 9, 11, 5.4, 2.1),
    ]
    for col, c0, r, c1, dur, delay in ghost_specs:
        x1, y1 = cc(c0, r)
        x2, y2 = cc(c1, r)
        # patrol back and forth along the row
        b.append(
            f'<g>'
            f'<animateMotion dur="{dur:.1f}s" begin="{-delay:.1f}s" '
            f'repeatCount="indefinite" calcMode="linear" '
            f'keyPoints="0;1;0" keyTimes="0;0.5;1" '
            f'path="M {x1:.1f},{y1:.1f} L {x2:.1f},{y2:.1f}"/>'
            # body
            f'<path d="M -15,12 L -15,-1 A 15 16 0 0 1 15,-1 L 15,12 '
            f'L 10,6 L 5,12 L 0,6 L -5,12 L -10,6 Z" fill="{col}" '
            f'opacity="0.95"/>'
            # eyes
            f'<circle cx="-5.5" cy="-3" r="4.4" fill="#fff"/>'
            f'<circle cx="5.5" cy="-3" r="4.4" fill="#fff"/>'
            f'<circle cx="-4.6" cy="-2.4" r="2.1" fill="#1b2a5e"/>'
            f'<circle cx="6.4" cy="-2.4" r="2.1" fill="#1b2a5e"/>'
            f'</g>'
        )

    # ---- pac-man ---------------------------------------------------------
    # mouth half-angle sweeps 6deg .. 44deg; the arc flags stay identical so
    # SMIL can interpolate the path.
    def mouth(a_deg):
        a = math.radians(a_deg)
        return (f"M 0,0 L {15 * math.cos(a):.2f},{15 * math.sin(a):.2f} "
                f"A 15 15 0 1 1 {15 * math.cos(-a):.2f},{15 * math.sin(-a):.2f} Z")

    b.append(
        f'<g>'
        f'<animateMotion dur="{CYCLE}s" repeatCount="indefinite" '
        f'calcMode="linear" path="{path_d}"/>'
        f'<g>'
        f'<animateTransform attributeName="transform" type="rotate" '
        f'values="0;0;180;180;0;0" '
        f'keyTimes="0;0.19;0.21;0.44;0.46;1" dur="{CYCLE}s" '
        f'repeatCount="indefinite"/>'
        f'<circle cx="0" cy="0" r="24" fill="url(#pGlow)" opacity="0.8"/>'
        f'<path d="{mouth(8)}" fill="{YELLOW}" stroke="#fff3b0" '
        f'stroke-width="1.2">'
        f'<animate attributeName="d" values="{mouth(8)};{mouth(46)};{mouth(8)}" '
        f'dur="0.26s" calcMode="linear" repeatCount="indefinite"/>'
        f'</path>'
        f'</g></g>'
    )

    # ---- HUD -------------------------------------------------------------
    b.append(f'<text x="26" y="40" font-family="{MONO}" font-size="11" '
             f'fill="{YELLOW}" letter-spacing="1.7">1UP</text>')
    b.append(f'<text x="26" y="62" font-family="{MONO}" font-size="14" '
             f'fill="{TXT}">00</text>')
    b.append(f'<text x="{W - 26}" y="40" text-anchor="end" '
             f'font-family="{MONO}" font-size="11" fill="{MUT}" '
             f'letter-spacing="1.4">HIGH SCORE</text>')
    b.append(f'<text x="{W - 26}" y="62" text-anchor="end" '
             f'font-family="{MONO}" font-size="14" fill="{TXT}">3370</text>')
    b.append(f'<text x="{W / 2}" y="{H - 18}" text-anchor="middle" '
             f'font-family="{MONO}" font-size="9.5" fill="{MUT}">'
             f'{len(route)} cells &#183; pellets clear on contact &#183; '
             f'4 ghosts</text>')
    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 3. octocat - full mascot: 8 undulating tentacles, darting eyes, blink
# ---------------------------------------------------------------------------
def octocat():
    W, H = 800, 520
    CX, CY = 400, 246
    R = 96
    CYCLE = 7.0

    b = []
    defs = [
        '<radialGradient id="oBody" cx="0.38" cy="0.32" r="0.78">'
        f'<stop offset="0" stop-color="#ffffff"/>'
        f'<stop offset="0.55" stop-color="#e6ebf2"/>'
        f'<stop offset="1" stop-color="#b3bdcb"/>'
        '</radialGradient>',
        '<radialGradient id="oAura" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0.45" stop-color="#6ea8ff" stop-opacity="0.20"/>'
        f'<stop offset="1" stop-color="#6ea8ff" stop-opacity="0"/>'
        '</radialGradient>',
    ]
    b.append(f'<rect width="{W}" height="{H}" fill="#0a0d14"/>')
    b.append(f'<circle cx="{CX}" cy="{CY}" r="260" fill="url(#oAura)"/>')

    # ---- orbiting glyphs -------------------------------------------------
    glyphs = ["&lt;/&gt;", "{ }", "&#955;", "#", "git", "&#9741;"]
    for i, g in enumerate(glyphs):
        a0 = 360.0 * i / len(glyphs)
        b.append(
            f'<g transform="translate({CX},{CY})">'
            f'<g>'
            f'<animateTransform attributeName="transform" type="rotate" '
            f'from="{a0:.1f}" to="{a0 + 360:.1f}" dur="{26 + i * 3}s" '
            f'repeatCount="indefinite"/>'
            f'<g transform="translate(0,-232)">'
            f'<g>'
            f'<animateTransform attributeName="transform" type="rotate" '
            f'from="0" to="-360" dur="{26 + i * 3}s" repeatCount="indefinite"/>'
            f'<text x="0" y="0" text-anchor="middle" font-family="{MONO}" '
            f'font-size="17" fill="{CYAN}" opacity="0.5">{g}</text>'
            f'</g></g></g></g>'
        )

    # ---- tentacles (8), behind the body ---------------------------------
    # Each is a 3-segment bezier whose control points orbit; phases differ so
    # the wave travels around the body rather than pulsing in unison.
    for i in range(8):
        # fan them across the lower half of the body
        base_ang = math.radians(28 + i * (124 / 7))
        bx = CX + math.cos(base_ang) * (R - 12)
        by = CY + math.sin(base_ang) * (R - 12) * 0.92
        out_ang = base_ang
        length = 96 + (i % 3) * 16
        ph = i * 0.8
        frames = []
        for k in range(5):
            f = k / 4.0
            wob = math.sin(ph + f * 5.0)
            x = bx + math.cos(out_ang) * length * f + wob * 12 * f
            y = by + math.sin(out_ang) * length * f + f * f * 34 + wob * 8 * f
            frames.append((x, y))
        # build a smooth path with 4 cubic segments
        d = f"M {bx:.1f},{by:.1f} "
        d += " ".join(
            f"C {frames[k][0] + math.cos(out_ang + 1.4) * 22 * (1 - k / 4):.1f},"
            f'{frames[k][1] + math.sin(out_ang + 1.4) * 22 * (1 - k / 4) + 8:.1f} '
            f'{frames[k + 1][0] - math.cos(out_ang - 1.2) * 20 * (1 - k / 4):.1f},'
            f'{frames[k + 1][1] - math.sin(out_ang - 1.2) * 20 * (1 - k / 4) - 6:.1f} '
            f'{frames[k + 1][0]:.1f},{frames[k + 1][1]:.1f}'
            for k in range(4)
        )
        # the closed-loop variant: shift the phase by half a wave
        frames2 = []
        for k in range(5):
            f = k / 4.0
            wob = math.sin(ph + 2.6 + f * 5.0)
            x = bx + math.cos(out_ang) * length * f + wob * 12 * f
            y = by + math.sin(out_ang) * length * f + f * f * 34 + wob * 8 * f
            frames2.append((x, y))
        d2 = f"M {bx:.1f},{by:.1f} "
        d2 += " ".join(
            f"C {frames2[k][0] + math.cos(out_ang + 1.4) * 22 * (1 - k / 4):.1f},"
            f'{frames2[k][1] + math.sin(out_ang + 1.4) * 22 * (1 - k / 4) + 8:.1f} '
            f'{frames2[k + 1][0] - math.cos(out_ang - 1.2) * 20 * (1 - k / 4):.1f},'
            f'{frames2[k + 1][1] - math.sin(out_ang - 1.2) * 20 * (1 - k / 4) - 6:.1f} '
            f'{frames2[k + 1][0]:.1f},{frames2[k + 1][1]:.1f}'
            for k in range(4)
        )
        b.append(
            f'<path d="{d}" fill="none" stroke="#cfd7e1" '
            f'stroke-width="{15 - (i % 3) * 1.6:.1f}" stroke-linecap="round" '
            f'opacity="0.96">'
            f'<animate attributeName="d" values="{d};{d2};{d}" '
            f'dur="{3.4 + (i % 4) * 0.45:.2f}s" repeatCount="indefinite"/>'
            f'</path>'
        )
        # sucker dots along the tentacle
        for k in range(3):
            f = 0.34 + k * 0.22
            sx = bx + math.cos(out_ang) * length * f
            sy = by + math.sin(out_ang) * length * f + f * f * 34
            b.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="2.2" '
                     f'fill="#9aa7b8" opacity="0.55"/>')

    # ---- body ------------------------------------------------------------
    b.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#oBody)"/>')
    # ears
    b.append(f'<path d="M {CX - 74},{CY - 62} L {CX - 50},{CY - 104} '
             f'L {CX - 26},{CY - 74} Z" fill="#e6ebf2"/>')
    b.append(f'<path d="M {CX + 74},{CY - 62} L {CX + 50},{CY - 104} '
             f'L {CX + 26},{CY - 74} Z" fill="#e6ebf2"/>')

    # ---- eyes: sclera, darting pupil, blinking lid -----------------------
    for sgn in (-1, 1):
        ex = CX + sgn * 38
        ey = CY - 14
        b.append(f'<ellipse cx="{ex}" cy="{ey}" rx="21" ry="23" fill="#fff"/>')
        # pupil darts around on a slow loop
        b.append(
            f'<g clip-path="none">'
            f'<circle cx="{ex}" cy="{ey}" r="10.5" fill="#1b2430">'
            f'<animate attributeName="cx" '
            f'values="{ex - 4:.1f};{ex + 4:.1f};{ex + 3:.1f};{ex - 3:.1f};{ex - 4:.1f}" '
            f'keyTimes="0;0.26;0.5;0.76;1" dur="{CYCLE}s" '
            f'repeatCount="indefinite"/>'
            f'<animate attributeName="cy" '
            f'values="{ey + 2:.1f};{ey - 3:.1f};{ey + 3:.1f};{ey - 2:.1f};{ey + 2:.1f}" '
            f'keyTimes="0;0.3;0.56;0.8;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'</circle>'
            f'<circle cx="{ex - 3.4:.1f}" cy="{ey - 3.6:.1f}" r="3.4" fill="#fff" '
            f'opacity="0.9"/>'
            f'</g>'
        )
        # blink: a lid that drops for a moment
        b.append(
            f'<path d="M {ex - 22},{ey - 24} L {ex + 22},{ey - 24} '
            f'L {ex + 22},{ey - 24} L {ex - 22},{ey - 24} Z" '
            f'fill="#dde3ea" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="0;0.42;0.45;0.49;0.52;1" dur="{CYCLE * 1.7}s" '
            f'repeatCount="indefinite"/>'
            f'</path>'
        )
        # brow
        b.append(f'<path d="M {ex - 20},{ey - 32} Q {ex},{ey - 40} {ex + 20},{ey - 32}" '
                 f'fill="none" stroke="#b3bdcb" stroke-width="2" '
                 f'stroke-linecap="round" opacity="0.75"/>')

    # ---- muzzle / mouth --------------------------------------------------
    b.append(f'<path d="M {CX - 22},{CY + 30} Q {CX},{CY + 46} {CX + 22},{CY + 30}" '
             f'fill="none" stroke="#8d97a5" stroke-width="4" '
             f'stroke-linecap="round"/>')
    b.append(f'<path d="M {CX},{CY + 30} L {CX},{CY + 40}" stroke="#8d97a5" '
             f'stroke-width="3.4" stroke-linecap="round"/>')
    # cheeks
    for sgn in (-1, 1):
        b.append(f'<ellipse cx="{CX + sgn * 60}" cy="{CY + 22}" rx="12" ry="7" '
                 f'fill="{PINK}" opacity="0.22"/>')

    # ---- HUD -------------------------------------------------------------
    b.append(f'<text x="26" y="36" font-family="{MONO}" font-size="11" '
             f'fill="{MUT}" letter-spacing="1.7">OCTOCAT</text>')
    b.append(f'<text x="26" y="56" font-family="{MONO}" font-size="9.5" '
             f'fill="{MUT}" opacity="0.85">8 tentacles &#183; blink &#183; gaze</text>')
    b.append(f'<text x="{W - 26}" y="{H - 22}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9.5" fill="{MUT}">'
             f'built from geometry, no bitmap</text>')
    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 4. daynight - a full 24h cycle with sun, moon, stars, weather, city
# ---------------------------------------------------------------------------
def daynight():
    W, H = 800, 520
    HORIZON = 372
    CYCLE = 24.0

    b = []
    defs = [
        '<linearGradient id="nSky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#050a1c">'
        f'<animate attributeName="stop-color" dur="{CYCLE}s" repeatCount="indefinite" '
        'values="#050a1c;#050a1c;#1d3b6b;#4a7fc4;#2a4a78;#1b2b52;#3a2a55;'
        '#7a4a63;#c9705a;#2c3f6b;#0d1633;#050a1c"'
        '/></stop>'
        '<stop offset="0.55" stop-color="#0d1430">'
        f'<animate attributeName="stop-color" dur="{CYCLE}s" repeatCount="indefinite" '
        'values="#0d1430;#0d1430;#3f5f96;#87b4e4;#5c7fae;#3c4f7a;#6b4a6e;'
        '#b06a72;#e8a06a;#4c6a9c;#1a2a52;#0d1430"'
        '/></stop>'
        '<stop offset="1" stop-color="#1a1f3a">'
        f'<animate attributeName="stop-color" dur="{CYCLE}s" repeatCount="indefinite" '
        'values="#1a1f3a;#1a1f3a;#6d7fb0;#c3d9f2;#9db4cf;#6d7fa8;#9c7f9a;'
        '#d99a86;#f5c48c;#7d97c0;#2a3a66;#1a1f3a"'
        '/></stop>'
        '</linearGradient>',
        '<radialGradient id="nSun" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#fffdf0"/>'
        '<stop offset="0.55" stop-color="#ffe07a"/>'
        '<stop offset="1" stop-color="#ffb02e" stop-opacity="0.1"/>'
        '</radialGradient>',
        '<radialGradient id="nMoon" cx="0.38" cy="0.34" r="0.72">'
        '<stop offset="0" stop-color="#fdfbf4"/>'
        '<stop offset="0.6" stop-color="#ddd8cb"/>'
        '<stop offset="1" stop-color="#a8a294"/>'
        '</radialGradient>',
        '<radialGradient id="nGlow" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#ffd27f" stop-opacity="0.5"/>'
        '<stop offset="1" stop-color="#ffd27f" stop-opacity="0"/>'
        '</radialGradient>',
    ]

    b.append(f'<rect width="{W}" height="{H}" fill="url(#nSky)"/>')

    # ---- stars (fade in at night) ---------------------------------------
    random.seed(131)
    stars = []
    for _ in range(90):
        x = random.uniform(0, W)
        y = random.uniform(0, HORIZON - 20)
        r = random.choice([0.6, 0.8, 1.0, 1.3, 1.7])
        base = random.uniform(0.35, 0.95)
        dur = random.uniform(2.2, 6.0)
        stars.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#eaf2ff" '
            f'opacity="0">'
            f'<animate attributeName="opacity" '
            f'values="0;0;{base:.2f};{base * 0.45:.2f};{base:.2f};0;0" '
            f'keyTimes="0;0.16;0.24;0.34;0.62;0.80;1" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" '
            f'values="{base:.2f};{min(1.0, base + 0.3):.2f};{base:.2f}" '
            f'dur="{dur:.2f}s" begin="{random.uniform(0, dur):.2f}s" '
            f'repeatCount="indefinite" additive="sum"/>'
            f'</circle>'
        )
    b.append("".join(stars))

    # ---- sun -------------------------------------------------------------
    # rises at 06:00 (left), peaks at noon, sets at 18:00 (right)
    SUN_PATH = f"M 60,{HORIZON} Q 400,-60 740,{HORIZON}"
    sun_vis = [0, 0.25, 0.50, 0.75, 1]
    b.append(
        f'<g opacity="0">'
        f'<animate attributeName="opacity" values="0;0;1;1;0" '
        f'keyTimes="{kt(sun_vis, CYCLE)}" dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'<g>'
        f'<animateMotion dur="{CYCLE}s" repeatCount="indefinite" '
        f'calcMode="linear" keyPoints="0;0;0.5;1;1" '
        f'keyTimes="{kt(sun_vis, CYCLE)}" path="{SUN_PATH}"/>'
        f'<circle cx="0" cy="0" r="96" fill="url(#nGlow)" opacity="0.75"/>'
        f'<circle cx="0" cy="0" r="30" fill="url(#nSun)"/>'
        f'<circle cx="0" cy="0" r="42" fill="none" stroke="#ffe07a" '
        f'stroke-width="1.4" opacity="0.35">'
        f'<animate attributeName="r" values="40;48;40" dur="5s" '
        f'repeatCount="indefinite"/>'
        f'</circle>'
        f'</g></g>'
    )

    # ---- moon (rises 18:00 right, peaks midnight, sets 06:00 left) -------
    MOON_PATH = f"M 740,{HORIZON} Q 400,-60 60,{HORIZON}"
    # Night runs 18:00 -> 06:00, i.e. half the 24s cycle. Driving the motion
    # with its own dur=12s and begin=18s is simpler and spec-safe: keyPoints
    # must be monotonically increasing, so encoding the wrap-around (0.5 -> 1
    # -> 0 -> 0.5) as keyPoints would be rejected.
    b.append(
        f'<g opacity="0">'
        f'<animate attributeName="opacity" values="1;0;0;1" '
        f'keyTimes="0;0.25;0.75;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'<g>'
        f'<animateMotion dur="{CYCLE / 2}s" begin="{CYCLE * 0.75}s" '
        f'repeatCount="indefinite" calcMode="linear" '
        f'keyPoints="0;1" keyTimes="0;1" path="{MOON_PATH}"/>'
        f'<circle cx="0" cy="0" r="70" fill="#cfe0ff" opacity="0.10"/>'
        f'<circle cx="0" cy="0" r="24" fill="url(#nMoon)"/>'
        f'<circle cx="-7" cy="-6" r="4.6" fill="#c2bcac" opacity="0.55"/>'
        f'<circle cx="6" cy="4" r="3.4" fill="#c2bcac" opacity="0.5"/>'
        f'<circle cx="-2" cy="10" r="2.6" fill="#c2bcac" opacity="0.45"/>'
        f'<circle cx="10" cy="-9" r="2.2" fill="#c2bcac" opacity="0.4"/>'
        f'</g></g>'
    )

    # ---- clouds ----------------------------------------------------------
    random.seed(151)
    for i in range(5):
        y = 70 + i * 34
        scale = random.uniform(0.7, 1.25)
        dur = random.uniform(52, 88)
        delay = random.uniform(0, dur)
        op = random.uniform(0.20, 0.42)
        cl = [f'<g transform="translate(0,{y:.0f}) scale({scale:.2f})" opacity="0">']
        cl.append(
            f'<animate attributeName="opacity" values="0;{op:.2f};{op:.2f};0;0" '
            f'keyTimes="0;0.12;0.72;0.86;1" dur="{CYCLE}s" '
            f'begin="{-delay:.1f}s" repeatCount="indefinite"/>'
        )
        cl.append(
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="-220 0;820 0" dur="{dur:.0f}s" begin="{-delay:.1f}s" '
            f'repeatCount="indefinite"/>'
            f'<ellipse cx="0" cy="0" rx="62" ry="20" fill="#ffffff"/>'
            f'<ellipse cx="-38" cy="6" rx="42" ry="15" fill="#ffffff"/>'
            f'<ellipse cx="36" cy="7" rx="46" ry="16" fill="#ffffff"/>'
            f'<ellipse cx="4" cy="-12" rx="38" ry="17" fill="#ffffff"/>'
            f'</g>'
        )
        cl.append('</g>')
        b.append("".join(cl))

    # ---- birds (day only) ------------------------------------------------
    for i in range(4):
        x0 = 120 + i * 150
        y0 = 120 + (i % 3) * 46
        dur = 11 + i * 2
        delay = i * 1.7
        flap = 0.5 + i * 0.08
        b.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.75;0.6;0;0" '
            f'keyTimes="0;0.28;0.36;0.62;0.74;1" dur="{CYCLE}s" '
            f'repeatCount="indefinite"/>'
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="-80 10; 60 -14; 200 6; 320 -8" '
            f'keyTimes="0;0.33;0.66;1" dur="{dur}s" begin="{-delay:.1f}s" '
            f'repeatCount="indefinite"/>'
            f'<path d="M 0,0 Q 7,-7 14,0 Q 21,-7 28,0" fill="none" '
            f'stroke="#2b3547" stroke-width="2" stroke-linecap="round">'
            f'<animate attributeName="d" '
            f'values="M 0,0 Q 7,-7 14,0 Q 21,-7 28,0;'
            f'M 0,0 Q 7,4 14,0 Q 21,4 28,0;'
            f'M 0,0 Q 7,-7 14,0 Q 21,-7 28,0" '
            f'dur="{flap:.2f}s" repeatCount="indefinite"/>'
            f'</path>'
            f'</g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 0" dur="1s" repeatCount="indefinite"/>'
            f'</g>'
        )
        # reposition each bird
        b[-1] = b[-1].replace("<g opacity=\"0\">",
                              f'<g opacity="0" transform="translate({x0},{y0})">', 1)

    # ---- hills (3 parallax layers) --------------------------------------
    b.append(f'<path d="M 0,{HORIZON} L 0,330 Q 130,282 260,326 '
             f'Q 380,368 520,318 Q 650,272 800,330 L 800,{HORIZON} Z" '
             f'fill="#1b2b40"/>')
    b.append(f'<path d="M 0,{HORIZON} L 0,348 Q 160,314 300,348 '
             f'Q 450,382 600,340 Q 700,314 800,350 L 800,{HORIZON} Z" '
             f'fill="#16233a"/>')

    # ---- conifers --------------------------------------------------------
    random.seed(163)
    for i in range(9):
        x = 40 + i * 88 + random.uniform(-14, 14)
        h = random.uniform(46, 82)
        base_y = HORIZON - 4
        w = h * 0.42
        b.append(f'<polygon points="{x:.0f},{base_y - h:.0f} '
                 f'{x - w:.0f},{base_y:.0f} {x + w:.0f},{base_y:.0f}" '
                 f'fill="#0f1c2c"/>')
        b.append(f'<polygon points="{x:.0f},{base_y - h * 0.62:.0f} '
                 f'{x - w * 0.78:.0f},{base_y:.0f} {x + w * 0.78:.0f},{base_y:.0f}" '
                 f'fill="#132234" opacity="0.9"/>')

    # ---- ground ----------------------------------------------------------
    b.append(f'<rect x="0" y="{HORIZON}" width="{W}" height="{H - HORIZON}" '
             f'fill="#0c1622"/>')
    b.append(f'<rect x="0" y="{HORIZON}" width="{W}" height="2" fill="#2b3d55"/>')

    # ---- city skyline with windows that light up at night ---------------
    random.seed(173)
    x = 486
    while x < 790:
        bw = random.uniform(26, 46)
        bh = random.uniform(40, 118)
        by = HORIZON - bh
        b.append(f'<rect x="{x:.0f}" y="{by:.0f}" width="{bw:.0f}" '
                 f'height="{bh:.0f}" fill="#0a121e"/>')
        # roof mast
        if random.random() < 0.4:
            b.append(f'<line x1="{x + bw / 2:.0f}" y1="{by:.0f}" '
                     f'x2="{x + bw / 2:.0f}" y2="{by - 12:.0f}" '
                     f'stroke="#0a121e" stroke-width="2"/>')
            b.append(f'<circle cx="{x + bw / 2:.0f}" cy="{by - 13:.0f}" r="1.8" '
                     f'fill="{RED}">'
                     f'<animate attributeName="opacity" values="1;0.1;1" '
                     f'dur="{1.4 + random.uniform(0, 1.2):.1f}s" '
                     f'repeatCount="indefinite"/></circle>')
        # windows
        cols = max(1, int(bw // 12))
        rows = max(1, int(bh // 15))
        for cx in range(cols):
            for ry in range(rows):
                if random.random() < 0.42:
                    continue
                wx = x + 5 + cx * 12
                wy = by + 7 + ry * 15
                delay = random.uniform(0, 3)
                b.append(
                    f'<rect x="{wx:.0f}" y="{wy:.0f}" width="5" height="7" '
                    f'fill="#ffd98a" opacity="0">'
                    f'<animate attributeName="opacity" values="0;0;0.85;0.8;0;0" '
                    f'keyTimes="0;0.62;0.70;0.86;0.94;1" dur="{CYCLE}s" '
                    f'begin="{-delay:.1f}s" repeatCount="indefinite"/>'
                    f'</rect>'
                )
        x += bw + random.uniform(4, 10)

    # ---- fireflies (night only) -----------------------------------------
    random.seed(181)
    for _ in range(14):
        fx = random.uniform(30, 470)
        fy = random.uniform(HORIZON - 90, HORIZON - 8)
        dur = random.uniform(3.4, 6.8)
        delay = random.uniform(0, 4)
        b.append(
            f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="2.2" fill="#d8ff8a" '
            f'opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.9;0.2;0.8;0;0" '
            f'keyTimes="0;0.68;0.74;0.80;0.86;0.93;1" dur="{CYCLE}s" '
            f'begin="{-delay:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" '
            f'values="{fy:.1f};{fy - 22:.1f};{fy - 8:.1f};{fy:.1f}" '
            f'keyTimes="0;0.4;0.7;1" dur="{dur:.1f}s" '
            f'begin="{-delay:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cx" '
            f'values="{fx:.1f};{fx + 16:.1f};{fx - 12:.1f};{fx:.1f}" '
            f'keyTimes="0;0.35;0.72;1" dur="{dur * 1.3:.1f}s" '
            f'begin="{-delay:.1f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    # ---- HUD clock -------------------------------------------------------
    marks = [(0.00, "00:00"), (0.25, "06:00"), (0.50, "12:00"),
             (0.75, "18:00"), (1.00, "00:00")]
    for i, (p, label) in enumerate(marks[:-1]):
        t0 = p * CYCLE
        t1 = marks[i + 1][0] * CYCLE
        b.append(
            f'<text x="{W / 2}" y="52" text-anchor="middle" '
            f'font-family="{MONO}" font-size="26" fill="{TXT}" '
            f'letter-spacing="3" opacity="0" '
            f'font-weight="700">{label}'
            f'<animate attributeName="opacity" values="0;0.92;0.92;0;0" '
            f'keyTimes="{kt([0, t0 + 0.05, t1 - 0.35, t1 - 0.1, CYCLE], CYCLE)}" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></text>'
        )
    b.append(f'<text x="{W / 2}" y="74" text-anchor="middle" '
             f'font-family="{MONO}" font-size="9" fill="{MUT}" '
             f'letter-spacing="2" opacity="0.8">LOCAL TIME</text>')

    b.append(f'<text x="26" y="{H - 20}" font-family="{MONO}" font-size="9.5" '
             f'fill="{MUT}" opacity="0.85">24h cycle &#183; sun &#183; moon '
             f'&#183; 90 stars &#183; city lights</text>')
    b.append(f'<text x="{W - 26}" y="{H - 20}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9.5" fill="{MUT}" '
             f'opacity="0.85">6am &#183; noon &#183; 6pm &#183; midnight</text>')
    return svg(W, H, "".join(b), "".join(defs))


def main():
    print("generating second-batch scenes:")
    # coffee and octocat are intentionally NOT written here: they were
    # redesigned in generate_polish.py, which runs later in the pipeline and
    # owns those two files.
    save("pacman.svg", pacman())
    save("daynight.svg", daynight())
    print("done.")


if __name__ == "__main__":
    main()