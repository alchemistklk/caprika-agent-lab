# Comparative Version Lock — 2026-08-07

## Policy

For this comparison, **latest** means the newest non-prerelease version on the
project's immediate release channel as observed on 2026-08-07 in Asia/Shanghai.
Snapshot, beta, alpha, `next`, and development builds are recorded only when a
local product embeds one; they do not replace the source baseline.

**Claude Code exception:** its comparison baseline is the actual local runtime,
not a moving remote latest target. The locked local runtime is `2.1.224`.

A version lock has three separate fields:

1. **Source baseline:** the exact public tag and commit used for implementation
   study.
2. **Published package/product:** the latest version users can install from the
   project's primary release channel.
3. **Local runtime:** the version actually observed on this machine.

These fields must not be silently treated as identical.

## Locked Versions

| System | Latest baseline | Source revision | Local runtime | Match status |
|---|---|---|---|---|
| Codex | `0.147.0` | [`rust-v0.147.0`](https://github.com/openai/codex/tree/rust-v0.147.0) at [`be6e8ea`](https://github.com/openai/codex/commit/be6e8eac029b183056b7e4402879f15d2c85f61b) | Terminal `0.145.0`; desktop bundle `0.147.0-alpha.6.5` | Neither local executable exactly matches |
| Claude Code | Local native arm64 runtime `2.1.224` | Local static snapshot fingerprint `ae54cc83a5ad76d8007e1933fa7128353c0f8f5842c2b4ed79fae23ce516e713`; product-version mapping unknown | Native arm64 `2.1.224` | Runtime is locked directly; snapshot remains a separately labeled implementation artifact |
| OpenCode | `1.18.14` | [`v1.18.14`](https://github.com/anomalyco/opencode/tree/v1.18.14) at [`65cf14d`](https://github.com/anomalyco/opencode/commit/65cf14df16c191f3e9684f0d9a8bae69103ced6d) | No `opencode` executable on PATH; local fork package reports `1.18.1` | Local source does not match and has diverged from upstream |
| Pi | `0.84.1` | [`v0.84.1`](https://github.com/earendil-works/pi/tree/v0.84.1) at [`53fa77c`](https://github.com/earendil-works/pi/commit/53fa77ccd8a279eb87e92294ef3687b03ff80112) | No `pi` executable on PATH | Clean source checkout matches the locked tag; no local runtime is installed |

## System Notes

### Codex

The official OpenAI changelog published Codex CLI `0.147.0` on 2026-08-07.
The desktop bundle observed earlier contains an alpha build from the same
development line, but an alpha build is not evidence-equivalent to the final
`0.147.0` tag. Cross-system source comparison uses commit `be6e8ea`.

### Claude Code

Claude Code explicitly distinguishes two update channels:

- `latest`, the default channel, receives releases immediately;
- `stable` is typically delayed and skips releases with major regressions.

The installed native binary is `2.1.224`; this observed local version is the
comparison baseline even after the remote `latest` channel advances. At the
time of locking, it also matches the current `latest` package tag; the stable
channel is `2.1.220`.

The locally held static source-map snapshot has no Git history or verified
product-version mapping. It may support bounded implementation study, but it
must not be described as the source of Claude Code `2.1.224`. Runtime findings
and snapshot findings remain separate evidence lanes.

### OpenCode

The upstream GitHub release and `opencode-ai` package both identify `1.18.14`
as latest. The existing local checkout reports package version `1.18.1` on a
custom branch. GitHub comparison shows that the local head and upstream
`v1.18.14` have diverged. Use a separate clean checkout of the tag; do not
repurpose or reset the existing working repository.

### Pi

The current project and package have moved from the older
`badlogic/pi-mono` / `@mariozechner/pi-coding-agent` identity to:

- repository: [`earendil-works/pi`](https://github.com/earendil-works/pi);
- package: `@earendil-works/pi-coding-agent`;
- latest version: `0.84.1`.

The older npm package remains at `0.73.1` and is not the latest comparison
target.

## Evidence Sources

- [Official OpenAI Codex changelog](https://learn.chatgpt.com/docs/changelog)
- [Official Claude Code installation and update channels](https://code.claude.com/docs/en/installation)
- [OpenCode `v1.18.14` release](https://github.com/anomalyco/opencode/releases/tag/v1.18.14)
- [Pi `v0.84.1` release](https://github.com/earendil-works/pi/releases/tag/v0.84.1)
- npm registry metadata for `@anthropic-ai/claude-code`, `opencode-ai`,
  `@earendil-works/pi-coding-agent`, and the legacy
  `@mariozechner/pi-coding-agent`, queried on 2026-08-07.

## Checkout and Index Status

The three public-source baselines were checked out separately and verified on
2026-08-07. Each checkout is detached at the exact commit recorded above, has
a clean working tree, and has a full local code-graph index. The existing
divergent OpenCode repository was not modified.

The Claude Code runtime remains locked independently at `2.1.224`. Its local
static snapshot is indexed only as a version-unverified evidence lane and must
not be treated as source matched to that runtime.

## Next Actions

1. Build a bounded source map for one complete agent turn in each public
   source baseline.
2. Trace the smallest no-tool turn before following a tool-call continuation.
3. Keep the Claude runtime and local snapshot evidence lanes separate
   throughout the trace.
