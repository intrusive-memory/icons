#!/usr/bin/env python3
"""Generate SF Symbols templates for the custom storyboard icons.

Writes the storyboard and storyboard.sequence symbolsets into
Sources/Icons/Resources/Icons.xcassets. Each SVG is an SF Symbols 4 template
(Ultralight-S, Regular-S, Black-S) that also opens in SF Symbols.app.

The glyphs are built from filled outlines (SF Symbols does not accept strokes).
Every weight emits the same path commands, so Xcode can interpolate the other
six weights and the M/L scales.

  storyboard           one panel with two caption lines under it
  storyboard.sequence  two stacked panels, the back one showing only its left
                       half, pierced left to right by an arrow

In hierarchical mode the panels (storyboard) and the front panel + arrow
(sequence) are primary; captions and the back panel are secondary.

Usage: python3 Scripts/generate-storyboard-symbols.py
"""

from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "Sources" / "Icons" / "Resources" / "Icons.xcassets"

KAPPA = 0.5522847498
BASELINE_S = 696.0
CAP_HEIGHT = 70.459
OPTICAL_CENTER = -CAP_HEIGHT / 2  # symbols center on half the cap height
SIDEBEARING = 3.0

# Weight column centers, taken from the template SF Symbols exports.
WEIGHTS = {
    "Ultralight": {"column": 559.711, "stroke": 2.4},
    "Regular": {"column": 1449.84, "stroke": 6.6},
    "Black": {"column": 2933.4, "stroke": 12.0},
}


def fmt(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def rounded_rect(x, y, w, h, r, clockwise=True):
    """Closed rounded-rect subpath. Same command sequence for every radius."""
    k = r * KAPPA
    if clockwise:
        pts = [
            ("M", (x + r, y)),
            ("L", (x + w - r, y)),
            ("C", (x + w - r + k, y), (x + w, y + r - k), (x + w, y + r)),
            ("L", (x + w, y + h - r)),
            ("C", (x + w, y + h - r + k), (x + w - r + k, y + h), (x + w - r, y + h)),
            ("L", (x + r, y + h)),
            ("C", (x + r - k, y + h), (x, y + h - r + k), (x, y + h - r)),
            ("L", (x, y + r)),
            ("C", (x, y + r - k), (x + r - k, y), (x + r, y)),
        ]
    else:
        pts = [
            ("M", (x + r, y)),
            ("C", (x + r - k, y), (x, y + r - k), (x, y + r)),
            ("L", (x, y + h - r)),
            ("C", (x, y + h - r + k), (x + r - k, y + h), (x + r, y + h)),
            ("L", (x + w - r, y + h)),
            ("C", (x + w - r + k, y + h), (x + w, y + h - r + k), (x + w, y + h - r)),
            ("L", (x + w, y + r)),
            ("C", (x + w, y + r - k), (x + w - r + k, y), (x + w - r, y)),
            ("L", (x + r, y)),
        ]
    out = []
    for cmd, *coords in pts:
        out.append(cmd + " ".join(f"{fmt(px)} {fmt(py)}" for px, py in coords))
    return "".join(out) + "Z"


def frame(x, y, w, h, stroke):
    """Outlined panel: outer rect clockwise, inner hole counter-clockwise."""
    outer_r = 3.0 + stroke * 0.6
    inner_r = max(outer_r - stroke, 0.6)
    return rounded_rect(x, y, w, h, outer_r) + rounded_rect(
        x + stroke, y + stroke, w - 2 * stroke, h - 2 * stroke, inner_r, clockwise=False
    )


def capsule(x, cy, w, stroke):
    """Horizontal caption line with round caps, centered on cy."""
    return rounded_rect(x, cy - stroke / 2, w, stroke, stroke / 2 * 0.999)


def storyboard(stroke):
    width, panel_h = 92.0, 56.0
    gap = 8.0 + stroke * 0.25
    pitch = 5.5 + stroke  # caption line spacing
    caption1 = panel_h + gap + stroke / 2
    caption2 = caption1 + pitch
    height = caption2 + stroke / 2
    top = OPTICAL_CENTER - height / 2
    x = SIDEBEARING
    panels = frame(x, top, width, panel_h, stroke)
    captions = capsule(x, top + caption1, width * 0.72, stroke) + capsule(
        x, top + caption2, width * 0.42, stroke
    )
    return width, [("primary", panels), ("secondary", captions)]


def to_path(pts):
    return "".join(
        cmd + " ".join(f"{fmt(px)} {fmt(py)}" for px, py in coords) for cmd, *coords in pts
    ) + "Z"


def pierced_panel(x, y, w, h, stroke, cut, open_right=False):
    """Panel outline split at its vertical middle so the arrow can pass through.

    `cut` is the half-height of the opening in the side edges. With open_right
    the panel's right edge is hidden behind the next panel, leaving a bracket.
    Returns the upper and lower pieces as one path.
    """
    r = 3.0 + stroke * 0.6
    ri = max(r - stroke, 0.6)
    k, ki = r * KAPPA, ri * KAPPA
    xi, yi, xr, xri = x + stroke, y + stroke, x + w, x + w - stroke
    yc = y + h / 2 - cut
    pts = [
        ("M", (x, yc)),
        ("L", (x, y + r)),
        ("C", (x, y + r - k), (x + r - k, y), (x + r, y)),
    ]
    if open_right:
        pts += [("L", (xr, y)), ("L", (xr, yi))]
    else:
        pts += [
            ("L", (xr - r, y)),
            ("C", (xr - r + k, y), (xr, y + r - k), (xr, y + r)),
            ("L", (xr, yc)),
            ("L", (xri, yc)),
            ("L", (xri, yi + ri)),
            ("C", (xri, yi + ri - ki), (xri - ri + ki, yi), (xri - ri, yi)),
        ]
    pts += [
        ("L", (xi + ri, yi)),
        ("C", (xi + ri - ki, yi), (xi, yi + ri - ki), (xi, yi + ri)),
        ("L", (xi, yc)),
    ]
    mid = y + h / 2
    lower = [(cmd, *[(px, 2 * mid - py) for px, py in coords]) for cmd, *coords in pts]
    return to_path(pts) + to_path(lower)


def arrow(x, cy, length, shaft, stroke):
    """Left-to-right arrow: round-capped shaft with a triangular head."""
    half = shaft / 2
    xh, xe = x + length - arrow_head_len(stroke), x + length
    head_half = arrow_head_half(stroke)
    k = half * KAPPA
    return to_path([
        ("M", (x + half, cy - half)),
        ("L", (xh, cy - half)),
        ("L", (xh, cy - head_half)),
        ("L", (xe, cy)),
        ("L", (xh, cy + head_half)),
        ("L", (xh, cy + half)),
        ("L", (x + half, cy + half)),
        ("C", (x + half - k, cy + half), (x, cy + k), (x, cy)),
        ("C", (x, cy - k), (x + half - k, cy - half), (x + half, cy - half)),
    ])


def arrow_head_len(stroke):
    return 7.0 + stroke * 1.3


def arrow_head_half(stroke):
    return 4.5 + stroke * 0.9


def storyboard_sequence(stroke):
    panel_w, panel_h = 60.0, 45.0  # 4:3
    offset = panel_w / 2  # each earlier panel shows only its left half
    knockout = 2.5 + stroke * 0.5  # gap between a back panel and the one in front
    shaft = stroke * 0.75  # thinner than the frames so the panels stay dominant
    cut = shaft / 2 + 1.5 + stroke * 0.2  # opening in each edge the arrow crosses
    overshoot = arrow_head_len(stroke) + 4.0  # arrowhead clears the front panel
    width = panel_w + offset + overshoot
    top = OPTICAL_CENTER - panel_h / 2
    x0 = SIDEBEARING
    backs = "".join(
        pierced_panel(x0 + i * offset, top, offset - knockout, panel_h, stroke, cut, open_right=True)
        for i in range(1)
    )
    front = pierced_panel(x0 + offset, top, panel_w, panel_h, stroke, cut)
    shaft_path = arrow(x0, top + panel_h / 2, width, shaft, stroke)
    return width, [("secondary", backs), ("primary", front + shaft_path)]


STYLE = """ <style>.monochrome-0 {fill:#000000}
.monochrome-1 {fill:#000000}

.multicolor-0:tintColor {fill:#007AFF}
.multicolor-1:tintColor {fill:#007AFF}

.hierarchical-0:primary {fill:#212121}
.hierarchical-0:secondary {fill:#8E8E93}
.hierarchical-1:primary {fill:#212121}
.hierarchical-1:secondary {fill:#8E8E93}

.SFSymbolsPreviewWireframe {fill:none;opacity:1.0;stroke:black;stroke-width:0.5}
</style>"""

def layer_class(index, level):
    return (
        f"monochrome-{index} multicolor-{index}:tintColor "
        f"hierarchical-{index}:{level} SFSymbolsPreviewWireframe"
    )

CONTENTS_JSON = """{{
  "info" : {{
    "author" : "xcode",
    "version" : 1
  }},
  "symbols" : [
    {{
      "filename" : "{name}.svg",
      "idiom" : "universal"
    }}
  ]
}}
"""

TEXT = "stroke:none;fill:black;font-family:sans-serif;font-size:13;"
GUIDE = "fill:none;stroke:#27AAE1;opacity:1;stroke-width:0.5;"
MARGIN = "fill:none;stroke:#00AEEF;stroke-width:0.5;opacity:1.0;"


def template(name, build):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
        '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="3300" height="2200">',
        f' <!--glyph: "{name}", point size: 100.0, generated by Scripts/generate-storyboard-symbols.py-->',
        STYLE,
        ' <g id="Notes">',
        '  <rect height="2200" id="artboard" style="fill:white;opacity:1" width="3300" x="0" y="0"/>',
        '  <line style="fill:none;stroke:black;opacity:1;stroke-width:0.5;" x1="263" x2="3036" y1="292" y2="292"/>',
        f'  <text style="{TEXT}font-weight:bold;" transform="matrix(1 0 0 1 263 322)">Weight/Scale Variations</text>',
    ]
    for weight, spec in WEIGHTS.items():
        lines.append(
            f'  <text style="{TEXT}text-anchor:middle;" transform="matrix(1 0 0 1 {spec["column"]} 322)">{weight}</text>'
        )
    lines += [
        '  <line style="fill:none;stroke:black;opacity:1;stroke-width:0.5;" x1="263" x2="3036" y1="1903" y2="1903"/>',
        f'  <text id="template-version" style="{TEXT}text-anchor:end;" transform="matrix(1 0 0 1 3036 1933)">Template v.4.0</text>',
        f'  <text id="descriptive-name" style="{TEXT}text-anchor:end;" transform="matrix(1 0 0 1 3036 1969)">{name}</text>',
        " </g>",
        ' <g id="Guides">',
    ]
    for scale, baseline in (("S", 696), ("M", 1126), ("L", 1556)):
        capline = fmt(baseline - CAP_HEIGHT)
        lines.append(f'  <line id="Baseline-{scale}" style="{GUIDE}" x1="263" x2="3036" y1="{baseline}" y2="{baseline}"/>')
        lines.append(f'  <line id="Capline-{scale}" style="{GUIDE}" x1="263" x2="3036" y1="{capline}" y2="{capline}"/>')

    groups = []
    for weight, spec in WEIGHTS.items():
        width, layers = build(spec["stroke"])
        advance = width + 2 * SIDEBEARING
        left = spec["column"] - advance / 2
        right = left + advance
        for side, x in (("left", left), ("right", right)):
            lines.append(
                f'  <line id="{side}-margin-{weight}-S" style="{MARGIN}" x1="{fmt(x)}" x2="{fmt(x)}" y1="600.785" y2="720.121"/>'
            )
        group = [f'  <g id="{weight}-S" transform="matrix(1 0 0 1 {fmt(left)} {fmt(BASELINE_S)})">']
        for index, (level, d) in enumerate(layers):
            group.append(f'   <path class="{layer_class(index, level)}" d="{d}"/>')
        group.append("  </g>")
        groups.append(group)
    lines.append(" </g>")
    lines.append(' <g id="Symbols">')
    for group in reversed(groups):  # SF Symbols lists Black first
        lines += group
    lines += [" </g>", "</svg>", ""]
    return "\n".join(lines)


def main():
    for name, build in (("storyboard", storyboard), ("storyboard.sequence", storyboard_sequence)):
        symbolset = OUT_DIR / f"{name}.symbolset"
        symbolset.mkdir(parents=True, exist_ok=True)
        path = symbolset / f"{name}.svg"
        path.write_text(template(name, build))
        (symbolset / "Contents.json").write_text(CONTENTS_JSON.format(name=name))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
