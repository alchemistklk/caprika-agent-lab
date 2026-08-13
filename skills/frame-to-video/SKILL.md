---
name: frame-to-video
description: Turn designed static frames into a narrated, captioned HyperFrames video in one or more aspect ratios. Use when producing an episode from image-generated design boards, wiring narration, binding animation to a word-level transcript, building captions, or cutting a vertical variant. Covers the ordering constraints that make the pipeline cheap and the verification gates that make "done" mean done.
---

# Frame To Video

Produce an episode: designed boards → animatable frames → narrated, captioned
video → per-platform aspect variants.

The pipeline's value is its **order**. Several stages are cheap if done early
and expensive if done late, and the failure mode is silent — the tooling stays
green while the deliverable is wrong.

## Stage order (the order is the point)

| # | Stage | Must happen before |
|---|---|---|
| 1 | Brief: destination, aspect ratio(s), language | anything is laid out |
| 2 | Narration audio generated **and wired into the composition** | any animation timing |
| 3 | Static design boards (raster) | frame rebuild |
| 4 | Frame rebuild as HTML/SVG | animation |
| 5 | Animation bound to the word-level transcript | captions |
| 6 | Captions | render |
| 7 | Aspect variants | publish |

### 1. Aspect ratio is a stage-1 decision

Decide 16:9 / 9:16 / both **before layout**. Retrofitting vertical is a
re-layout, not a resize: diagram-heavy frames are wider than 1080 at their core
and every absolute position, connector, and tween axis has to be redone.

Reserve the **caption safe area now**: keep all frame content above
`height − 120px − (caption lines × line-height)`. Measure it, don't eyeball —
see `references/frame-geometry.md`.

### 2. Wire the audio before you time anything

The audio track is **narration only** — these episodes ship without background
music. The audio stage is complete once narration is wired and verified.


Add the `<audio>` element to the root composition as soon as narration exists.
`check` does **not** verify that audio is present — a fully green project can
render silent. See `references/verification.md`.

Wiring it early also means every later timing decision can be reviewed with
sound, instead of being numerically aligned and only heard at the end.

### 3. Design boards are the authority, not the asset

Generate boards with the codex `image_gen` provider (see
`references/image-generation.md`). They are the **visual authority** used to
catch implementation drift — not video material.

Do not animate the rasters. Frames must be rebuilt as HTML/SVG because the
video needs per-element entrance timing, crisp text at any scale, and a layout
layer that can be swapped for a second aspect ratio while the timeline stays
untouched.

### 4. Rebuild frames, then diff against the board

After building each frame, compare it element-by-element with its board. Drift
is normal and invisible until you look: a card's folder tab collapsed into a
floating bracket, a dashed cycle flattened into a container rectangle whose
edges bisected every icon, a browser-window glyph reduced to three bare
rectangles. All shipped green.

### 5. Bind animation to the transcript, not to taste

Extract word-level timings and place every tween on the word that licenses it.
Record the mapping in a comment next to the tween so a later reader can check
it without re-deriving.

Then **watch it with sound**. Numeric alignment is necessary and not
sufficient; only a human listen closes this stage.

### 6. Captions: authored text, machine timing

Never generate captions from the ASR transcript alone — it mishears. Take text
from the approved script, timing from the word-level transcript, and align them
character by character. Chinese line breaking has hard rules.
See `references/captions.md`.

### 7. Aspect variants share everything except layout

A second aspect ratio is a sibling project with `assets/`, `audio/`,
`captions/`, and `output/` **symlinked** to the master — the narration is tens
of MB and the cue timings must not fork.

Copy the timeline positions verbatim. If a tween time changes between cuts, the
approved timing review no longer covers the variant.

## Verification gates

Every claim needs physical evidence, not a return code:

| Claim | Evidence |
|---|---|
| audio is in the render | `ffprobe` shows an `aac` stream |
| captions are burned in | extract a frame from the **MP4**, check pixels in the caption band |
| layout has no collisions | measure gaps between elements on the rendered still |
| frames match the design | side-by-side with the board |
| timing is right | a human listened |

`references/verification.md` has the commands and the traps.

## References

| File | Use |
|---|---|
| `references/verification.md` | why green checks lie, and what to run instead |
| `references/captions.md` | script+ASR alignment, Chinese line-breaking rules |
| `references/frame-geometry.md` | measure-don't-eyeball, compute geometry, layout coupling |
| `references/image-generation.md` | codex `image_gen` provider and its gotchas |
| `scripts/build-captions.py` | the aligner; parameterize per episode |
