# frame-to-video

Turn designed static frames into a narrated, captioned HyperFrames video, in
one or more aspect ratios.

Distilled from producing *Agent Loop Part 01* (six frames, 133s, 16:9 + 9:16,
burned-in and sidecar captions). Every rule in `references/` corresponds to a
defect that shipped green and had to be found by hand.

## What it covers

- the **stage order** — which steps are cheap early and expensive late
  (aspect ratio, audio wiring, caption safe area)
- why design boards are the visual **authority** and not video material
- binding animation to a word-level transcript, and the human gate that no
  command replaces
- captions from **authored text + machine timing**, with the Chinese
  line-breaking rules
- cutting an aspect variant that shares audio, cues, and timeline
- **verification gates** — what to run instead of trusting a green check

## Layout

```
SKILL.md                          the pipeline and its ordering constraints
references/verification.md        why green checks lie; evidence commands
references/captions.md            script+ASR alignment; Chinese line breaking
references/frame-geometry.md      measure-don't-eyeball; computed geometry
references/image-generation.md    codex image_gen via cinematic-image-director
scripts/build-captions.py         the aligner; set ASR + script bounds per episode
```

## Related

- `gpt-image2-prompt/` — the house prompt system for design boards
- `cinematic-image-director` — owns the still-image workflow
- `hyperframes-core` / `hyperframes-cli` — the composition and render contract
