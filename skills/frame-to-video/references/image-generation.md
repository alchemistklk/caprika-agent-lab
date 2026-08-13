# Design boards — codex `image_gen`

## Which skill owns this

**`cinematic-image-director`.** It owns the complete still-image workflow —
director-level prompt planning, generation and editing through Codex's built-in
`image_gen` tool, continuity protection, and visual QA (grain, speckling,
mottling, oversharpening).

It does **not** route through `media-use`. `media-use` is the media OS for a
HyperFrames project (BGM, SFX, voice, transcription, captions, reframing); still
images for design boards go through `cinematic-image-director`.

Do not use or install the local mflux / FLUX-on-MLX path.

## Why codex needs no key

Auth lives in the codex CLI on the user's ChatGPT subscription. There is no API
key here and no per-call charge — an empty `OPENAI_API_KEY` is expected and
irrelevant.

Preflight:

```bash
codex features list | grep image_generation     # must be: stable  true
test -f ~/.codex/auth.json && echo authed
ls -l "$(command -v codex)"                     # must be a real binary/symlink
```

Output lands in `~/.codex/generated_images/<id>/`.

## Verified invocation from Claude Code

Confirmed working 2026-08-13. Run from the target asset directory and pipe the
prompt in:

```bash
cat prompt.md | codex exec --skip-git-repo-check --sandbox danger-full-access -
```

Instruct codex, inside the prompt, to call `image_gen` **once** and copy the
result to an exact path.

- `--skip-git-repo-check` is required whenever the asset directory is not a git
  repo.
- A writable sandbox is required or codex cannot place the file.

`media-use`'s `scripts/lib/codex-provider.mjs`
(`codex exec --enable image_generation`) remains the path for video-adjacent
asset resolution — not for still design boards.

## Three gotchas

1. **`codex` must be a real binary on `PATH`.** A shell alias is not enough —
   spawned processes cannot see aliases. Symlink the real binary if needed:
   `ln -s "$(readlink -f "$(command -v codex)")" ~/.local/bin/codex`
2. **Check auth by file, not by `codex login status`.** That command writes to
   stderr/TTY and exits 0, so piped stdout reads empty and a naive gate reports
   "not logged in" and blocks generation.
3. **Allow a long timeout (~600s).** First-run tool spin-up is slow.

## House prompt system

This repo already has one — reuse it rather than writing prompts from scratch:

```
gpt-image2-prompt/
  style-system.md            shared visual constraints and style variables
  general-poster.md          milestone / launch / proof-of-work posters
  general-profile-header.md  profile headers
  product-visual.md          product concepts and workflow artifacts
```

Each entry separates `Purpose` / `Variables` / `Composition`, so project
specifics stay replaceable. For episode design boards, add an entry in the same
shape rather than inlining one-off prompts.

## What the boards are for

Boards are the **visual authority for the rebuild and the drift check** — not
video material. Keep them under `visual-reference/` next to the composition and
diff each built frame against its board. On Part 01 that diff is what caught a
folder tab rendered as a floating bracket, a dashed cycle flattened into a
container whose edges bisected four icons, and a browser-window glyph reduced
to three bare rectangles — none of which any automated check flagged.
