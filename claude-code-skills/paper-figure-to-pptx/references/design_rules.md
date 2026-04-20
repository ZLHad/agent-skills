# Design Rules — Extended Reasoning

Read this when a design choice needs justification — either because the user pushes back on a rule, or because a new situation doesn't obviously match one of the short rules in SKILL.md.

## Rule 1: Case/Sub-Figure Labels Go Outside, No Card Frame

The short rule: place "Case A: x_u = 0 (Edge/UAV)" as vertical stacked text to the left of the region, not inside a rounded-rectangle card.

**Why**: card frames with borders/fills consume horizontal space that should go to the region's actual content. In a `12.7 × 3.0` horizontal band, a 1.5-inch card on the left eats 12% of width and makes the region feel cramped. External vertical labels occupy the same footprint but without visual weight, making the region feel larger.

**Implementation**:
```python
add_tb(slide, CASE_X, y1, CASE_W, 0.35,
       "Case A:", fs=15, bold=True, color=C_NAVY, align=PP_ALIGN.LEFT)
add_formula_tb(slide, CASE_X, y2, CASE_W, 0.40,
               [("x", 'n'), ("u", 'sub'), (" = 0", 'n')],
               fs=17, bold=True, italic=True, align=PP_ALIGN.LEFT)
add_tb(slide, CASE_X, y3, CASE_W, 0.30,
       "(Edge / UAV)", fs=12, italic=True, color=C_NAVY, align=PP_ALIGN.LEFT)
```

Three lines: label → main variable (largest) → context description. Color-code by case (C_NAVY for Case A, C_BROWN for Case B) to differentiate.

## Rule 2: Dashed Borders, Pale Fills

The short rule: region outer frames use `dash=True` with `C_PALE_*` fills, not solid borders with `C_LIGHT_*` fills.

**Why**: academic architecture diagrams use dashed borders as a semantic signal — "this is a conceptual grouping, not a physical boundary". Solid borders read as literal boxes. Pale fills (e.g. `RGBColor(0xE7, 0xF0, 0xFA)` for pale blue) are light enough that text on top stays readable; light fills (e.g. `RGBColor(0xBE, 0xDB, 0xF8)`) are too saturated and fight with content.

**Guideline**: use `C_PALE_*` for outer region fills, `C_LIGHT_*` for small secondary elements (like ISL↑/ISL↓ narrow blocks within a bigger region), `C_*` for high-importance elements (like Decode blocks in a pipeline).

## Rule 3: Formulas Use `add_formula_tb`, Always

The short rule: never put `T^{G2A}_{u→k}` in `add_tb`'s `text` param.

**Why**: two separate reasons.
1. python-pptx shows text literally — curly braces and carets render as characters, not formatting.
2. Even if you manually add superscript/subscript with Unicode characters, you lose edit-ability. The whole point of this skill is producing files where the user can open PowerPoint and edit each formula.

**Limitation to communicate to users**: `add_formula_tb`'s sub/superscript implementation uses `baseline` XML attribute. This is real PPT native formatting (the user can select the character and change its size/position in PowerPoint), BUT it's not a true mathematical equation — when a variable should have both a subscript AND superscript attached (like `n_u^{out}`), baseline offsets appear sequentially, not vertically aligned. For publication-grade math, recommend the user re-type critical formulas using PowerPoint's equation editor. For most schematic figures, baseline is good enough.

## Rule 4: Critical Decorative Lines Drawn Last

The short rule: red dashed vertical markers, horizontal braces — add these at the END of `build_module`, after all regions and content.

**Why**: python-pptx has no z-order API; it renders shapes in the order they were added. A line drawn early gets painted over by a filled region drawn later.

**Special case**: if a Module has NO filled regions, order doesn't matter. But most academic figures DO have filled regions (TTFT/TPOT, input/output blocks), so default to "decorative lines last".

## Rule 5: `[Type]` Placeholder Icons

The short rule: for UAV, satellite, phone, NN diagram, database, and other domain-specific icons, use `add_icon(slide, x, y, w, h, "[UAV]")`.

**Why**: python-pptx can draw rectangles, ovals, and a few geometric shapes, but NOT realistic domain icons. Attempting to build a UAV out of primitive shapes produces ugly results. Better to make the placeholder explicit so the user swaps it in PowerPoint with a real icon.

**Recommended replacement sources** (tell the user):
- **Cisco Network Topology Icons** — free, official, most complete for terrestrial network infrastructure (routers, servers, cell towers, end devices).
- **AWS / Azure / GCP Architecture Icons** — free, official, cloud-native components.
- **BioRender** — biology/medical (may require subscription).
- **Flaticon / Iconscout / The Noun Project** — generic for UAV, satellite, phone, etc.

Label convention: `[Type]` with square brackets. User can search-and-replace `[` in PowerPoint to find all placeholders.

## Rule 6: Shared Horizontal Coordinate Constants

The short rule: every Module file starts with the same set of x-coordinate constants.

**Why**: when `assemble.py` combines Modules into a multi-page pptx, or when the user stacks slides on top of each other in PowerPoint to reconstruct the full figure, corresponding regions should align vertically. If Module 2's TTFT region starts at `x=1.60` and Module 3's TTFT region starts at `x=1.75`, they look misaligned when stacked.

**Standard constants** (adapt to your figure's structure):
```python
DRAW_X       = 0.3       # Slide left margin
DRAW_RIGHT   = 13.00     # Slide right boundary (just before right edge)
CASE_X       = 0.3       # Case label column start
CASE_W       = 1.30      # Case label column width
TTFT_X       = 1.60      # Left-region (TTFT-equivalent) start
RED_LINE_X   = 6.75      # Center divider (red dashed reference)
TPOT_X       = 6.80      # Right-region (TPOT-equivalent) start
```

Copy this block into every `moduleN.py` file verbatim. Adjust values once at the top if needed, propagate to all files.

## Rule 7: No Wavy Lines in python-pptx

The short rule: draw a straight line where a wavy line should be, note it in the delivery summary.

**Why**: python-pptx connectors support `STRAIGHT`, `ELBOW`, and `CURVE` — but `CURVE` is a simple S-curve, not a wavy line (multiple oscillations). PowerPoint itself has a wavy line shape in its connector library, but python-pptx can't invoke it through the shape API.

**What to do**:
1. Draw a straight `add_arrow` (or `add_line`) in the color of the wavy-line semantic (e.g., blue for uplink, green for downlink).
2. In the delivery summary, tell the user: "Replace the straight G2A uplink line and A2G downlink line with PowerPoint's built-in wavy-line connector — Insert → Shapes → Lines → Scribble, or Insert → Shapes → Lines → Curved."
3. Do NOT leave `[wavy line]` text on the slide as a reminder. The user will see a straight line in the color, which is visually acceptable even if not ideal.

---

## Rule 8: Arrow Labels Between Adjacent Sub-Blocks — Center on Midpoint

The short rule: for a label on an arrow connecting two adjacent sub-blocks, compute the arrow midpoint and place a narrow text box centered on it, rather than anchoring the text box to the arrow's left edge.

**Why**: anchoring to the arrow's left edge means the text overflows to the right and slides into the next sub-block's fill (Pitfall 9). Centering on the midpoint distributes overflow symmetrically into whatever whitespace exists above or below the arrow, and makes the label visually read as "belonging to" the arrow, not to a block.

**Implementation**:
```python
# Two adjacent sub-blocks: block_A at x=2.0 w=1.2, block_B at x=3.3 w=1.2
block_A_right = 2.0 + 1.2   # 3.2
block_B_left  = 3.3
_mid_x = (block_A_right + block_B_left) / 2  # 3.25

# Text box centered on midpoint, width narrow enough to not overflow beyond the arrow
add_tb(slide, _mid_x - 0.25, y_label, 0.50, 0.25,
       "Build", fs=11, bold=True,
       color=C_NAVY, align=PP_ALIGN.CENTER)
```

Note the text-box width (0.50) should roughly equal the inter-block gap. If the label is wider than the gap, move it to the whitespace row above/below the sub-block row instead (see Pitfall 9, option b).

## Rule 9: Color-Gradient Tokens — Pass an Explicit List of `RGBColor`

The short rule: for a row of tokens where each one has a different shade (e.g., Decode steps fading from deep orange to pale orange), build a list of `RGBColor(r, g, b)` objects and pass it as the `colors` argument to `add_token_row` — don't try to interpolate programmatically.

**Why**: two reasons.
1. `add_token_row` supports per-token color via the `colors` param, but the skill's default color constants are a flat palette (`C_ORANGE`, `C_PALE_ORANGE`) with no intermediate shades. Gradient sequences need explicitly chosen intermediate values.
2. Visual gradients aren't linear in RGB space — perceptually, an evenly-spaced linear RGB interpolation looks uneven. Hand-picking 3-5 shades that look right to the eye beats any automatic interpolation scheme for schematic figures.

**Implementation** — Decode tokens fading from deep to pale orange:
```python
from pptx.dml.color import RGBColor

dec_colors = [
    RGBColor(0xC0, 0x5A, 0x10),  # deep orange, newest/most recent
    RGBColor(0xE0, 0x77, 0x16),
    RGBColor(0xF0, 0xA0, 0x50),
    RGBColor(0xFB, 0xD3, 0x8B),  # pale orange, oldest/least recent
]

add_token_row(slide, DEC_X, DEC_Y, n=4, w=0.35, h=0.35,
              colors=dec_colors, labels=["t+3", "t+2", "t+1", "t"])
```

For reverse gradients (pale → deep, as in Input/Prefill building up), reverse the list. Keep a small library of 3-5 shade sequences in the Module file's top constants block if multiple rows use the same gradient.

## When to Break a Rule

Rules 1-9 are defaults that work for 90%+ of academic figures. Break them when:

- User explicitly requests a different style ("I want boxed Case labels" → Rule 1 off).
- The original figure is unusual — e.g., it already uses solid borders (Rule 2 off) or card labels (Rule 1 off). In that case, mirror the original.
- Rule conflicts with Rule — e.g., Rule 4 (decorative lines last) conflicts with a figure where a decorative line passes BEHIND a semi-transparent region. Not common, but if it happens, reverse the order and experiment.

Document any rule deviation in the delivery summary so the user knows what's non-standard.
