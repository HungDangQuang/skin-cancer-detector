---
name: draw-diagram
description: >
  Draw a project figure (pipeline / architecture / flow diagram) in the house
  "soft-card" style — pastel rounded containers, white inner cards, thin gray
  arrows. Use when the user asks to "make/redraw a diagram", "draw the pipeline",
  "a figure for the report/slide", or "use that nice style". Produces a hand-built
  SVG (editable, renders in GitHub/browser, exports to PNG) in TWO variants —
  a portrait one for the report and a landscape 16:9 one for slides. Canonical
  examples: report_phase_1/figures/data_pipeline{,_slide}.svg. NOT for plots of
  numbers (that is a matplotlib job in the benchmark/eval scripts).
---

# House diagram style — "soft-card pipeline"

One reusable visual system for every project figure, so all report/slide diagrams
look identical. Output format is **hand-authored SVG** (not Mermaid) because the
look — centered pastel container with a title, white inner cards with a colored
accent, thin gray connector arrows — is not reproducible in Mermaid's default
renderer, and SVG stays editable + exports to PNG anywhere.

**Always produce BOTH variants** (same content, two aspect ratios) so the figure
drops into either medium without re-work:

| Variant | File suffix | Aspect | Layout | Use |
|---|---|---|---|---|
| **Portrait** | `<name>.svg` | tall (≈1000×1206) | single column, stages stacked top→down | embed in the report `.md` |
| **Landscape** | `<name>_slide.svg` | 16:9 (1600×820) | 3×2 **serpentine** grid | slide / presentation |

Canonical examples (copy from these):
[data_pipeline.svg](../../../report_phase_1/figures/data_pipeline.svg) (portrait) ·
[data_pipeline_slide.svg](../../../report_phase_1/figures/data_pipeline_slide.svg) (landscape).
Open one, duplicate a stage block, swap the palette + text, restack the cursor.

The landscape variant condenses text (shorter headers, fewer detail lines, `·`
separators) so each card reads at slide distance — don't just reflow the portrait
strings; trim them. Both variants must carry the **same corrected content**.

## 1. Anatomy (top-down single column)

```
┌─ container (pastel fill + matching border, rx=14) ──────────────┐
│                 3.x  Stage title  (18px bold, accent color)      │
│   ┌ card (white, accent border, soft shadow, rx=10) ┐  ┌ card ┐  │
│   │  Header (14px bold accent) + detail lines (12px) │  │ ...  │  │
│   └──────────────────────────────────────────────────┘  └──────┘ │
│   ▔▔▔ optional full-width "bar" (tinted, one caveat line) ▔▔▔     │
└──────────────────────────────────────────────────────────────────┘
                              │  thin gray arrow (marker-end)
                              ▼
                        (next container)
```

Three inner primitives: **card** (white, header + ≤3 detail lines), **chip**
(smaller white card, 1 bold label + 1–2 tiny lines — use for 3–4 across a row),
**bar** (full-width tinted strip, one bold caveat/summary line).

## 2. Palette tokens (one accent per stage)

| Stage color | container fill | container/ card border | accent (title+header) | bar fill | detail text |
|---|---|---|---|---|---|
| Green    | `#E7F4EC` | `#B6DEC5` / `#CDE8D7` | `#1E7A45` | `#DCEBD9` | `#5A5A5A` |
| Gray     | `#EEEDEA` | `#D8D6D1` / `#DCDAD5` | `#55534E` | `#E2E0DB` | `#5A5A5A` |
| Purple   | `#ECEBFB` | `#C9C6F0` / `#D6D3F5` | `#4B41B8` | `#E0DEF7` | `#5A5A5A` |
| Red      | `#FBEAE7` | `#F0C9C1` / `#F3D3CC` | `#B23A2A` (bar text `#9E3324`) | `#F6DBD5` | `#5A5A5A` |
| Olive    | `#EFF5E2` | `#D2E3B0` / `#DCEBC3` | `#55801F` | `#E6EFD3` | `#5A5A5A` |
| Blue     | `#E8F0FB` | `#C2D8F2` / `#D2E1F6` | `#2C63B0` | `#DCE8F8` | `#5A5A5A` |

Card fill is always `#FFFFFF`. Arrows/connectors: `#9AA0A6`, stroke-width 1.6.
Canvas background `#FFFFFF`. Pick stage colors in this order for a fresh diagram;
they read well top-to-bottom and are colorblind-distinct.

## 3. Layout grid (the numbers that keep it aligned)

- Canvas width **1000**; container `x=40 width=920 rx=14`; inner content spans
  `x=60 … 940` (20px side padding).
- Title baseline = `container_top + 34`, `text-anchor="middle" x="500"`, 18px/700.
- Cards row top = `container_top + 56`.
- **2 big cards:** `x=60 w=430` and `x=510 w=430` (20px gutter), height 66–88.
- **4 chips:** `w=208`, x = `60, 284, 508, 732` (16px gutters), height 58–66.
- **Full-width bar:** `x=60 w=880`, height 28, `10px` above it.
- Container height = `56 + <cards height> + (bar? 10+28) + 18` bottom pad.
- **Arrow** between stages: vertical line `x1=500 x2=500`, from prev bottom to
  next top (28px gap), `marker-end="url(#arrow)"`.
- Keep a running `y` cursor down the file; each stage = prev bottom + 28.

Font stack (put once on the root `<svg>`):
`-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif`.
Sizes: title 18/700, card header 14/700, detail 12, chip label 13/700, chip sub 11,
bar 12/600.

### 3b. Landscape grid (slide variant, 16:9)

6 stages don't fit one horizontal row legibly, so use a **3×2 serpentine** flow —
top row left→right, drop down the right column, bottom row right→left:

```
[3.1] → [3.2] → [3.3]          canvas 1600×820
                  ↓            cols x = 40 / 560 / 1080  (width 480, gap 40)
[3.6] ← [3.5] ← [3.4]          rows top = 50 / 430      (height 380, gap 40)
```

- Each panel is one stage; inside it, arrange the **same** primitives, sized to the
  480-wide panel: 2 cards side-by-side (`w=212`, x = `panel+20` / `panel+248`),
  4 chips as a 2×2 grid, full-width bar `w=440`. Panel centers x = `panel+240`.
- **Vertically center** the inner block within the 380-tall panel (title at
  `top+34`), so light and heavy panels line up as a clean grid.
- Arrows: horizontal in the col gaps at each row's vertical center
  (`top+170` = 220 / 600); one vertical arrow down the right column (x=1320,
  y 390→430). Leftward arrows on the bottom row (`x2<x1`, marker still at the end).
- Slide fonts run ~1px smaller (title 17, header 13, detail 11, chip 12/10, bar 11).

## 4. Reusable snippets

`<defs>` (once per file — arrowhead + soft card shadow):
```xml
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="#9AA0A6"/>
  </marker>
  <filter id="cardShadow" x="-6%" y="-6%" width="112%" height="118%">
    <feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-color="#1a1a1a" flood-opacity="0.10"/>
  </filter>
</defs>
```
Container + card (swap the 3 colors + text; `CX` = card center x):
```xml
<rect x="40" y="{T}" width="920" height="{H}" rx="14" fill="{CONTAINER}" stroke="{BORDER}"/>
<text x="500" y="{T+34}" text-anchor="middle" font-size="18" font-weight="700" fill="{ACCENT}">3.x  Title</text>
<rect x="60" y="{T+56}" width="430" height="66" rx="10" fill="#FFFFFF" stroke="{CARD_BORDER}" filter="url(#cardShadow)"/>
<text x="{CX}" y="{T+80}" text-anchor="middle" font-size="14" font-weight="700" fill="{ACCENT}">Header</text>
<text x="{CX}" y="{T+100}" text-anchor="middle" font-size="12" fill="#5A5A5A">detail line…</text>
```

## 5. Rules (so figures stay honest and on-brand)

1. **Content must match the code, not the proposal.** Verify every box against the
   real implementation before drawing — the reference figure had 3 wrong boxes
   (stronger-aug-on-malignant, CutOut/MixUp, microscope-crop) that contradict
   `docs/PREPROCESSING.md` + `configs/augmentation/*`. Cross-check with the area
   docs / `configs/` first; use a **bar** to state what was *excluded and why*.
2. One accent color per stage; never mix two accents inside a container.
3. Text must fit its box: ≤ ~50 chars/line in a 430px card, ≤ ~26 in a 208px chip.
   Use `·` as an inline separator, `→` for maps/transforms, `×` for counts.
4. Escape `&` as `&amp;` in text (breaks the SVG otherwise).
5. Keep it single-column top-down with centered arrows — matches the house look.

## 6. Render / export

SVG renders as-is in GitHub and browsers. For a PNG (slides / Word), **headless
Chrome gives an exact-size, high-DPI raster** — prefer it over `qlmanage` (which
pads the output to a square) and `rsvg-convert` (often not installed). Wrap the SVG
in a `margin:0` HTML page and screenshot at the SVG's own width/height:

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W=1600; H=820; SVG="$PWD/report_phase_1/figures/data_pipeline_slide.svg"
cat > /tmp/wrap.html <<HTML
<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;padding:0;background:#fff}img{display:block;width:${W}px;height:${H}px}</style>
</head><body><img src="file://$SVG"></body></html>
HTML
"$CHROME" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=${W},${H} --default-background-color=FFFFFFFF \
  --screenshot="${SVG%.svg}.png" "file:///tmp/wrap.html"
# → PNG at 2×  (1600×820 → 3200×1640).  Use the SVG's own W/H, not a guess.
```

Save all four files under `report_phase_1/figures/`: `<name>.svg` + `<name>.png`
(portrait) and `<name>_slide.svg` + `<name>_slide.png` (landscape). `.svg` = the
editable source, `.png` = the embed.
