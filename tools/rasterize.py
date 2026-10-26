#!/usr/bin/env python3
"""Rasterize svg/ to png/ and favicon.ico with ImageMagick. Run tools/outline.py first."""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "design/tokens.json").read_text())["color"]
SIZE = 1024  # one export size for lockups, mark and squares
FILL = round(SIZE / 1.4)  # logo width inside a square: about 0.6 block height of margin


def magick(svg, out, *args):
    subprocess.run(["magick", "-background", "none", "-density", "1200", "-define", "png:exclude-chunks=date,time", ROOT / "svg" / f"{svg}.svg", *args, "-strip", out], check=True)


def main():
    png = ROOT / "png"
    (png / "square").mkdir(parents=True, exist_ok=True)
    for name in ("logo", "logo-reversed", "logo-mono", "logo-mono-reversed", "mark"):
        magick(name, png / f"{name}.png", "-resize", f"{SIZE}x")
    for name, svg, ground in (("logo-light", "logo", "snow"), ("logo-dark", "logo-reversed", "night"),
                              ("mark-light", "mark", "snow"), ("mark-dark", "mark", "night")):
        magick(svg, png / "square" / f"{name}.png", "-resize", f"{FILL}x", "-background", C[ground],
               "-gravity", "center", "-extent", f"{SIZE}x{SIZE}")
    for s in (16, 48):
        magick(f"favicon-{s}", png / f"favicon-{s}.png", "-resize", f"{s}x{s}")
    magick("favicon-48", png / "app-icon.png", "-resize", "512x512")
    with tempfile.TemporaryDirectory() as tmp:  # the .ico also holds 32 px, which has no PNG in the repo
        magick("favicon-48", Path(tmp) / "32.png", "-resize", "32x32")
        subprocess.run(["magick", png / "favicon-16.png", Path(tmp) / "32.png", png / "favicon-48.png", ROOT / "favicon.ico"], check=True)
    print("wrote PNGs and favicon.ico")


if __name__ == "__main__":
    main()
