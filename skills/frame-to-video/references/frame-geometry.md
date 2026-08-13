# Frame geometry — measure, compute, re-measure

## "Looks wrong" must become "is off by N pixels"

Acting on the symptom fixes the wrong thing. Part 01 examples:

- **"The arrows curve inconsistently."** The arcs were fine as drawn; the four
  node centres were **never on one ellipse** (one frame's left/right nodes sat
  30px above the centre implied by top/bottom). Fixing the arcs would not have
  helped — the nodes had to move first.
- **A merge bracket that never merged.** Its two branches ended 77px apart in
  its own viewBox, with the arrow floating as a third disconnected stroke.
  Invisible at a glance; obvious in the path data.
- **"The caption area is occupied."** A per-frame pixel probe showed the real
  numbers (907 / 989 / 1007 / 882 / 975 / 987), so the fix was a 20–40px lift,
  not the redesign it looked like.

## The pixel probe

The board is `#101112`, so anything brighter than L≈45 is content:

```python
from PIL import Image
im = Image.open(png).convert('L'); w, h = im.size; px = im.load()
low = max(y for y in range(h) if max(px[x, y] for x in range(0, w, 3)) > 45)
print(f"lowest content y = {low}, bottom margin = {h - low}")
```

Use the same idea to measure a gap (scan for runs of empty rows between two
bands) or to confirm ink exists inside a region — that is how you verify a
caption is really in the encoded MP4.

## Compute geometry, don't hand-tune it

Anything with a mathematical definition should be generated:

- **Arcs on a shared ellipse**: place nodes at exact parametric points, then
  emit SVG `A` segments with endpoints solved numerically for equal clearance.
  Curvature is then identical *by construction* rather than by eye.
- **Arrowheads**: compute the barbs from the curve's end tangent (`P3 − P2` for
  a cubic) at ±27°, ~25 units.
- **Gear teeth**: generate the cog outline from radii and tooth count.

Hand-tuned Béziers drift, and the drift is invisible until someone asks why it
looks off.

## SVG markers vs drawn arrowheads

`marker-end` has two traps:

1. `markerUnits` defaults to `strokeWidth`, so a 12×12 marker on a 4.2px stroke
   renders ~50px — oversized and coarse.
2. **Markers ignore `stroke-dasharray`.** During a draw-on reveal the arrowhead
   is visible at the destination from frame one, floating ahead of the line.

Drawing the arrowhead as geometry appended to the path fixes both — but note
Part 01's owner preferred the marker look after seeing both, so treat this as a
trade-off to surface, not a rule to apply silently.

## Dash-based reveals need `pathLength`

`stroke-dasharray: 1200` against a ~200-unit path means the draw completes in
the first ~20% of the tween and then sits idle. Set `pathLength="1"` and use
`stroke-dasharray: 1; stroke-dashoffset: 1 → 0` so the reveal spans the whole
tween and ends exactly on the arrowhead.

## Layout is coupled — re-measure after every move

Every positional change in Part 01 created a new collision somewhere else:

- Aligning loop nodes onto a true ellipse pushed a node label into the path of
  its incoming arrow.
- Reserving the caption band lifted a verdict box onto a scale icon.
- Giving cogs a board-coloured `fill` (so the dashed orbit would pass *behind*
  them, instead of showing through their hollow interiors) then occluded most
  of the orbit, which had to be enlarged.

After any move, re-run the probe and confirm the gaps. Do not assume a local
change is local.

## Cross-frame consistency

Values that repeat across frames drift. Audit them explicitly:

- header origin (`top` / `left` / `gap`) — a 22px difference is clearly visible
  across a crossfade
- the closing-line baseline
- semantic colour usage in secondary elements (a summary strip should inherit
  the diagram's colours)
- storyboard `poster` timestamps — recompute as `max(tween position + duration)`
  per frame whenever timing changes, and place the poster ~0.5s after the frame
  settles
