#!/usr/bin/env python3
"""Generate static/css/demo.css, the CSS for the home page's animated demo.

The demo (templates/partials/demo_keelinfra.html) is pure CSS, one 18s loop.
Each line that appears and each matrix cell that turns green has its own
keyframes, so the timeline lives here as plain data -- "visible from 15% of
the loop", "cell (2, 1) goes green at 63.2%" -- and this script writes the
CSS. Edit this script, not demo.css; CI runs --check on every build.

    python3 scripts/gen_demo_css.py           # rewrite static/css/demo.css
    python3 scripts/gen_demo_css.py --check   # exit 1 if it is stale

Ported from the keelinfra demo on shenxianpeng.dev
(shenxianpeng/blog, .github/scripts/gen_demo_css.py). The timeline and the
.ki-demo-* class names are kept identical so a change can be carried across
either way. Local differences: the site's monospace stack instead of Geist
Mono, a lighter shadow for the light hero, the Actions title in the static
frame, rounded corners on the last matrix row (:last-of-type matched the
echo line, not the row), and zoom steps for this site's 24px gutters.
"""

import argparse
import os
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_PATH = os.path.join(SITE, "static", "css", "demo.css")

# Default fade, in percent of the loop, when an element appears or disappears.
F = 0.8


def vis(name, intervals, f=F):
    """Opacity keyframes: visible during each (start, end) window, else hidden.

    Windows are percentages, in order and non-overlapping. A window starting at
    0 or ending at 100 is visible across the loop boundary.
    """
    pts = {}
    if intervals[0][0] > 0:
        pts[0] = 0
    for a, b in intervals:
        if a > 0:
            pts[round(a - f, 2)] = 0
            pts[a] = 1
        else:
            pts[0] = 1
        pts[b] = 1
        if b < 100:
            pts[round(b + f, 2)] = 0
        else:
            pts[100] = 1
    if intervals[-1][1] < 100:
        pts[100] = 0
    body = " ".join(f"{k:g}% {{ opacity: {pts[k]}; }}" for k in sorted(pts))
    return f"@keyframes {name} {{ {body} }}"


def props(name, frames):
    """Keyframes from (selector, declarations) pairs, written as given."""
    body = " ".join(f"{k} {{ {v} }}" for k, v in frames)
    return f"@keyframes {name} {{ {body} }}"


# ---- keelinfra (18s loop) -----------------------------------------------------
# 0-45 terminal: ./configure typed (2-7) and confirmed (9), ./install typed
# (11-13), the ten plays of playbooks/install.yml (15-33), the recap (36-39).
# 47-97 upgrade matrix: each path's four checks turn green column by column,
# rows staggered; the session assertion's echo appears at 90.

MONO = 'ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace'

ki = f"""/* keelinfra: ./configure and ./install, then the nightly upgrade matrix. */

.hero-demo {{ margin-top: 34px; }}
.hero-demo figcaption {{ margin-top: 14px; max-width: 600px; font-size: 13.5px; color: var(--muted); overflow-wrap: anywhere; }}
.hero-demo figcaption code {{ font-size: 12.5px; color: var(--ink); }}
.ki-demo-win {{ width: 600px; height: 430px; overflow: hidden; border: 1px solid #30363d; border-radius: 10px; background: #0d1117; color: #e6edf3; text-align: left; box-shadow: 0 18px 44px rgb(11 34 57 / 0.22); }}
.ki-demo-bar {{ position: relative; display: flex; align-items: center; height: 32px; padding: 0 12px; border-bottom: 1px solid #30363d; background: #161b22; }}
.ki-demo-dots {{ display: flex; gap: 6px; }}
.ki-demo-dots i {{ width: 10px; height: 10px; border-radius: 50%; background: #30363d; }}
.ki-demo-title {{ position: absolute; inset: 0; text-align: center; color: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; }}
.ki-demo-title b {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-weight: 500; opacity: 0; }}
.ki-demo-t1 {{ opacity: 1; animation: ki-demo-t1 18s linear infinite; }}
.ki-demo-t2 {{ animation: ki-demo-t2 18s linear infinite; }}
.ki-demo-body {{ position: relative; height: 398px; }}
.ki-demo-term, .ki-demo-matrix {{ position: absolute; inset: 0; padding: 14px 16px; opacity: 0; }}
.ki-demo-term {{ font-family: {MONO}; font-size: 12px; line-height: 17px; animation: ki-demo-term 18s ease infinite; }}
.ki-demo-matrix {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", sans-serif; font-size: 12.5px; animation: ki-demo-matrix 18s ease infinite; }}
.ki-demo-ln {{ overflow: hidden; white-space: nowrap; }}
.ki-demo-ps {{ color: #7ee787; }}
.ki-demo-type {{ display: inline-block; overflow: hidden; vertical-align: bottom; white-space: nowrap; }}
.ki-demo-type1 {{ width: 36ch; animation: ki-demo-type1 18s infinite; }}
.ki-demo-type2 {{ width: 9ch; animation: ki-demo-type2 18s infinite; }}
.ki-demo-ok {{ color: #7ee787; }}
.ki-demo-play {{ color: #8b949e; }}
.ki-demo-host {{ display: inline-block; width: 12ch; color: #e3b341; }}
.ki-demo-mhead {{ display: flex; align-items: baseline; justify-content: space-between; padding-bottom: 12px; }}
.ki-demo-mhead strong {{ font-size: 15px; }}
.ki-demo-mhead span, .ki-demo-row em {{ color: #8b949e; font-style: normal; }}
.ki-demo-grid {{ display: grid; grid-template-columns: 170px repeat(4, minmax(0, 1fr)); align-items: center; padding: 0 12px; white-space: nowrap; }}
.ki-demo-gh {{ height: 30px; border: 1px solid #30363d; border-radius: 6px 6px 0 0; background: #161b22; color: #8b949e; font-size: 11.5px; font-weight: 600; }}
.ki-demo-gh span:not(:first-child), .ki-demo-cell {{ justify-self: center; }}
.ki-demo-row {{ height: 46px; border: 1px solid #30363d; border-top: 0; white-space: nowrap; }}
.ki-demo-row:nth-last-child(2) {{ border-radius: 0 0 6px 6px; }}
.ki-demo-cell {{ position: relative; width: 16px; height: 16px; }}
.ki-demo-cell i {{ position: absolute; inset: 0; display: flex; opacity: 0; }}
.ki-demo-spin {{ transform-box: view-box; transform-origin: 8px 8px; animation: ki-demo-spin 1s linear infinite; }}
.ki-demo-echo {{ margin-top: 14px; color: #7ee787; font-family: {MONO}; font-size: 12px; opacity: 0; animation: ki-demo-echo 18s ease infinite; }}
"""
PLAYS = 10
KI_LINES = {"l1": 9, "l2": 10.5, "recap": 36, "n0": 37, "n1": 38, "n2": 39}
for key in KI_LINES:
    ki += f".ki-demo-{key} {{ opacity: 0; animation: ki-demo-{key} 18s linear infinite; }}\n"
for i in range(PLAYS):
    ki += f".ki-demo-p{i} {{ opacity: 0; animation: ki-demo-p{i} 18s linear infinite; }}\n"


def ki_cell_time(row, col):
    """When cell (row, col) of the matrix turns green, in percent of the loop."""
    return round(50 + col * 10 + row * 1.6, 2)


KI_ROWS, KI_COLS, KI_RUN = 5, 4, 3.5
for r in range(KI_ROWS):
    for col in range(KI_COLS):
        for st in "prd":
            ki += f".ki-demo-c{r}{col}{st} {{ animation: ki-demo-c{r}{col}{st} 18s linear infinite; }}\n"

ki_k = [
    vis("ki-demo-term", [(1, 45)]),
    vis("ki-demo-matrix", [(47, 97)]),
    vis("ki-demo-t1", [(0, 46), (98, 100)], 0.3),
    vis("ki-demo-t2", [(46, 98)], 0.3),
    vis("ki-demo-echo", [(90, 100)]),
    props("ki-demo-type1", [("0%, 2%", "width: 0; animation-timing-function: steps(36, end);"), ("7%, 100%", "width: 36ch;")]),
    props("ki-demo-type2", [("0%, 11%", "width: 0; animation-timing-function: steps(9, end);"), ("13%, 100%", "width: 9ch;")]),
    props("ki-demo-spin", [("100%", "transform: rotate(360deg);")]),
]
for key, t in KI_LINES.items():
    ki_k.append(vis(f"ki-demo-{key}", [(t, 100)], 0.3))
for i in range(PLAYS):
    ki_k.append(vis(f"ki-demo-p{i}", [(15 + i * 2, 100)], 0.3))
for r in range(KI_ROWS):
    for col in range(KI_COLS):
        t = ki_cell_time(r, col)
        ki_k.append(vis(f"ki-demo-c{r}{col}p", [(0, round(t - KI_RUN, 2))], 0.3))
        ki_k.append(vis(f"ki-demo-c{r}{col}r", [(round(t - KI_RUN, 2), t)], 0.3))
        ki_k.append(vis(f"ki-demo-c{r}{col}d", [(t, 100)], 0.3))

# After the keyframes: the frame shown when animations are off, then scaling.
tail = """
/* Static frame for reduced motion: the finished matrix, under its own title.
   The keyframes override these while the demo runs. site.css already turns
   animations off for prefers-reduced-motion; the rule below keeps this file
   correct on its own. */
.ki-demo-matrix, .ki-demo-echo, .ki-demo-title .ki-demo-t2, .ki-demo-cell i:last-child { opacity: 1; }

@media (prefers-reduced-motion: reduce) {
  .ki-demo * { animation: none !important; }
}

/* The demo is laid out in fixed pixels, 600px wide; scale it to the column
   (viewport minus the 24px gutters on .wrap). */
@media (max-width: 647px) {
  .ki-demo-win { zoom: 0.75; }
}

@media (max-width: 497px) {
  .ki-demo-win { zoom: 0.52; }
}

@media (max-width: 359px) {
  .ki-demo-win { zoom: 0.45; }
}
"""

HEADER = "/* GENERATED by scripts/gen_demo_css.py -- edit the script, not this file. */\n\n"


def build():
    """Return the full contents of demo.css."""
    return HEADER + ki + "\n" + "\n".join(ki_k) + "\n" + tail


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if demo.css is out of date")
    args = parser.parse_args()

    css = build()
    try:
        with open(CSS_PATH, encoding="utf-8") as f:
            current = f.read()
    except FileNotFoundError:
        current = None
    if args.check:
        if current != css:
            print("static/css/demo.css is out of date; run scripts/gen_demo_css.py", file=sys.stderr)
            return 1
        print("static/css/demo.css is up to date")
        return 0
    if current != css:
        with open(CSS_PATH, "w", encoding="utf-8") as f:
            f.write(css)
        print("updated static/css/demo.css")
    else:
        print("static/css/demo.css already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
