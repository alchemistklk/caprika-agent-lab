# Codex Implementation Study

## Scope Lock

- **System:** OpenAI Codex
- **Category:** coding-agent product and harness
- **Current comparison source baseline:** `codex-cli 0.147.0`
- **Current comparison source tag:** `rust-v0.147.0`
- **Current comparison source commit:** `be6e8eac029b183056b7e4402879f15d2c85f61b`
- **Primary runtime target:** the Codex desktop app bundle installed on macOS
- **Primary embedded CLI version:** `codex-cli 0.147.0-alpha.6.5`
- **Observed desktop source tag:** `rust-v0.147.0-alpha.6.5`
- **Observed desktop source commit:** `618b8e9111da9f57fe380b09d0f6516e3f343536`
- **Comparison runtime:** the independently installed terminal CLI
- **Comparison CLI version:** `codex-cli 0.145.0`
- **Comparison source tag:** `rust-v0.145.0`
- **Comparison source commit:** `25af12f7e61572b0bc18ddb1008be543b91519b0`
- **Access date:** 2026-08-07

### Included surfaces

- the public `openai/codex` repository at the locked revisions;
- the npm launcher and platform-specific native executable;
- the desktop-bundled native Codex executable;
- public Codex CLI, app-server, MCP, sandbox, approval, configuration, and
  extension contracts when relevant to the traced path;
- sanitized local observations and bounded verification experiments.

### Excluded surfaces

- credentials, authentication tokens, private prompts, and session contents;
- personal configuration values that are not required to explain a public
  implementation contract;
- reverse engineering or decompilation of proprietary desktop UI code;
- unsupported claims about OpenAI production services or cloud internals;
- model-quality evaluation before the runtime path is understood.

### Known source limits

The public repository is the source authority for the native Codex code at the
locked tags. The desktop product includes additional application and service
surfaces. We must not assume that every desktop or cloud behavior is
implemented in the public repository. Phase 1 will classify each observed
surface as public source, documented contract, local observation, inference,
or unknown.

## Current Phase

- **Phase:** 0 — Lock the target
- **Status:** `verified`
- **Next question:** Which processes, crates, binaries, protocols, and state
  stores form the smallest complete agent execution surface at the current
  `rust-v0.147.0` source baseline?

## Phase 0 Findings

### 1. There are two relevant local Codex executables

The shell command resolves to an npm-managed JavaScript launcher under the
active NVM installation. It reports `codex-cli 0.145.0`.

The desktop app bundle contains a separate native `arm64` executable under
`Contents/Resources/codex`. It reports `codex-cli 0.147.0-alpha.6.5`.

The desktop app reports:

- bundle identifier: `com.openai.codex`;
- short version: `26.803.41515`;
- build version: `6321`.

This means a terminal experiment and a desktop-thread observation may exercise
different Codex revisions. Every later trace must name which executable it
uses.

### 2. The npm command is a launcher, not the agent implementation

The installed `@openai/codex` package contains a small JavaScript entry point.
On this machine it:

1. detects `darwin` and `arm64`;
2. resolves the `@openai/codex-darwin-arm64` platform package;
3. locates the native `aarch64-apple-darwin` Codex binary;
4. spawns that binary with inherited standard I/O and arguments;
5. forwards `SIGINT`, `SIGTERM`, and `SIGHUP`;
6. mirrors the native process exit status.

The primary implementation study must therefore begin in the Rust/native
source, not in the npm wrapper.

### 3. Both installed versions map to exact public source revisions

The installed npm metadata identifies
[`openai/codex`](https://github.com/openai/codex) as its repository and uses the
Apache-2.0 license.

- [`rust-v0.145.0`](https://github.com/openai/codex/tree/rust-v0.145.0)
  resolves to commit
  [`25af12f`](https://github.com/openai/codex/commit/25af12f7e61572b0bc18ddb1008be543b91519b0).
- [`rust-v0.147.0-alpha.6.5`](https://github.com/openai/codex/tree/rust-v0.147.0-alpha.6.5)
  resolves to commit
  [`618b8e9`](https://github.com/openai/codex/commit/618b8e9111da9f57fe380b09d0f6516e3f343536).

The second revision is the source match for the observed desktop runtime. The
current cross-system source baseline is the later stable `rust-v0.147.0`
release recorded at the top of this file.

## Evidence Inventory

| Claim | Label | Evidence pointer | Confidence |
|---|---|---|---|
| Codex CLI operates on local repositories and exposes permissions and non-interactive execution | `DOC` | [Official Codex CLI documentation](https://learn.chatgpt.com/docs/codex/cli) | High |
| The shell CLI is version `0.145.0` | `OBSERVATION` | `with-env codex --version` on 2026-08-07 | High |
| The npm package points to `openai/codex` and uses a platform-native optional dependency | `SOURCE` | Installed `@openai/codex` `package.json` | High |
| The JavaScript entry point selects and spawns a native target binary | `SOURCE` | Installed `@openai/codex/bin/codex.js` | High |
| The machine and selected platform binary are Apple Silicon `arm64` | `OBSERVATION` | `uname -m` and `file` on the installed binary | High |
| The desktop app embeds Codex CLI `0.147.0-alpha.6.5` | `OBSERVATION` | Bundled executable `--version` on 2026-08-07 | High |
| The two versions resolve to the recorded commits | `SOURCE` | GitHub tag and annotated-tag objects in `openai/codex` | High |
| The complete desktop implementation is represented by the public repository | `UNKNOWN` | Phase 1 must map this boundary | Unknown |

## Version Discipline

For every later claim, use one of these prefixes:

- **Desktop 0.147 alpha:** behavior or source tied to the desktop-bundled
  `0.147.0-alpha.6.5` executable and commit `618b8e9`.
- **CLI 0.145 stable:** behavior or source tied to the independently installed
  `0.145.0` executable and commit `25af12f`.
- **Current docs:** a public contract from official OpenAI documentation,
  accessed on the recorded date.

Do not transfer a finding between these baselines without checking the diff or
repeating the observation.

## Phase 0 Exit Check

- [x] Exact product and category recorded.
- [x] Local executables distinguished.
- [x] Versions recorded without exposing credentials or session data.
- [x] Public repository and exact revisions resolved.
- [x] Included and excluded evidence surfaces stated.
- [x] Source limitations made explicit.
- [x] Next implementation question defined.

The original local-runtime lock is complete. The comparative source baseline
was refreshed on 2026-08-07 to stable release commit
`be6e8eac029b183056b7e4402879f15d2c85f61b`. Phase 1 will build its source and
process surface map at that revision while retaining the earlier desktop alpha
as a separately labeled runtime observation.
