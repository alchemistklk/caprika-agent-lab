# Verification — why the green check lies

Every rule here was learned from a real miss on Part 01, where the tooling
reported success and the deliverable was wrong.

## `check` does not check everything

`hyperframes check` runs lint, runtime, layout, motion, and contrast. It does
**not** verify:

- that an `<audio>` element exists at all — the project passed every gate while
  `index.html` had no audio, so `render` would have produced a silent video
- that a caption survives into the encoded MP4
- that an element is positioned where the design says

## A failing lint short-circuits the later passes

This is the most dangerous output in the toolchain:

```
Lint      ✗ 1 error
Layout    ◇ 0 issues across 0 sample(s)
Contrast  ◇ 0/0 text checks pass WCAG AA
```

`0 issues across 0 samples` and `0/0 pass` read as green. They mean **nothing
ran**. Always read the sample and check counts, not just the ✓/✗:

- layout sample count should be non-zero (9 for a six-scene project)
- contrast count should be non-zero and should *grow* when you add text

A contrast count that silently drops is a signal that text disappeared. When
Part 01's captions were added the count went 53 → 57; when a title accidentally
stayed at `opacity: 0` it sat 2 lower than expected.

## Evidence commands

```bash
# audio actually in the render
ffprobe -v error -show_entries stream=index,codec_type,codec_name,channels \
  -show_entries format=duration -of default renders/<file>.mp4

# captions actually burned in: pull a frame FROM THE MP4, not from snapshot
ffmpeg -v error -ss 63 -i renders/<file>.mp4 -frames:v 1 -y /tmp/probe.png
# then check ink in the caption band (see frame-geometry.md for the probe)

# what the composition thinks it has
npx hyperframes info .        # → "Elements N (M text, 1 audio)", "Tracks N"
```

`hyperframes info` reporting `1 audio` proves the element parsed. It does
**not** prove the file decodes or that the codec survives muxing — only a
render plus `ffprobe` does. A low-fps smoke render (`--fps 2`) is a cheap way
to exercise the full encode path when you only need to prove wiring.

## Trust the render log, but verify the artifact

The render log reports `hasAudio: true` and `artifact validated`. Both were
true on Part 01 — and were still worth confirming with `ffprobe`, because they
describe the pipeline's intent rather than the encoded result.

Two log traps:

- `static-frame dedup: disabled … this is the safe fallback, **not an error**`
  contains the word "error" and will trip a naive `grep -i error` watcher.
- The output file appears a moment after the "Render complete" line. An `ls`
  fired immediately can miss it; re-check before concluding the render failed.

## Human gates that no command replaces

- **Timing**: numeric alignment to a word-level transcript is necessary and not
  sufficient. Someone must watch with sound before timing is "approved".
- **Legibility at target size**: a 26px chip is fine on a desktop still and may
  not be on a phone. Check the vertical cut at phone scale.
