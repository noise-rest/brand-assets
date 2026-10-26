#!/usr/bin/env python3
"""Draw docs/styleguide.svg: a one-image style guide with outlined text. Values come from design/tokens.json."""
import re
from pathlib import Path

import outline as o

C = o.C
W, H, M = 1200, 600, 48
LINE = "#DDE2EA"
out = []


def text(s, x, y, size, weight, fill, tracking=0.0):
    out.append(f'<path fill="{fill}" d="{o.outline(s, weight, size, x, y, tracking)[0]}"/>')


def card(x, y, w, h, fill):
    stroke = f' stroke="{LINE}"' if fill in (C["white"], C["snow"]) else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}"{stroke}/>')


def place(svg, cx, cy, w):
    """Nest an SVG from outline.py, centred on (cx, cy), w units wide."""
    vx, vy, vw, vh = map(float, re.search(r'viewBox="([^"]+)"', svg).group(1).split())
    h = w * vh / vw
    head = f'<svg x="{o.n(cx - w / 2)}" y="{o.n(cy - h / 2)}" width="{o.n(w)}" height="{o.n(h)}" viewBox="{vx} {vy} {vw} {vh}">'
    out.append(re.sub(r"<svg[^>]*>", head, svg, count=1))


ink, snow, night = C["ink"], C["snow"], C["night"]
out.append(f'<rect width="{W}" height="{H}" fill="{snow}"/>')
text("NOISE REST · STYLE GUIDE", M, 58, 14, 400, C["slate"], 0.2)

# Logos: primary, reversed, then the one-colour versions and the mark.
card(M, 88, 572, 312, C["white"])
place(o.lockup_svg(ink, o.ACCENT), M + 286, 244, 360)
card(652, 88, 500, 156, night)
place(o.lockup_svg(snow, o.ACCENT_DARK), 902, 166, 170)
for i, (fill, svg, w) in enumerate([
    (C["white"], o.lockup_svg(ink, ink), 120),
    (night, o.lockup_svg(snow, snow), 120),
    (C["white"], o.mark_svg(o.ACCENT), 96),
]):
    x = 652 + i * 172
    card(x, 260, 156, 140, fill)
    place(svg, x + 78, 330, w)

# Colour.
swatches = [("ink / night", ink), ("slate", C["slate"]), (C["accent"]["default"] + " (accent)", o.ACCENT),
            ("snow", snow), ("white", C["white"])]
for i, (name, hex_) in enumerate(swatches):
    x = M + i * 128
    out.append(f'<rect x="{x}" y="440" width="112" height="64" rx="8" fill="{hex_}" stroke="{LINE}"/>')
    text(name, x, 530, 11, 800, ink)
    text(hex_, x, 550, 11, 400, C["slate"])

# Rules.
for i, (k, v) in enumerate([("Font", "JetBrains Mono, noise 400 / rest 800"),
                            ("Space", "1 block height on all sides"),
                            ("Size", "S 18 px and up; below, mark only"),
                            ("Never", "overhang the line or tint noise")]):
    y = 456 + i * 30
    text(k, 720, y, 13, 800, ink)
    text(v, 790, y, 13, 400, C["slate"])

svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(out)}</svg>\n'
dest = o.ROOT / "docs/styleguide.svg"
dest.write_text(svg)
print("wrote", dest)
