#!/usr/bin/env python3
"""Outline the J11 lockup to SVG paths. Geometry and colours come from design/tokens.json."""
import json
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
T = json.loads((ROOT / "design/tokens.json").read_text())
C, L = T["color"], T["logo"]
ACCENT = C["accent"][C["accent"]["default"]]
ACCENT_DARK = C["accent"]["sageOnDark"] if C["accent"]["default"] == "sage" else ACCENT
S = 100  # font size of "noise" in SVG units
WEIGHTS = {400: "Regular", 800: "ExtraBold"}
FONTS = {}


def font(weight):
    if weight not in FONTS:
        FONTS[weight] = TTFont(ROOT / f"fonts/JetBrainsMono-{WEIGHTS[weight]}.ttf")
    return FONTS[weight]


def n(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def outline(text, weight, size, x0, base, tracking=0.0):
    """Return (path d, ink xMin, ink xMax, ink yMin, ink yMax, advance); y points down."""
    f = font(weight)
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    k = size / upm
    svg_pen, bounds, x = SVGPathPen(gs, ntos=n), BoundsPen(gs), x0
    for ch in text:
        glyph = gs[cmap[ord(ch)]]
        for pen in (svg_pen, bounds):
            glyph.draw(TransformPen(pen, (k, 0, 0, -k, x, base)))
        x += glyph.width * k + tracking * size
    xmin, ymin, xmax, ymax = bounds.bounds
    return svg_pen.getCommands(), xmin, xmax, ymin, ymax, x - x0 - tracking * size


def rrect_bottom(x, y, w, h, r):
    """Rectangle with rounded bottom corners."""
    return (f"M{n(x)} {n(y)}H{n(x + w)}V{n(y + h - r)}Q{n(x + w)} {n(y + h)} {n(x + w - r)} {n(y + h)}"
            f"H{n(x + r)}Q{n(x)} {n(y + h)} {n(x)} {n(y + h - r)}Z")


def lockup():
    noise_w, rest_w = L["noise"]["weight"], L["rest"]["weight"]
    b, r, line = L["block"], L["rest"], L["line"]
    track = L["noise"]["tracking"]
    # Line = visible ink of "noise": measure, then shift so the ink starts at x = 0.
    ink_x0 = outline(L["noise"]["text"], noise_w, S, 0, 0, track)[1]
    nx0, nx1, ny0 = outline(L["noise"]["text"], noise_w, S, -ink_x0, 0, track)[1:4]
    letters, x = [], -ink_x0
    for ch in L["noise"]["text"]:  # one path per letter, so each can fade
        d, *_, adv = outline(ch, noise_w, S, x, 0)
        letters.append(d)
        x += adv + track * S
    line_w, line_y, line_h = nx1 - nx0, L["gap"] * S, line["height"] * S
    # Block: CSS line box of "rest" (hhea ascent + descent), as in the board 13 reference.
    f = font(rest_w)
    rs = r["size"] * S
    asc = f["hhea"].ascent / f["head"].unitsPerEm * rs
    desc = -f["hhea"].descent / f["head"].unitsPerEm * rs
    pad_x = b["padX"] * S
    block_top = line_y + line_h
    adv = outline(r["text"], rest_w, rs, 0, 0)[5]
    block_w = adv + 2 * pad_x
    block_h = b["padTop"] * S + asc + desc + b["padBottom"] * S
    block_x = nx0 + (line_w - block_w) / 2
    rd = outline(r["text"], rest_w, rs, block_x + pad_x, block_top + b["padTop"] * S + asc)[0]
    return dict(noise=letters, line=(nx0, line_y, line_w, line_h), block=(block_x, block_top, block_w, block_h),
                rest=rd, top=ny0, bottom=block_top + block_h, width=line_w)


def svg(vb, body, size=None):
    x, y, w, h = vb
    sw, sh = size or (w, h)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{n(x)} {n(y)} {n(w)} {n(h)}" '
            f'width="{n(sw)}" height="{n(sh)}">{body}</svg>\n')


def block_path(g):
    bx, by, bw, bh = g["block"]
    lh = g["line"][3]  # start inside the line: no anti-aliasing seam
    return rrect_bottom(bx, by - lh, bw, bh + lh, L["block"]["radiusBottom"] * S)


def lockup_svg(noise_color, accent):
    g = lockup()
    lx, ly, lw, lh = g["line"]
    fade = "".join(f'<path fill="{noise_color}"{"" if a == 1 else f" fill-opacity=\"{a}\""} d="{d}"/>'
                   for d, a in zip(g["noise"], L["noise"]["opacity"]))
    body = (fade +
            f'<rect x="{n(lx)}" y="{n(ly)}" width="{n(lw)}" height="{n(lh)}" fill="{accent}"/>'
            f'<path fill="{accent}" fill-rule="evenodd" d="{block_path(g)}{g["rest"]}"/>')
    return svg((0, g["top"], g["width"], g["bottom"] - g["top"]), body)


def mark_svg(color):
    g = lockup()
    lx, ly, lw, lh = g["line"]
    body = (f'<rect x="{n(lx)}" y="{n(ly)}" width="{n(lw)}" height="{n(lh)}" fill="{color}"/>'
            f'<path fill="{color}" d="{block_path(g)}"/>')
    return svg((0, ly, lw, g["bottom"] - ly), body)


def favicon_svg(size):
    f = T["favicon"]["viewBox16" if size == 16 else "viewBox48"]
    tw, th, tr = f["tile"][2], f["tile"][3], f["tile"][4] if len(f["tile"]) > 4 else 0
    lx, ly, lw, lh = f["line"]
    bx, by, bw, bh, *br = f["block"]
    body = (f'<rect width="{tw}" height="{th}" rx="{tr}" fill="{C[f["ground"]]}"/>'
            f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="{ACCENT}"/>'
            f'<path fill="{ACCENT}" d="{rrect_bottom(bx, ly, bw, bh + by - ly, br[0] if br else 0)}"/>')  # start inside the line: no seam
    return svg((0, 0, tw, th), body, (size, size))


def main():
    ink, snow = C["ink"], C["snow"]
    out = {
        "logo.svg": lockup_svg(ink, ACCENT),
        "logo-mono.svg": lockup_svg(ink, ink),
        "logo-reversed.svg": lockup_svg(snow, ACCENT_DARK),
        "logo-mono-reversed.svg": lockup_svg(snow, snow),
        "mark.svg": mark_svg(ACCENT),
        **{f"favicon-{s}.svg": favicon_svg(s) for s in (16, 48)},
    }
    d = ROOT / "svg"
    d.mkdir(exist_ok=True)
    for name, text in out.items():
        (d / name).write_text(text)
    print("wrote", len(out), "files to", d, "| accent", ACCENT)


if __name__ == "__main__":
    main()
