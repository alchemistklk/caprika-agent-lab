# Captions — authored text, machine timing

## Never generate captions from ASR text

The ASR transcript mishears. On Part 01, diffing it against the approved script
found two errors that would have been burned into the deliverable:

| script (correct) | ASR heard |
|---|---|
| 也可以**截**一张图 | 也可以**结**一张图 |
| 叫**作**推理与行动模式 | 叫**做**推理与行动模式 |

**Text comes from the approved script; timing comes from the word-level ASR.**
Align them character by character with `difflib.SequenceMatcher` over
punctuation-stripped strings, then map each script character back to its ASR
timestamp. Interpolate any unmatched character between its neighbours.

`scripts/build-captions.py` implements this. It prints every script↔ASR
difference so the mishearings are visible rather than silently overwritten.

Watch the extractor: a script's metadata block may wrap onto a continuation
line (e.g. `**On-screen identifiers:**` continuing onto a line that starts with
a backtick). On Part 01 that leaked `Reason/Act/Observe/Agent Loop` into the
narration body and produced a bogus cue.

## Chinese line breaking — hard rules

Chinese has no word spaces, so a naive character-count cut splits words.

1. **Break only at punctuation** (`。？！，、；：`). Merge clauses greedily up to
   ~26 characters / 6 seconds, forcing a cue boundary after sentence-final
   punctuation.
2. **A long clause wraps inside one cue, never into two.** Add a second line
   only when a punctuation break exists in the middle 30–70% of the line.
3. **If there is no usable punctuation, leave the line long.** A midpoint split
   cuts a word in half (模|型), which is worse than one wide line.
4. **Exclude the final character from wrap candidates** — breaking at the
   trailing `。` emits an empty second line.

Each rule above corresponds to a bug that shipped and had to be fixed: `更聪|明
的搜索框`, then a blank second line, then `模|型`.

## Quality gate

Assert before accepting a cue set:

- 0 overlapping cues
- 0 empty lines
- 0 cues above ~9 characters/second
- the last cue ends inside the composition duration
- the known-corrected strings are present (e.g. `截一张图`, not `结一张图`)

## Burned-in vs sidecar

Both come from the same cue list, so build the cues once and emit `.srt`,
`.vtt`, and `.cues.json` together.

- **Sidecar** is free and reversible — always produce it.
- **Burned-in** needs a caption safe area reserved at layout time, and forces a
  re-render on every text change.

For burned-in, force **single-line cues** so the band is one row rather than
two — it roughly halves the vertical space you must reserve.

## Aspect variants

Generate a per-aspect cue variant that keeps `CUE_CHARS` (so cue boundaries and
timing are identical) and only changes `LINE_CHARS` (so line breaks suit the
narrower canvas). Assert that timing and punctuation-stripped text are
**identical** across variants — a drift here silently desynchronises one cut.
