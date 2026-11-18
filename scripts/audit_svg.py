#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static audit for the profile SVGs.

Every widget here is hand-generated SMIL, and SMIL fails *silently*: an
animation with a bad keyTimes list, a bad dur, or mismatched arity is dropped
by the renderer, and the element simply keeps its base value. A card that
should fade in stays at opacity 0 forever; a line that should type in is either
always visible or never visible. Nothing throws, so a broken asset looks fine
in a diff and only shows up on the rendered page.

This module re-checks the things that have actually broken before:

  XML       well-formedness
  SMIL      keyTimes strictly increasing and within [0,1]
  SMIL      dur carries exactly one unit ("13ss" is invalid)
  SMIL      values / keyTimes / keyPoints have matching arity
  SMIL      an element with a transform attribute must not have a direct,
            non-additive <animateTransform> child - the child REPLACES the
            attribute, so the element loses its placement
  INVISIBLE an element pinned at opacity="0" with no valid opacity animation
            child never renders at all
  PAINT     fill/stroke/stop-color must be #hex, a named colour, url(#id)...
  EXTERNAL  no references to another host (camo/githubusercontent are blocked
            in some networks, and a self-contained SVG should not need them)
  DUPID     duplicate id attributes break url(#...) references
  BOUNDS    rects outside the viewBox, judged relative to the viewBox and
            skipping anything inside a transformed or clipped ancestor

Run directly for a report; exits non-zero when anything is found, so it can
gate a build. Importable: `audit(ASSETS_DIR)` returns the findings list.
"""

import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

SVG_NS = "{http://www.w3.org/2000/svg}"

NAMED_COLOURS = {
    "none", "black", "white", "red", "green", "blue", "yellow", "orange",
    "purple", "pink", "gray", "grey", "silver", "maroon", "navy", "teal",
    "aqua", "cyan", "magenta", "lime", "olive", "transparent",
    "currentcolor", "freeze", "remove", "inherit",
}

SEVERITY_ORDER = {
    "XML": 0, "SMIL": 1, "INVISIBLE": 2, "EXTERNAL": 3,
    "DUPID": 4, "PAINT": 5, "BOUNDS": 6,
}

_NUM = r"-?\d+(?:\.\d+)?"


def _tag(el):
    return el.tag.replace(SVG_NS, "")


def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_transform(raw):
    """Approximate (tx, ty, sx, sy) from a transform attribute.

    Rotation and skew are ignored: they do not affect whether a rect sits
    inside the viewBox along the axes we check.
    """
    tx = ty = 0.0
    sx = sy = 1.0
    if not raw:
        return tx, ty, sx, sy
    for m in re.finditer(r"(translate|scale)\s*\(([^)]*)\)", raw):
        parts = [float(x) for x in re.findall(_NUM, m.group(2))]
        if not parts:
            continue
        if m.group(1) == "translate":
            tx += parts[0]
            ty += parts[1] if len(parts) > 1 else 0.0
        else:
            sx *= parts[0]
            sy *= parts[1] if len(parts) > 1 else parts[0]
    return tx, ty, sx, sy


def _keytimes_ok(raw):
    """(ok, reason) for a keyTimes string."""
    try:
        v = [float(x) for x in raw.split(";")]
    except ValueError:
        return False, "non-numeric"
    if not v:
        return False, "empty"
    if any(x > 1.0 for x in v):
        return False, "value > 1.0"
    if any(x < 0.0 for x in v):
        return False, "value < 0"
    if any(b <= a for a, b in zip(v, v[1:])):
        return False, "duplicate/non-monotonic"
    return True, ""


def audit(assets_dir, verbose=False):
    """Check every SVG in `assets_dir`. Returns a list of (file, sev, message)."""
    findings = []

    def add(fname, sev, msg):
        findings.append((fname, sev, msg))

    for path in sorted(glob.glob(os.path.join(assets_dir, "*.svg"))):
        fname = os.path.basename(path)

        # ---- XML -----------------------------------------------------
        try:
            root = ET.parse(path).getroot()
        except Exception as exc:
            add(fname, "XML", str(exc)[:120])
            continue

        # viewBox is the coordinate system the artwork is drawn in; bounds must
        # be judged against it, not against the CSS width (a 1000x220 viewBox
            # rendered at width=800 legitimately contains x up to 1000).
        vb = root.get("viewBox")
        if vb:
            parts = [float(x) for x in re.findall(_NUM, vb)]
            if len(parts) == 4:
                vx, vy, vw, vh = parts
            else:
                vx = vy = 0.0
                vw = _num(root.get("width"))
                vh = _num(root.get("height"))
        else:
            vx = vy = 0.0
            vw = _num(root.get("width"))
            vh = _num(root.get("height"))

        # ---- walk with accumulated transform + clip state ------------
        def walk(el, ctx, clipped=False):
            tx, ty, sx, sy = ctx
            yield el, (tx, ty, sx, sy), clipped
            for ch in el:
                if not isinstance(ch.tag, str):
                    continue
                ntx, nty, nsx, nsy = _parse_transform(ch.get("transform"))
                yield from walk(
                    ch,
                    (tx + ntx * sx, ty + nty * sy, sx * nsx, sy * nsy),
                    clipped or bool(ch.get("clip-path")),
                )

        elements = list(walk(root, (0.0, 0.0, 1.0, 1.0)))

        # ---- duplicate ids -------------------------------------------
        ids = [el.get("id") for el, _c, _k in elements if el.get("id")]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            add(fname, "DUPID", f"duplicate id(s): {sorted(dupes)[:3]}")

        for el, ctx, clipped in elements:
            tg = _tag(el)

            # ---- transform clobbering -------------------------------
            # Only a DIRECT, non-additive animateTransform child is a problem.
            # additive="sum"/"add" composes on purpose (the sheen sweepers).
            own_tf = el.get("transform")
            if own_tf:
                for ch in el:
                    if not isinstance(ch.tag, str):
                        continue
                    if _tag(ch) != "animateTransform":
                        continue
                    if ch.get("attributeName") != "transform":
                        continue
                    if (ch.get("additive") or "").lower() in ("sum", "add"):
                        continue
                    add(fname, "SMIL",
                        f"<{tg}> has transform={own_tf!r} AND a direct "
                        f"non-additive animateTransform child "
                        f"(the child replaces the attribute)")
                    break

            # ---- permanently invisible ------------------------------
            op = el.get("opacity")
            if op is not None and _num(op) == 0.0:
                ok = False
                for ch in el:
                    if not isinstance(ch.tag, str):
                        continue
                    if _tag(ch) != "animate":
                        continue
                    if ch.get("attributeName") != "opacity":
                        continue
                    kv = ch.get("keyTimes")
                    if kv is None:
                        ok = True
                        break
                    good, _why = _keytimes_ok(kv)
                    if good:
                        ok = True
                        break
                if not ok:
                    add(fname, "INVISIBLE",
                        f"<{tg}> pinned opacity=0 with no valid opacity "
                        f"animation child")

            # ---- bounds ---------------------------------------------
            # Skip anything positioned/scaled by an ancestor, or clipped by
            # one: an off-canvas sheen rect inside a clipPath is intentional.
            if tg == "rect" and vw and vh and not clipped:
                tx, ty, sx, sy = ctx
                if tx or ty or sx != 1.0 or sy != 1.0:
                    pass
                else:
                    x = _num(el.get("x")) or 0.0
                    y = _num(el.get("y")) or 0.0
                    rw = _num(el.get("width"))
                    rh = _num(el.get("height"))
                    if rw is not None and rh is not None:
                        x1, y1 = x + rw, y + rh
                        if (x < vx - 2 or y < vy - 2
                                or x1 > vx + vw + 2 or y1 > vy + vh + 2):
                            add(fname, "BOUNDS",
                                f"rect ({x:.0f},{y:.0f})-({x1:.0f},{y1:.0f}) "
                                f"outside viewBox {vw:.0f}x{vh:.0f}")

            # ---- paints ---------------------------------------------
            for attr in ("fill", "stroke", "stop-color"):
                v = el.get(attr)
                if v is None:
                    continue
                if v.startswith("url(") or v.lower() in NAMED_COLOURS:
                    continue
                if re.fullmatch(r"#[0-9a-fA-F]{3,8}", v):
                    continue
                add(fname, "PAINT", f'{attr}="{v[:40]}"')

            # ---- animation arity / dur / keyTimes ------------------
            if tg in ("animate", "animateTransform", "animateMotion"):
                kv = el.get("keyTimes")
                vv = el.get("values")
                pp = el.get("keyPoints")
                if kv and vv and len(kv.split(";")) != len(vv.split(";")):
                    add(fname, "SMIL",
                        f"{tg}: keyTimes({len(kv.split(';'))}) != "
                        f"values({len(vv.split(';'))})")
                if kv and pp and len(kv.split(";")) != len(pp.split(";")):
                    add(fname, "SMIL", f"{tg}: keyTimes != keyPoints")
                if tg == "animateMotion" and not (
                        el.get("path") or pp
                        or any(isinstance(c.tag, str) and _tag(c) == "mpath"
                               for c in el)):
                    add(fname, "SMIL",
                        "<animateMotion> with no path/mpath/keyPoints")
                dur = el.get("dur")
                if dur is not None and not re.fullmatch(r"\d+(?:\.\d+)?s", dur):
                    add(fname, "SMIL", f"bad dur: {dur!r}")
                if kv:
                    good, why = _keytimes_ok(kv)
                    if not good:
                        add(fname, "SMIL", f"{tg} keyTimes {why}: {kv[:56]}")

        # ---- external references ------------------------------------
        for el, _c, _k in elements:
            href = el.get("href")
            if href and not href.startswith("#"):
                add(fname, "EXTERNAL", f"external ref: {href[:60]}")

    return findings


def _report(findings, total_files, verbose):
    """Print a compact summary; full detail with verbose=True."""
    by_file = {}
    for fname, sev, msg in findings:
        by_file.setdefault(fname, []).append((sev, msg))

    print(f"  assets scanned : {total_files}")
    print(f"  files flagged  : {len(by_file)}")
    print(f"  findings       : {len(findings)}")

    if not findings:
        print("  result         : CLEAN")
        return

    counts = {}
    for _f, sev, _m in findings:
        counts[sev] = counts.get(sev, 0) + 1
    summary = "  ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"  by severity    : {summary}")

    # Always show the worst few; verbose shows everything.
    ordered = sorted(
        by_file.items(),
        key=lambda kv: min(SEVERITY_ORDER.get(s, 9) for s, _ in kv[1]),
    )
    shown = ordered if verbose else ordered[:10]
    for fname, items in shown:
        worst = min(SEVERITY_ORDER.get(s, 9) for s, _ in items)
        sev = next(s for s, _ in items if SEVERITY_ORDER.get(s, 9) == worst)
        print(f"    [{sev}] {fname} ({len(items)})")
        if verbose:
            seen = set()
            for s, m in items:
                if (s, m) in seen:
                    continue
                seen.add((s, m))
                print(f"        {m}")
        else:
            for s, m in items[:2]:
                print(f"        {m}")

    if len(ordered) > len(shown):
        print(f"    ... and {len(ordered) - len(shown)} more file(s) "
              f"(re-run with --verbose for the full list)")
    print("  result         : FAILED")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    verbose = "--verbose" in argv or "-v" in argv

    assets = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "assets")
    if not os.path.isdir(assets):
        print(f"assets directory not found: {assets}", file=sys.stderr)
        return 2

    files = glob.glob(os.path.join(assets, "*.svg"))
    findings = audit(assets, verbose=verbose)
    print("SVG audit")
    _report(findings, len(files), verbose)
    # Non-zero exit so a CI job (the daily regenerate workflow) fails loudly.
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())