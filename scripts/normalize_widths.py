#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalize every profile SVG to one canonical width so the README reads as a
single, visually consistent column instead of a ragged stack of different sizes.

The transformation is lossless: it only changes the root <svg> width/height and
makes sure a viewBox exists so the vector artwork scales proportionally.
"""

import re
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
CANONICAL_WIDTH = 800

# Tiny inline badges are not shown as standalone panels; leave them at their
# natural size so they are not blown up if ever used inline later.
SKIP = {"visitor.svg", "follow.svg"}


def normalize(path):
    src = path.read_text(encoding="utf-8")
    m = re.search(r"<svg\b[^>]*>", src)
    if not m:
        return False, "no root <svg>"

    tag = m.group(0)
    attrs = tag[len("<svg"):-1]

    wm = re.search(r'(?<![-\w])width=["\'](\d+(?:\.\d+)?)["\']', attrs)
    hm = re.search(r'(?<![-\w])height=["\'](\d+(?:\.\d+)?)["\']', attrs)
    if not (wm and hm):
        return False, "no numeric width/height"

    w = float(wm.group(1))
    h = float(hm.group(1))
    if w == 0 or h == 0:
        return False, "zero dimension"

    new_h = round(h * CANONICAL_WIDTH / w, 2)

    # ensure a viewBox so scaling is proportional, not a crop
    if not re.search(r"\bviewBox=", attrs):
        attrs = f' viewBox="0 0 {w:g} {h:g}"' + attrs

    attrs = re.sub(
        r'(?<![-\w])width=["\'](\d+(?:\.\d+)?)["\']',
        f'width="{CANONICAL_WIDTH}"',
        attrs,
        count=1,
    )
    attrs = re.sub(
        r'(?<![-\w])height=["\'](\d+(?:\.\d+)?)["\']',
        f'height="{new_h:g}"',
        attrs,
        count=1,
    )

    out = src[: m.start()] + "<svg" + attrs + ">" + src[m.end():]
    if out != src:
        path.write_text(out, encoding="utf-8", newline="\n")
    return True, f"{w:g}x{h:g} -> {CANONICAL_WIDTH}x{new_h:g}"


def main():
    changed = 0
    skipped = []
    for f in sorted(ASSETS_DIR.glob("*.svg")):
        if f.name in SKIP:
            skipped.append(f.name)
            continue
        ok, info = normalize(f)
        if ok:
            changed += 1
    print(f"normalized {changed} SVGs to width {CANONICAL_WIDTH}px")
    if skipped:
        print(f"kept natural size: {', '.join(skipped)}")


if __name__ == "__main__":
    main()
