#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Polish pass: cleaner coffee + octocat, and one aspect ratio for every panel.

Two jobs:

1. coffee() and octocat() are redesigned. The earlier versions were assembled
   from primitives (triangle ears on a circle, seven thin squiggles for steam,
   bezier blobs for latte art) and read as crude rather than as illustrations.

2. The three panels authored at a different aspect ratio (conway 240x240,
   dna 300x320, skill-radar 460x400) are rebuilt at 800x520 so a README row of
   two panels has a uniform height instead of one tall tile beside a short one.

Pure SMIL, self-contained, authored at display size.

Run:  python scripts/generate_polish.py
Out:  assets/{coffee,octocat,conway,dna,skill-radar}.svg
"""

import math
import random
from pathlib import Path

from generate_scenes import (ASSETS, BLUE, BORDER, CARD, CYAN, FONT, GREEN, MUT,
                             MONO, ORANGE, PINK, PURPLE, RED, TEAL, TXT, YELLOW,
                             esc, save, svg)

W, H = 800, 520


# ---------------------------------------------------------------------------
# keyTimes helpers
# ---------------------------------------------------------------------------
def mono(vals, dur):
    """Monotonic keyTimes in [0,1] from second-offsets.

    SMIL silently kills the whole animation if this list is not
    non-decreasing or ends above 1.0, so quantise first and then force the
    sequence to be strictly increasing.
    """
    q = [min(1.0, max(0.0, round(v / dur, 4))) for v in vals]
    for i in range(1, len(q)):
        if q[i] <= q[i - 1]:
            q[i] = min(1.0, round(q[i - 1] + 1e-4, 4))
    for i in range(len(q) - 2, -1, -1):
        if q[i] >= q[i + 1]:
            q[i] = max(0.0, round(q[i + 1] - 1e-4, 4))
    q[0] = 0.0
    q[-1] = 1.0
    return ";".join(f"{v:.4f}" for v in q)


# ---------------------------------------------------------------------------
# 1. coffee - a drawn illustration rather than a cup from primitives
# ---------------------------------------------------------------------------
def coffee():
    CX, CY = 400, 300
    RX, RY = 148, 50
    BASE_Y = CY + 112
    CYCLE = 9.0

    b = []
    defs = [
        '<radialGradient id="pRoom" cx="0.42" cy="0.30" r="0.86">'
        '<stop offset="0" stop-color="#33271c"/>'
        '<stop offset="0.46" stop-color="#1b1410"/>'
        '<stop offset="1" stop-color="#080605"/>'
        '</radialGradient>',
        '<linearGradient id="pCup" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#6f7987"/>'
        '<stop offset="0.13" stop-color="#eef2f7"/>'
        '<stop offset="0.30" stop-color="#ffffff"/>'
        '<stop offset="0.52" stop-color="#dde3ea"/>'
        '<stop offset="0.80" stop-color="#a6b0bd"/>'
        '<stop offset="1" stop-color="#616b78"/>'
        '</linearGradient>',
        '<linearGradient id="pSteel" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#8d97a5"/>'
        '<stop offset="0.34" stop-color="#f4f7fa"/>'
        '<stop offset="0.62" stop-color="#c6ced9"/>'
        '<stop offset="1" stop-color="#79838f"/>'
        '</linearGradient>',
        '<radialGradient id="pCrema" cx="0.40" cy="0.30" r="0.82">'
        '<stop offset="0" stop-color="#e8bd85"/>'
        '<stop offset="0.26" stop-color="#c88f52"/>'
        '<stop offset="0.58" stop-color="#95612e"/>'
        '<stop offset="0.84" stop-color="#65401b"/>'
        '<stop offset="1" stop-color="#43290f"/>'
        '</radialGradient>',
        '<radialGradient id="pSaucer" cx="0.46" cy="0.34" r="0.72">'
        '<stop offset="0" stop-color="#414f65"/>'
        '<stop offset="0.62" stop-color="#26313f"/>'
        '<stop offset="1" stop-color="#121821"/>'
        '</radialGradient>',
        '<linearGradient id="pTable" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#1d1712"/>'
        '<stop offset="1" stop-color="#0b0908"/>'
        '</linearGradient>',
    ]

    # ---- room + table ----------------------------------------------------
    b.append(f'<rect width="{W}" height="{H}" fill="url(#pRoom)"/>')
    b.append(f'<ellipse cx="{CX - 50}" cy="{H - 110}" rx="350" ry="110" '
             f'fill="#ffb85c" opacity="0.055"/>')
    b.append(f'<rect x="0" y="{H - 104}" width="{W}" height="104" '
             f'fill="url(#pTable)"/>')
    b.append(f'<rect x="0" y="{H - 104}" width="{W}" height="1.6" '
             f'fill="#4a382a" opacity="0.75"/>')

    # ---- saucer ----------------------------------------------------------
    sy = BASE_Y + 12
    b.append(f'<ellipse cx="{CX + 8}" cy="{sy + 14}" rx="238" ry="60" '
             f'fill="#000" opacity="0.42"/>')
    b.append(f'<ellipse cx="{CX}" cy="{sy}" rx="232" ry="58" fill="url(#pSaucer)"/>')
    b.append(f'<ellipse cx="{CX}" cy="{sy}" rx="232" ry="58" fill="none" '
             f'stroke="#5a6b85" stroke-width="1.3" opacity="0.7"/>')
    b.append(f'<ellipse cx="{CX}" cy="{sy - 3}" rx="142" ry="34" fill="#1a222d"/>')
    b.append(f'<ellipse cx="{CX}" cy="{sy - 4}" rx="142" ry="34" fill="none" '
             f'stroke="#4a5a72" stroke-width="1.1" opacity="0.55"/>')
    b.append(f'<path d="M {CX - 180},{sy - 22} Q {CX - 60},{sy - 46} {CX + 50},{sy - 36}" '
             f'fill="none" stroke="#a8b8d0" stroke-width="2.4" '
             f'stroke-linecap="round" opacity="0.16"/>')

    # ---- handle ----------------------------------------------------------
    hx = CX + RX - 10
    b.append(
        f'<path d="M {hx},{CY + 28} '
        f'C {hx + 60},{CY + 20} {hx + 76},{CY + 64} {hx + 52},{CY + 90} '
        f'C {hx + 34},{CY + 108} {hx + 10},{CY + 104} {hx},{CY + 92}" '
        f'fill="none" stroke="url(#pSteel)" stroke-width="18" stroke-linecap="round"/>'
        f'<path d="M {hx + 6},{CY + 34} '
        f'C {hx + 52},{CY + 28} {hx + 62},{CY + 64} {hx + 42},{CY + 84}" '
        f'fill="none" stroke="#5d6672" stroke-width="4.5" '
        f'stroke-linecap="round" opacity="0.4"/>'
    )

    # ---- body ------------------------------------------------------------
    b.append(
        f'<path d="M {CX - RX},{CY} '
        f'C {CX - RX + 9},{CY + 58} {CX - 112},{CY + 92} {CX - 86},{CY + 108} '
        f'Q {CX},{CY + 128} {CX + 86},{CY + 108} '
        f'C {CX + 112},{CY + 92} {CX + RX - 9},{CY + 58} {CX + RX},{CY} Z" '
        f'fill="url(#pCup)"/>'
    )
    # shaded flank
    b.append(
        f'<path d="M {CX + 34},{CY + 6} '
        f'C {CX + 92},{CY + 28} {CX + 118},{CY + 72} {CX + 98},{CY + 102} '
        f'Q {CX + 66},{CY + 122} {CX + 24},{CY + 122} Z" '
        f'fill="#39424e" opacity="0.26"/>'
    )
    b.append(f'<ellipse cx="{CX + 2}" cy="{BASE_Y + 20}" rx="94" ry="14" '
             f'fill="#000" opacity="0.28"/>')
    # far inner wall seen through the opening
    b.append(f'<path d="M {CX - RX + 8},{CY} Q {CX},{CY + 36} {CX + RX - 8},{CY} '
             f'Q {CX},{CY - 24} {CX - RX + 8},{CY} Z" fill="#8e98a6"/>')

    # ---- rim + coffee ----------------------------------------------------
    b.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="#c9d1db"/>')
    b.append(f'<ellipse cx="{CX}" cy="{CY + 1.5}" rx="{RX - 6}" ry="{RY - 5}" '
             f'fill="#7f8996"/>')
    b.append(f'<ellipse cx="{CX}" cy="{CY + 2}" rx="{RX - 11}" ry="{RY - 9}" '
             f'fill="url(#pCrema)"/>')
    b.append(f'<path d="M {CX - RX + 12},{CY - 7} '
             f'Q {CX - 60},{CY - RY + 1} {CX + 12},{CY - RY + 4}" '
             f'fill="none" stroke="#ffffff" stroke-width="2.6" '
             f'stroke-linecap="round" opacity="0.5"/>')

    # ---- crema swirl -----------------------------------------------------
    b.append(f'<g opacity="0.4" transform="translate({CX},{CY + 2})"><g>'
             f'<animateTransform attributeName="transform" type="rotate" '
             f'from="0" to="360" dur="38s" repeatCount="indefinite"/>'
             f'<ellipse cx="0" cy="0" rx="94" ry="31" fill="none" '
             f'stroke="#f0d6b0" stroke-width="1.8" opacity="0.2" '
             f'stroke-dasharray="36 28"/>'
             f'<ellipse cx="0" cy="0" rx="58" ry="19" fill="none" '
             f'stroke="#f7e6c8" stroke-width="1.4" opacity="0.16" '
             f'stroke-dasharray="20 16"/>'
             f'</g></g>')

    # ---- rosetta ---------------------------------------------------------
    # Elliptical leaves that widen toward the base: reads as poured art.
    art = [f'<g transform="translate({CX},{CY + 2})" opacity="0.7">']
    art.append('<rect x="-1.6" y="-28" width="3.2" height="56" rx="1.6" '
               'fill="#f8ecd9" opacity="0.5"/>')
    for i in range(5):
        y = 21 - i * 10.8
        half = 11 + i * 7.6
        ry = 4.4 + i * 0.6
        for sgn in (-1, 1):
            cx = sgn * half * 0.60
            rot = sgn * (34 - i * 2)
            art.append(
                f'<ellipse cx="{cx:.1f}" cy="{y:.1f}" rx="{half * 0.60:.1f}" '
                f'ry="{ry:.1f}" fill="#faf0de" opacity="{0.62 - i * 0.05:.2f}" '
                f'transform="rotate({rot:.0f} {cx:.1f} {y:.1f})"/>'
            )
    # heart at the top of the pour
    art.append('<path d="M 0,-27 C -9,-36 -18,-27 0,-15 C 18,-27 9,-36 0,-27 Z" '
               'fill="#fbf3e4" opacity="0.66"/>')
    art.append('</g>')
    b.append("".join(art))

    # ---- surface life ----------------------------------------------------
    random.seed(97)
    for _ in range(18):
        a = random.uniform(0, 2 * math.pi)
        rr = math.sqrt(random.uniform(0, 1))
        x = CX + math.cos(a) * rr * (RX - 28)
        y = CY + 2 + math.sin(a) * rr * (RY - 16)
        r0 = random.uniform(1.2, 3.0)
        dur = random.uniform(3.4, 6.8)
        delay = random.uniform(0, dur)
        b.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r0:.1f}" fill="#f7e6c8" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.5;0.4;0" '
            f'keyTimes="{mono([0, delay, delay + dur * 0.45, delay + dur], dur + delay)}" '
            f'dur="{dur + delay:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{y:.1f};{y - 12:.1f};{y - 20:.1f}" '
            f'begin="{delay:.2f}s" dur="{dur:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    for i in range(2):
        t0 = 2.0 + i * 4.4
        b.append(
            f'<ellipse cx="{CX}" cy="{CY + 2}" rx="14" ry="5" fill="none" '
            f'stroke="#f7e6c8" stroke-width="1.3" opacity="0">'
            f'<animate attributeName="rx" values="14;124" begin="{t0:.1f}s" '
            f'dur="4.2s" repeatCount="indefinite"/>'
            f'<animate attributeName="ry" values="5;42" begin="{t0:.1f}s" '
            f'dur="4.2s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.4;0.13;0" '
            f'begin="{t0:.1f}s" dur="4.2s" repeatCount="indefinite"/>'
            f'</ellipse>'
        )

    # ---- steam: three broad ribbons, not seven squiggles ----------------
    for i in range(3):
        x0 = CX - 64 + i * 64
        amp = 16 + i * 4
        top = CY - 208 - i * 10
        dur = 5.6 + i * 0.9
        delay = i * 1.3

        def ribbon(phase):
            pts = []
            for k in range(4):
                f = k / 3.0
                y = CY - 28 - (CY - 28 - top) * f
                x = x0 + math.sin(f * 5.2 + i * 1.7 + phase) * amp * (0.3 + f * 0.95)
                pts.append((x, y))
            d = f"M {pts[0][0]:.1f},{pts[0][1]:.1f} "
            for k in range(3):
                x1, y1 = pts[k]
                x2, y2 = pts[k + 1]
                dy = y1 - y2
                d += (f"C {x1 - amp * 0.85:.1f},{y1 - dy * 0.36:.1f} "
                      f"{x2 + amp * 0.85:.1f},{y2 + dy * 0.36:.1f} "
                      f"{x2:.1f},{y2:.1f} ")
            return d

        d0, d1 = ribbon(0.0), ribbon(2.4)
        b.append(
            f'<path d="{d0}" fill="none" stroke="#e8eef7" '
            f'stroke-width="{7.5 - i * 1.1:.1f}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="0">'
            f'<animate attributeName="d" values="{d0};{d1};{d0}" '
            f'dur="{dur:.1f}s" begin="{-delay:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.20;0.13;0.05;0;0" '
            f'keyTimes="{mono([0, delay, delay + 0.9, delay + 2.6, delay + 4.2, CYCLE], CYCLE)}" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'</path>'
        )

    # ---- HUD -------------------------------------------------------------
    b.append(f'<text x="26" y="34" font-family="{MONO}" font-size="10.5" '
             f'fill="{MUT}" letter-spacing="2">ESPRESSO</text>')
    b.append(f'<text x="26" y="52" font-family="{MONO}" font-size="9" '
             f'fill="{MUT}" opacity="0.7">25s &#183; 36ml &#183; 9 bar</text>')
    b.append(f'<text x="{W - 26}" y="{H - 20}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9" fill="{MUT}" opacity="0.7">'
             f'crema &#183; rosetta &#183; steam</text>')
    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 2. octocat - a clean mascot silhouette, not a circle with triangle ears
# ---------------------------------------------------------------------------
def octocat():
    CX, CY = 400, 236
    CYCLE = 7.0

    b = []
    defs = [
        '<radialGradient id="oBody" cx="0.36" cy="0.28" r="0.82">'
        '<stop offset="0" stop-color="#ffffff"/>'
        '<stop offset="0.5" stop-color="#e9eef5"/>'
        '<stop offset="1" stop-color="#b9c4d2"/>'
        '</radialGradient>',
        '<linearGradient id="oTent" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#e2e8f0"/>'
        '<stop offset="1" stop-color="#a9b5c4"/>'
        '</linearGradient>',
        '<radialGradient id="oAura" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0.4" stop-color="#6ea8ff" stop-opacity="0.16"/>'
        '<stop offset="1" stop-color="#6ea8ff" stop-opacity="0"/>'
        '</radialGradient>',
    ]
    b.append(f'<rect width="{W}" height="{H}" fill="#0a0d14"/>')
    b.append(f'<circle cx="{CX}" cy="{CY + 30}" r="268" fill="url(#oAura)"/>')

    # ---- tentacles (5), behind the head ---------------------------------
    # Each is a thick round-capped stroke whose path morphs between two
    # phases, so the wave travels down the tentacle instead of the whole
    # limb sliding.
    tentacles = [
        (-118, 34, 74, 118, 0.0),
        (-74, 62, 40, 146, 0.7),
        (0, 74, 0, 164, 1.4),
        (74, 62, -40, 146, 2.1),
        (118, 34, -74, 118, 2.8),
    ]
    for bx, by, tx, ty, ph in tentacles:
        ax, ay = CX + bx, CY + by
        bx2, by2 = CX + tx, CY + ty

        def limb(phase):
            # control points bow outward, with a travelling offset
            mx = (ax + bx2) / 2 + math.sin(phase + ph) * 16
            my = (ay + by2) / 2 + math.cos(phase * 0.8 + ph) * 6
            ex = bx2 + math.sin(phase + 1.1 + ph) * 13
            ey = by2 + math.cos(phase + 0.6 + ph) * 5
            return (f"M {ax:.1f},{ay:.1f} "
                    f"Q {mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}")

        d0, d1 = limb(0.0), limb(2.5)
        b.append(
            f'<path d="{d0}" fill="none" stroke="url(#oTent)" stroke-width="25" '
            f'stroke-linecap="round" opacity="0.97">'
            f'<animate attributeName="d" values="{d0};{d1};{d0}" '
            f'dur="{3.6 + (ph % 1.4):.2f}s" repeatCount="indefinite"/>'
            f'</path>'
        )
        # sucker dots, following the tip
        for k, f in enumerate((0.45, 0.75, 0.95)):
            sx = ax + (bx2 - ax) * f
            sy = ay + (by2 - ay) * f
            b.append(
                f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{3.4 - k * 0.5:.1f}" '
                f'fill="#93a1b3" opacity="0.5">'
                f'<animate attributeName="opacity" values="0.25;0.6;0.25" '
                f'dur="{2.6 + k * 0.4:.1f}s" begin="{ph:.1f}s" '
                f'repeatCount="indefinite"/></circle>'
            )

    # ---- head: one path, cat ears integrated -----------------------------
    # 90 wide at the cheeks, tapering to a rounded chin, with two pointed ears.
    head = (
        f"M {CX - 92},{CY + 6} "
        f"C {CX - 97},{CY - 48} {CX - 78},{CY - 78} {CX - 60},{CY - 86} "
        f"L {CX - 46},{CY - 132} "
        f"L {CX - 14},{CY - 96} "
        f"C {CX - 5},{CY - 99} {CX + 5},{CY - 99} {CX + 14},{CY - 96} "
        f"L {CX + 46},{CY - 132} "
        f"L {CX + 60},{CY - 86} "
        f"C {CX + 78},{CY - 78} {CX + 97},{CY - 48} {CX + 92},{CY + 6} "
        f"C {CX + 88},{CY + 68} {CX + 50},{CY + 96} {CX},{CY + 96} "
        f"C {CX - 50},{CY + 96} {CX - 88},{CY + 68} {CX - 92},{CY + 6} Z"
    )
    b.append(f'<path d="{head}" fill="url(#oBody)"/>')
    # inner ear
    b.append(f'<path d="M {CX - 44},{CY - 122} L {CX - 38},{CY - 96} '
             f'L {CX - 20},{CY - 94} Z" fill="#f7b8c8" opacity="0.5"/>')
    b.append(f'<path d="M {CX + 44},{CY - 122} L {CX + 38},{CY - 96} '
             f'L {CX + 20},{CY - 94} Z" fill="#f7b8c8" opacity="0.5"/>')

    # ---- eyes ------------------------------------------------------------
    for sgn in (-1, 1):
        ex, ey = CX + sgn * 36, CY - 24
        b.append(f'<ellipse cx="{ex}" cy="{ey}" rx="17" ry="20" fill="#141a22"/>')
        # gaze drifts on two incommensurate periods so the motion never repeats
        b.append(
            f'<g>'
            f'<circle cx="{ex}" cy="{ey}" r="6.2" fill="#0a0d14">'
            f'<animate attributeName="cx" '
            f'values="{ex - 4:.1f};{ex + 4:.1f};{ex + 3:.1f};{ex - 3:.1f};{ex - 4:.1f}" '
            f'keyTimes="0;0.26;0.5;0.76;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" '
            f'values="{ey + 2:.1f};{ey - 3:.1f};{ey + 3:.1f};{ey - 2:.1f};{ey + 2:.1f}" '
            f'keyTimes="0;0.3;0.56;0.8;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'</circle>'
            f'<circle cx="{ex - 2.6:.1f}" cy="{ey - 3.0:.1f}" r="2.2" fill="#fff" '
            f'opacity="0.9"/>'
            f'</g>'
        )
        # blink: an eyelid that sweeps down over the eye
        b.append(
            f'<path d="M {ex - 18},{ey - 21} L {ex + 18},{ey - 21} '
            f'L {ex + 18},{ey - 21} L {ex - 18},{ey - 21} Z" fill="#e9eef5" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="0;0.42;0.45;0.49;0.52;1" dur="{CYCLE * 1.7}s" '
            f'repeatCount="indefinite"/></path>'
        )

    # ---- nose + mouth ----------------------------------------------------
    b.append(f'<path d="M {CX - 6},{CY + 22} L {CX + 6},{CY + 22} '
             f'L {CX},{CY + 30} Z" fill="#f7a8bd" opacity="0.85"/>')
    b.append(f'<path d="M {CX},{CY + 30} L {CX},{CY + 38}" stroke="#8d97a5" '
             f'stroke-width="2.6" stroke-linecap="round"/>')
    b.append(f'<path d="M {CX - 20},{CY + 38} Q {CX - 10},{CY + 50} {CX},{CY + 38}" '
             f'fill="none" stroke="#8d97a5" stroke-width="2.6" stroke-linecap="round"/>')
    b.append(f'<path d="M {CX},{CY + 38} Q {CX + 10},{CY + 50} {CX + 20},{CY + 38}" '
             f'fill="none" stroke="#8d97a5" stroke-width="2.6" stroke-linecap="round"/>')
    # cheeks
    for sgn in (-1, 1):
        b.append(f'<ellipse cx="{CX + sgn * 62}" cy="{CY + 22}" rx="13" ry="7.5" '
                 f'fill="#f778ba" opacity="0.2"/>')

    # ---- HUD -------------------------------------------------------------
    b.append(f'<text x="26" y="34" font-family="{MONO}" font-size="10.5" '
             f'fill="{MUT}" letter-spacing="2">OCTOCAT</text>')
    b.append(f'<text x="26" y="52" font-family="{MONO}" font-size="9" '
             f'fill="{MUT}" opacity="0.7">5 tentacles &#183; blink &#183; gaze</text>')
    b.append(f'<text x="{W - 26}" y="{H - 20}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9" fill="{MUT}" opacity="0.7">'
             f'pure vector, no bitmap</text>')
    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 3. conway - real Game of Life, simulated here and played back as keyframes
# ---------------------------------------------------------------------------
def conway():
    COLS, ROWS = 44, 22
    CELL = 16
    OX = (W - COLS * CELL) // 2
    OY = 62
    CYCLE = 16.0

    # --- seed -------------------------------------------------------------
    random.seed(2026)
    grid = [[0] * COLS for _ in range(ROWS)]
    # a few still lifes and oscillators so the soup never dies out
    for cx, cy, shape in (
        (6, 5, [(0, 0), (1, 0), (0, 1), (1, 1)]),                       # block
        (14, 4, [(1, 0), (2, 0), (0, 1), (2, 1), (1, 2)]),               # r-pentomino-ish
        (24, 8, [(0, 0), (1, 0), (2, 0)]),                              # blinker
        (33, 5, [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2)]),
    ):
        for dx, dy in shape:
            if 0 <= cy + dy < ROWS and 0 <= cx + dx < COLS:
                grid[cy + dy][cx + dx] = 1
    for _ in range(150):
        x, y = random.randrange(COLS), random.randrange(ROWS)
        grid[y][x] = 1

    def step(g):
        out = [[0] * COLS for _ in range(ROWS)]
        for y in range(ROWS):
            for x in range(COLS):
                n = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        n += g[(y + dy) % ROWS][(x + dx) % COLS]
                out[y][x] = 1 if (n == 3 or (g[y][x] and n == 2)) else 0
        return out

    GENS = 32
    frames = [grid]
    for _ in range(GENS):
        frames.append(step(frames[-1]))
    # pad the last frame so the cycle holds before restarting
    frames += [frames[-1]] * 4
    N = len(frames)

    # which cells are ever alive, and their per-frame opacity
    b = []
    defs = [
        '<radialGradient id="cGlow" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#3fb950" stop-opacity="0.10"/>'
        '<stop offset="1" stop-color="#3fb950" stop-opacity="0"/>'
        '</radialGradient>',
    ]
    b.append(f'<rect width="{W}" height="{H}" fill="#050a06"/>')
    b.append(f'<ellipse cx="{W / 2}" cy="{H / 2}" rx="420" ry="260" '
             f'fill="url(#cGlow)"/>')

    for y in range(ROWS):
        for x in range(COLS):
            if not any(f[y][x] for f in frames):
                continue
            px = OX + x * CELL
            py = OY + y * CELL
            # discrete opacity keyframes: alive = 1, dead = 0
            vals = ";".join("1" if f[y][x] else "0" for f in frames)
            # age-based colour: newborn bright, survivors deeper
            age = next((i for i, f in enumerate(frames) if f[y][x]), 0)
            col = "#7ee787" if age < 3 else ("#3fb950" if age < 10 else "#2a7f3f")
            b.append(
                f'<rect x="{px + 1.5}" y="{py + 1.5}" width="{CELL - 3}" '
                f'height="{CELL - 3}" rx="2.5" fill="{col}" opacity="0">'
                f'<animate attributeName="opacity" values="{vals}" '
                f'calcMode="discrete" dur="{CYCLE}s" repeatCount="indefinite"/>'
                f'</rect>'
            )

    b.append(f'<text x="26" y="34" font-family="{MONO}" font-size="10.5" '
             f'fill="{GREEN}" letter-spacing="2">CONWAY&#39;S GAME OF LIFE</text>')
    b.append(f'<text x="26" y="52" font-family="{MONO}" font-size="9" '
             f'fill="{MUT}" opacity="0.7">{COLS}&#215;{ROWS} cells &#183; '
             f'{GENS} generations</text>')
    b.append(f'<text x="{W - 26}" y="{H - 18}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9" fill="{MUT}" opacity="0.65">'
             f'B3/S23 &#183; torus wrap</text>')
    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 4. dna - a horizontal double helix with base-pair rungs
# ---------------------------------------------------------------------------
def dna():
    CY = 258
    AMP = 92
    X0, X1 = 70, 730
    TURNS = 3.4
    CYCLE = 12.0
    K = TURNS * 2 * math.pi / (X1 - X0)

    def strand(phase, sign):
        pts = []
        n = 90
        for i in range(n + 1):
            x = X0 + (X1 - X0) * i / n
            y = CY + sign * AMP * math.sin(K * (x - X0) + phase)
            pts.append((x, y))
        return pts

    def to_path(pts):
        return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    b = []
    defs = [
        '<linearGradient id="dNA" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#36BCF7"/>'
        '<stop offset="0.5" stop-color="#a0e9ff"/>'
        '<stop offset="1" stop-color="#36BCF7"/>'
        '</linearGradient>',
        '<linearGradient id="dNB" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#bc8cff"/>'
        '<stop offset="0.5" stop-color="#e2ccff"/>'
        '<stop offset="1" stop-color="#bc8cff"/>'
        '</linearGradient>',
    ]
    b.append(f'<rect width="{W}" height="{H}" fill="#070a12"/>')

    # three phase variants, looped d0 -> d1 -> d2 -> d0
    variants = [0.0, 2.094, 4.188]
    a_paths = [to_path(strand(v, 1)) for v in variants]
    b_paths = [to_path(strand(v + math.pi, 1)) for v in variants]

    for paths, grad, wdt, op in ((a_paths, "url(#dNA)", 4.2, 0.95),
                                 (b_paths, "url(#dNB)", 4.2, 0.95)):
        d0 = paths[0]
        vals = ";".join(paths + [paths[0]])
        b.append(
            f'<path d="{d0}" fill="none" stroke="{grad}" stroke-width="{wdt}" '
            f'stroke-linecap="round" opacity="{op}">'
            f'<animate attributeName="d" values="{vals}" calcMode="linear" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'</path>'
        )

    # base-pair rungs: rungs whose midpoint lies on the axis read as pairs
    NRUNG = 26
    for i in range(NRUNG):
        x = X0 + 24 + (X1 - X0 - 48) * i / (NRUNG - 1)
        # opacity peaks as the rung sweeps past, giving a travelling shimmer
        phase = (x - X0) / (X1 - X0)
        delay = phase * 3.0
        y1 = CY + AMP * math.sin(K * (x - X0))
        y2 = CY - AMP * math.sin(K * (x - X0))
        col = (PURPLE, CYAN, GREEN, YELLOW, PINK)[i % 5]
        b.append(
            f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" '
            f'stroke="{col}" stroke-width="2.6" stroke-linecap="round" opacity="0.28">'
            f'<animate attributeName="opacity" values="0.18;0.85;0.3;0.18" '
            f'keyTimes="0;0.3;0.7;1" dur="3.0s" begin="{-delay:.2f}s" '
            f'repeatCount="indefinite"/>'
            f'</line>'
        )
        # nucleotide knobs at both ends
        for yy in (y1, y2):
            b.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="3.2" fill="{col}" '
                     f'opacity="0.75"/>')

    # travelling highlight along the helix
    b.append(
        f'<circle cx="{X0}" cy="{CY}" r="6" fill="#ffffff" opacity="0.9">'
        f'<animateMotion dur="5.5s" repeatCount="indefinite" calcMode="linear" '
        f'path="M {to_path(strand(0, 1))[2:]}"/>'
        f'<animate attributeName="opacity" values="0;0.9;0.9;0" '
        f'keyTimes="0;0.1;0.85;1" dur="5.5s" repeatCount="indefinite"/>'
        f'</circle>'
    )

    b.append(f'<text x="26" y="34" font-family="{MONO}" font-size="10.5" '
             f'fill="{PURPLE}" letter-spacing="2">DNA &#183; DOUBLE HELIX</text>')
    b.append(f'<text x="26" y="52" font-family="{MONO}" font-size="9" '
             f'fill="{MUT}" opacity="0.7">{NRUNG} base pairs &#183; '
             f'{TURNS} turns</text>')
    b.append(f'<text x="{W - 26}" y="{H - 18}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9" fill="{MUT}" opacity="0.65">'
             f'5&#39;&#8594;3&#39; &#183; antiparallel</text>')
    return svg(W, H, "".join(b), "".join(defs))


# ---------------------------------------------------------------------------
# 5. skill-radar - radar on the left, ranked bars on the right
# ---------------------------------------------------------------------------
def skill_radar():
    CX, CY = 250, 262
    R = 150
    data = [
        ("JavaScript", 6, YELLOW),
        ("Python", 3, BLUE),
        ("TypeScript", 3, CYAN),
        ("Astro", 2, PURPLE),
        ("HTML", 1, ORANGE),
        ("CSS", 1, TEAL),
    ]
    total = sum(v for _, v, _ in data)
    n = len(data)

    b = []
    defs = [
        '<radialGradient id="kSweep" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.35"/>'
        f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>'
        '</radialGradient>',
        '<linearGradient id="kPoly" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.5"/>'
        f'<stop offset="1" stop-color="{PURPLE}" stop-opacity="0.3"/>'
        '</linearGradient>',
    ]
    b.append(f'<rect width="{W}" height="{H}" fill="{CARD}"/>')
    b.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" '
             f'fill="none" stroke="{BORDER}"/>')

    def pt(i, r):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        return CX + r * math.cos(ang), CY + r * math.sin(ang)

    # rings
    for ring in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, R * ring) for i in range(n)))
        b.append(f'<polygon points="{pts}" fill="none" stroke="{BORDER}" '
                 f'stroke-width="1" opacity="0.9"/>')
    # spokes
    for i in range(n):
        x, y = pt(i, R)
        b.append(f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" '
                 f'stroke="{BORDER}" stroke-width="1" opacity="0.8"/>')

    # ---- sweep -----------------------------------------------------------
    # A real plan-position-indicator sweep is not one wedge: it is a leading
    # edge plus a trail that decays behind it. Build ~18 thin wedges whose
    # opacity falls off with angular distance, all inside one rotating group.
    SWEEP_T = 5.2
    NW = 18
    span = 360.0 / NW            # each slice covers this many degrees
    trail = 100.0                # total angular length of the afterglow
    b.append('<g>')
    b.append(f'<animateTransform attributeName="transform" type="rotate" '
             f'from="0 {CX} {CY}" to="360 {CX} {CY}" dur="{SWEEP_T}s" '
             f'repeatCount="indefinite"/>')
    for i in range(NW):
        a0 = -i * span
        a1 = a0 - span
        p0 = (CX + R * math.cos(math.radians(a0 - 90)),
              CY + R * math.sin(math.radians(a0 - 90)))
        p1 = (CX + R * math.cos(math.radians(a1 - 90)),
              CY + R * math.sin(math.radians(a1 - 90)))
        # exponential decay with angular distance behind the leading edge
        d = i * span
        op = 0.42 * math.exp(-d / (trail * 0.42))
        b.append(
            f'<path d="M {CX},{CY} L {p0[0]:.1f},{p0[1]:.1f} '
            f'A {R} {R} 0 0 1 {p1[0]:.1f},{p1[1]:.1f} Z" '
            f'fill="{CYAN}" opacity="{op:.4f}"/>'
        )
    # leading edge: a bright core with a soft bloom
    b.append(f'<line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - R}" '
             f'stroke="{CYAN}" stroke-width="5" opacity="0.16"/>')
    b.append(f'<line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - R}" '
             f'stroke="{CYAN}" stroke-width="2" opacity="0.95"/>')
    b.append(f'<line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - R}" '
             f'stroke="#eafff8" stroke-width="0.9" opacity="0.9"/>')
    # a bright pip riding the tip
    b.append(f'<circle cx="{CX}" cy="{CY - R}" r="3" fill="#eafff8" opacity="0.9"/>')
    b.append('</g>')

    # ---- bearing ticks around the rim -----------------------------------
    NT = 72
    for k in range(NT):
        ang = math.radians(k * 360.0 / NT - 90)
        major = k % 6 == 0
        r1 = R + (11 if major else 6)
        x1 = CX + math.cos(ang) * r1
        y1 = CY + math.sin(ang) * r1
        x2 = CX + math.cos(ang) * R
        y2 = CY + math.sin(ang) * R
        b.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{CYAN}" stroke-width="{1.4 if major else 0.7}" '
                 f'opacity="{0.55 if major else 0.22}"/>')

    # ---- data polygon ----------------------------------------------------
    pts = [pt(i, R * (v / max(x[1] for x in data))) for i, (_, v, _) in enumerate(data)]
    b.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
             f'fill="url(#kPoly)" stroke="{CYAN}" stroke-width="2.2"/>')
    # vertices flash as the sweep passes their bearing
    for i, (x, y) in enumerate(pts):
        col = data[i][2]
        ang = -90 + i * 360.0 / n
        phi = (ang + 90) % 360                 # clockwise angle from up
        hit = phi / 360.0 * SWEEP_T
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{col}">'
                 f'<animate attributeName="r" values="4;5.5;4" dur="2.8s" '
                 f'begin="{i * 0.22:.2f}s" repeatCount="indefinite"/></circle>')
        # expanding halo when painted
        # For the vertex at the top (i=0) hit == 0, so a naive
        # max(0, hit - 0.04) yields a duplicate 0 and SMIL rejects the list.
        # mono() quantises and forces a strictly increasing sequence.
        halo_t = mono([0, max(0.0, hit - 0.04), hit + 0.05, hit + 0.22, SWEEP_T],
                      SWEEP_T)
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="none" '
                 f'stroke="{col}" stroke-width="1.4" opacity="0">'
                 f'<animate attributeName="r" values="4;4;16;20;20" '
                 f'keyTimes="{halo_t}" '
                 f'dur="{SWEEP_T}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;0;0.75;0;0" '
                 f'keyTimes="{halo_t}" '
                 f'dur="{SWEEP_T}s" repeatCount="indefinite"/></circle>')

    # axis labels
    for i, (name, v, col) in enumerate(data):
        lx, ly = pt(i, R + 26)
        anchor = "middle"
        if lx < CX - 20:
            anchor = "end"
        elif lx > CX + 20:
            anchor = "start"
        b.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
                 f'font-family="{MONO}" font-size="10" fill="{col}">{esc(name)}</text>')

    # ---- right panel: ranked bars ---------------------------------------
    BX, BY = 470, 108
    BARW = 250
    b.append(f'<text x="{BX}" y="{BY - 34}" font-family="{MONO}" font-size="10" '
             f'fill="{MUT}" letter-spacing="1.8">LANGUAGE SHARE</text>')
    maxv = max(v for _, v, _ in data)
    for i, (name, v, col) in enumerate(data):
        y = BY + i * 54
        pct = v / total * 100
        b.append(f'<text x="{BX}" y="{y - 6}" font-family="{MONO}" font-size="10" '
                 f'fill="{TXT}">{esc(name)}</text>')
        b.append(f'<text x="{BX + BARW}" y="{y - 6}" text-anchor="end" '
                 f'font-family="{MONO}" font-size="10" fill="{col}">{pct:.1f}%</text>')
        b.append(f'<rect x="{BX}" y="{y + 2}" width="{BARW}" height="9" rx="4.5" '
                 f'fill="#1f2733"/>')
        # bar grows on load, then breathes
        full = BARW * v / maxv
        b.append(
            f'<rect x="{BX}" y="{y + 2}" width="0" height="9" rx="4.5" fill="{col}">'
            f'<animate attributeName="width" values="0;{full:.1f};{full * 0.94:.1f};{full:.1f}" '
            f'keyTimes="0;0.35;0.75;1" dur="{CYCLE_D}s" begin="{i * 0.12:.2f}s" '
            f'fill="freeze"/>'
            f'</rect>'
        )

    b.append(f'<text x="{BX}" y="{H - 46}" font-family="{MONO}" font-size="9" '
             f'fill="{MUT}" opacity="0.7">share of {total} repositories</text>')
    b.append(f'<text x="{W - 26}" y="{H - 18}" text-anchor="end" '
             f'font-family="{MONO}" font-size="9" fill="{MUT}" opacity="0.65">'
             f'excludes forks</text>')
    return svg(W, H, "".join(b), "".join(defs))


CYCLE_D = 14.0


# ---------------------------------------------------------------------------
# 6. joke - rotating developer jokes, full width
# ---------------------------------------------------------------------------
def joke():
    """Dev Joke card.

    The previous version was a static asset with a latent SMIL bug: its
    keyTimes began "0;0.000;..." — a duplicated stop, which makes the list
    invalid and can leave the punchlines permanently at opacity 0. This one is
    generated, uses monotonic keyTimes, and is authored at full width.
    """
    jokes = [
        ("Why do programmers prefer dark mode?",
         "Because light attracts bugs."),
        ("A SQL query walks into a bar,",
         "walks up to two tables and asks: can I join you?"),
        ("There are 10 types of people:",
         "those who understand binary, and those who don't."),
    ]
    W, H = 800, 200
    n = len(jokes)
    seg = 1.0 / n
    CYCLE = 15.0

    b = []
    defs = [
        '<linearGradient id="jSheen" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.05"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
        '</linearGradient>',
    ]
    b.append(f'<rect width="{W}" height="{H}" fill="{CARD}"/>')
    b.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" '
             f'fill="none" stroke="{BORDER}"/>')
    # accent block on the left
    b.append(f'<rect x="1" y="1" width="5" height="{H - 2}" rx="2.5" fill="{YELLOW}" '
             f'opacity="0.85"/>')

    # header
    b.append(f'<text x="28" y="40" font-family="{FONT}" font-size="15" '
             f'font-weight="700" fill="{YELLOW}">&#128514; Dev Joke</text>')
    b.append(f'<rect x="28" y="50" width="{W - 56}" height="1" fill="{BORDER}" '
             f'opacity="0.7"/>')

    # three jokes, each opaque for its own slice of the cycle
    for i, (setup, punch) in enumerate(jokes):
        t0 = i * seg
        t1 = (i + 1) * seg
        fade = 0.012
        times = mono([0, t0 * CYCLE, (t0 + fade) * CYCLE,
                      (t1 - fade) * CYCLE, t1 * CYCLE, CYCLE], CYCLE)
        op = f'<animate attributeName="opacity" values="0;0;1;1;0;0" ' \
             f'keyTimes="{times}" dur="{CYCLE}s" repeatCount="indefinite"/>'
        b.append(
            f'<text x="28" y="92" font-family="{FONT}" font-size="17" '
            f'fill="{TXT}" opacity="0">{esc(setup)}{op}</text>'
        )
        b.append(
            f'<text x="28" y="122" font-family="{FONT}" font-size="17" '
            f'fill="{CYAN}" opacity="0">{esc(punch)}{op}</text>'
        )
        # counter
        b.append(
            f'<text x="{W - 28}" y="40" text-anchor="end" '
            f'font-family="{MONO}" font-size="10" fill="{MUT}" opacity="0">'
            f'{i + 1} / {n}{op}</text>'
        )

    # progress dots
    for i in range(n):
        cx = 28 + i * 16
        b.append(f'<circle cx="{cx}" cy="{H - 26}" r="3.4" fill="{BORDER}"/>')
        b.append(
            f'<circle cx="{cx}" cy="{H - 26}" r="3.4" fill="{YELLOW}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="{mono([0, i * seg * CYCLE, (i * seg + 0.012) * CYCLE, ((i + 1) * seg - 0.012) * CYCLE, (i + 1) * seg * CYCLE, CYCLE], CYCLE)}" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></circle>'
        )

    # a sheen sweeping across every few seconds
    b.append(
        f'<g clip-path="inset(0 round 16px)">'
        f'<rect x="-200" y="0" width="160" height="{H}" fill="url(#jSheen)" '
        f'transform="skewX(-16)">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0;1100 0;1100 0" keyTimes="0;0.5;1" dur="11s" '
        f'repeatCount="indefinite" additive="sum"/>'
        f'</rect></g>'
    )
    return svg(W, H, "".join(b), "".join(defs))


def main():
    print("generating polish pass:")
    save("coffee.svg", coffee())
    # conway.svg is intentionally not written: the user removed it from the
    # README, and leaving the generator wired would resurrect the asset on the
    # next daily run.
    save("dna.svg", dna())
    save("skill-radar.svg", skill_radar())
    save("joke.svg", joke())
    print("done.")


if __name__ == "__main__":
    main()