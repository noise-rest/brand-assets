# Noise Rest · brand assets

Logo and identity for Noise Rest: a calm, "High-Tech Zen" site on Platform Engineering, DevOps and SRE.

## Read first

1. `design/tokens.json`: colours, font and logo geometry. Code must read values from here, not hard-code them.
2. `docs/brief.md`: the original brief.
3. `exploration/index.html`: the 14 design boards (static). Board 13 tile J11 is the master; board 14 is the usage guide.

## Fixed decisions (do not change without asking)

- Wordmark: lowercase "noise" stacked over a heavy line, with "rest" knocked out of a block that hangs from the line, like the musical whole rest 𝄻.
- Font: JetBrains Mono. "noise" 400, tracked +0.12em, fading n→e. "rest" 800.
- Colour: "noise" in ink `#2E3440`; line, block and knock-out in the accent.
- The line is exactly as wide as the visible "noise"; it never overhangs.

## Build

`svg/`, `png/`, `favicon.ico` and `docs/styleguide.svg` are generated: edit `design/tokens.json` or `tools/`, never the outputs. Run `tools/outline.py`, then `tools/rasterize.py` (needs ImageMagick), then `tools/styleguide.py`. Re-running must leave `git status` clean. The "don't" examples G10–G12 in `exploration/14-usageguide.html` are hand-pasted inline SVG; update them if the geometry changes.

## Open

- Accent colour is assumed sage `#6B8B72`; not confirmed.

## Working style

- Simplified technical English (ASD-STE100); brief, forward-looking notes.
- State assumptions; ask when a requirement is ambiguous.
- Continue without asking when a step needs no input. Ask before deleting data, force-pushing, or changing anything outside this repo.
- Minimum code; follow existing patterns; few dependencies (fontTools is acceptable for outlining).
- For multi-step work, state a short plan with one check per step.
- Make commits as targeted hunks, each with one clear intent.
