# Pitfalls Reference

Read this file when a visual defect appears that you don't immediately understand, or before attempting something that might hit a known trap.

These traps all emerged from real reworks during development of this skill.

## 1. `LEFT_BRACE` Rotation Produces an Out-of-Control Giant Red Line

**Symptom**: Using `MSO_SHAPE.LEFT_BRACE` + `shape.rotation = 270` (or 90) to draw a horizontal brace produces a huge red line spanning half the slide and occluding other elements.

**Root cause**: python-pptx rotates shapes around their center, but the visible rendered area after rotation doesn't match the bounding box defined by `x/y/w/h`. The rotated shape extends unpredictably.

**Correct approach**: Use `add_hbrace(slide, x1, x2, y, color, width, tip_depth)` from helpers — it constructs the brace from 4 straight lines (main horizontal + two upturned ends + one downward tip). Fully predictable positioning.

## 2. Red Dashed Line Occluded by Region Fill

**Symptom**: A red dashed vertical reference line is visible outside the regions but disappears inside them, as if the line is broken.

**Root cause**: python-pptx draws shapes in insertion order. If `add_line()` for the red dashed line is called BEFORE `add_shape()` for the filled region, the region's fill is painted on top.

**Correct approach**: Draw all regions first. Call `add_line()` for critical decorative lines (red dashed markers, horizontal braces) as the LAST operations before saving.

```python
# Wrong
add_line(slide, x, 0, x, 5, color=C_RED, dash=True)  # covered later
add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, ...)   # fills over it

# Right
add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, ...)   # region first
# ... all other content ...
add_line(slide, x, 0, x, 5, color=C_RED, dash=True)  # last, on top
```

## 3. Unicode Subscript Characters Mixed with Baseline Offset

**Symptom**: Formula like `ηᵤ ∈ [ηₘᵢₙ, 1]` shows `ₘᵢₙ` scrunched together with odd spacing.

**Root cause**: Unicode already has precomposed subscript characters (`ₘ` U+2098, `ᵢ` U+1D62, `ₙ` U+2099). If you also apply `baseline=-25000` to a run containing these, the characters get re-shrunk AND offset, breaking glyph spacing.

**Correct approach**: Pick one approach consistently per formula:
- Use Unicode subscripts in plain runs (no baseline), OR
- Use plain ASCII letters with baseline-offset runs

Don't mix. Example:
```python
# OK — Unicode only, no baseline
add_formula_tb(slide, ..., [("ηᵤ ∈ [ηₘᵢₙ, 1]", 'n')])

# OK — plain ASCII with baseline
add_formula_tb(slide, ..., [
    ("η", 'n'), ("u", 'sub'),
    (" ∈ [η", 'n'), ("min", 'sub'),
    (", 1]", 'n'),
])
```

## 4. LaTeX Source Text Placed Directly as `text`

**Symptom**: The figure literally shows `T^{G2A}_{u→k}` with visible braces and underscores.

**Root cause**: `add_tb(slide, ..., text="T^{G2A}_{u→k}")` displays the string verbatim. python-pptx doesn't parse LaTeX.

**Correct approach**: Always use `add_formula_tb()` with the parts list for anything involving sub/superscripts:
```python
add_formula_tb(slide, ..., [
    ("T", 'n'), ("G2A", 'sup'), ("u→k", 'sub'),
])
```

## 5. Debug Placeholder Text Leaks to Final Output

**Symptom**: The final figure contains strings like `[wavy line]`, `[TODO]`, `xxx` that were never meant to be visible.

**Root cause**: Debug annotations added during development weren't removed before delivery.

**Correct approach**: During self-review (Stage 4), scan the generated JPG for these patterns. When you draw a straight line as a placeholder for a wavy line, DON'T leave a `[wavy line]` label on the slide — instead, note it in the delivery summary for the user to address in PPT.

## 6. Over-Split Subscript Runs

**Symptom**: `s₀ → sᵤ` built as four runs — `("s", 'sub'), ("0", 'sub'), ("→s", 'sub'), ("u", 'sub')` — renders with oddly wide character spacing, looking like `s 0 → s u`.

**Root cause**: Each run is an independent text flow; multiple consecutive sub-runs introduce unintended kerning gaps between them.

**Correct approach**: Merge consecutive subscript content into a single run:
```python
# Wrong
[("T", 'n'), ("A2S", 'sup'),
 ("k→s", 'sub'), ("0", 'sub')]

# Right
[("T", 'n'), ("A2S", 'sup'), ("k→s0", 'sub')]
```

Sacrifices strict mathematical nesting (the `0` isn't a nested subscript of `s`) for visual continuity. Acceptable trade-off for schematic figures.

## 7. Forcing Every Module to Fill 16:9

**Symptom**: A Module that should be a horizontal band in the original (like a TTFT/TPOT timeline) ends up looking square in the output, with elements spread too thin and the aspect ratio visibly wrong.

**Root cause**: Default assumption that each Module occupies the full slide.

**Correct approach**: At Stage 3 (proportion estimate), decide what band height a Module should occupy based on its ratio in the original figure. A horizontal band like `(12.7 × 3.0)` lives in the middle of a `(13.333 × 7.5)` slide with whitespace above and below, preserving the horizontal-band feel from the original. When assembled, those bands stack naturally like the original layout.

## 8. Subscripts in Explanatory Prose, Not Just Formulas

**Symptom**: A caption like `Process all ñ_u^in tokens in parallel` renders literally as `ñ_u^in` in the slide, even though nothing about the sentence "looks like" a formula.

**Root cause**: It's easy to read Rule 3 as "use `add_formula_tb` for *formulas*" and then hand explanatory prose to `add_tb` because it reads as a sentence. But any variable token with sub/superscripts (ñ_u^in, n_u^txt, L_{u,i}, etc.) hits the same LaTeX-literal failure as a standalone formula — it doesn't care whether the surrounding context is math or a sentence.

**Correct approach**: Treat any sub/superscript-bearing token as triggering the formula path, regardless of surrounding context. If a sentence contains even one such token, build the whole line with `add_formula_tb` and plain-style ('n') runs for the prose parts:

```python
# Wrong — token disappears into literal text
add_tb(slide, x, y, w, h, "Process all ñ_u^in tokens in parallel", ...)

# Right — plain runs surround the formula token
add_formula_tb(slide, x, y, w, h, [
    ("Process all ñ", 'n'), ("u", 'sub'), ("in", 'sup'),
    (" tokens in parallel", 'n'),
], ...)
```

Applies to captions, sub-titles, step annotations, legend text — anywhere a math variable could sneak into prose.

## 9. Arrow Labels Between Densely-Packed Sub-Blocks Get Occluded

**Symptom**: A label like "Build" or "Read" placed above a short arrow connecting two adjacent sub-blocks is clipped on one side by the next sub-block's fill, so only half the word is visible.

**Root cause**: When the inter-block gap is small (say 0.05 inch) and the label text ("Build" ≈ 0.35 inch wide at fs=12) is wider than the gap, the text box overflows into the adjacent sub-block's region. Sub-block fills are drawn in insertion order and may be painted after the label, occluding it.

**Correct approach**: Two options, pick by situation.
- **Keep label on the arrow**: ensure inter-block gap ≥ `label_width + 0.2` inch. For a 5-character label at fs=12, that's roughly 0.55 inch minimum gap.
- **Move label off the arrow**: place the label in the whitespace above the sub-block row (not in the narrow gap between blocks). Center it on the arrow midpoint with `_mid_x = (block_A_right + block_B_left) / 2; add_tb(slide, _mid_x - 0.25, y_above_row, 0.50, 0.25, ...)`. This is the safer default when blocks must stay close.

Design rule 8 in `design_rules.md` expands on the midpoint-centering calculation.

## 10. `MSO_SHAPE.RIGHT_TRIANGLE` Rotation Won't Build a Funnel

**Symptom**: Attempting to draw a "funnel" (two triangles meeting at a narrow waist) by placing one `RIGHT_TRIANGLE` and another with `rotation=180` produces two triangles that are misaligned — the hypotenuses don't meet cleanly, and the apex vertices are offset from each other.

**Root cause**: `RIGHT_TRIANGLE`'s shape geometry isn't symmetric around its center, so a 180° rotation doesn't produce a mirror image at the same bounding-box position. The rotated triangle's visible apex lands somewhere other than where the first triangle's apex sits.

**Correct approach**: Don't try to compose a funnel from two `RIGHT_TRIANGLE` shapes. Alternatives:
- `MSO_SHAPE.CHEVRON` for a compressor/funnel-like left-pointing arrow — single shape, predictable geometry.
- `MSO_SHAPE.PENTAGON` rotated 90° for a similar effect.
- Leave a `[funnel]` icon placeholder (via `add_icon`) and let the user paste a real SVG funnel in PowerPoint. This is often the cleanest path for complex domain icons.

## 11. Narrow Partitions Can't Hold Their Own Wide Labels

**Symptom**: A partition ~1.2 inch wide contains a phone icon (0.85-1.00 inch) and a text label like "A2G downlink" (~1.1 inch at fs=11). The label either overflows into the next partition or gets shrunk into unreadable tiny font.

**Root cause**: Partition width was estimated at Stage 3 from the original figure's proportions, but the check didn't consider whether each partition's *widest internal element* (icon + label text) fits. Text label widths aren't obvious from the original thumbnail.

**Correct approach**: At Stage 3 (proportion estimate), run a narrow-partition check:
1. For each partition narrower than ~1.5 inch, list its planned internal elements.
2. If any element is wider than the partition (icon width *or* label text width), decide: (a) relocate the label to the upstream partition's whitespace where the arrow enters this partition, not inside the narrow partition itself; or (b) widen the partition by stealing width from a neighboring wider partition.
3. Option (a) is usually better because it preserves the original figure's partition proportions and the label reads as "crossing into" the partition, which matches the semantic of a transport link.

This is a Stage 3 check item, not a Stage 4 fix — catching it earlier avoids rebuilding the whole partition layout.

---

## General Debugging Checklist

If generating a Module produces something unexpected:

1. Check z-order: did you draw something important BEFORE a filled region?
2. Check formula rendering: did you accidentally pass LaTeX source as plain text?
3. Check coordinate system: are your `x/y/w/h` values in inches (not EMUs)?
4. Check `dash=True` vs `no_line=True` — they're different.
5. Check `fill=None` (no fill = transparent) vs `fill=C_WHITE` (explicit white).
