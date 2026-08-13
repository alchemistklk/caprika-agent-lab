# Agent Turn — Initial Source Navigation

## Shared Question

How does one user request enter the runtime, reach a model, consume the model
response, optionally execute tools, and reach a stop or continuation state?

This document is a Phase 1 navigation map, not yet an end-to-end execution
trace. A listed symbol is a verified source location, but its role in the full
path remains provisional until callers, callees, and state transitions are
traced.

## Public-Source Navigation

| System | Locked revision | Initial coordinator | Adjacent source surfaces | Evidence status |
|---|---|---|---|---|
| Codex | `rust-v0.147.0` / `be6e8ea` | `codex-rs/core/src/session/turn.rs::run_turn` | `run_sampling_request`, `try_run_sampling_request`, `build_prompt`, tool router and parallel tool runtime | `SOURCE`, path located; complete turn not yet traced |
| OpenCode | `v1.18.14` / `65cf14d` | `packages/opencode/src/session/prompt.ts` | `session/processor.ts`, `session/llm.ts`, `session/tools.ts` | `SOURCE`, collaborating modules located; loop ownership not yet proven |
| Pi | `v0.84.1` / `53fa77c` | `packages/agent/src/agent-loop.ts::agentLoop` and `runLoop` | `streamAssistantResponse`, sequential/parallel tool execution, tool result finalization | `SOURCE`, [no-tool source trace complete](../../systems/pi/) |

## Claude Code Evidence Boundary

The separately indexed local snapshot contains a query-loop coordinator and
distinct tool, API, compaction, permission, and CLI surfaces. This is a
sanitized `OBSERVATION` about a local static artifact, not evidence that those
internals match the locked `2.1.224` runtime. Exact snapshot pointers remain
local-only until a finding can be independently supported or safely promoted.

## First Trace Contract

The first pass intentionally excludes tool execution. For each system, trace:

1. the callable or event that begins a turn;
2. creation of turn/session state;
3. instruction and message assembly;
4. construction of the provider request;
5. streaming or response normalization;
6. the no-tool completion decision;
7. persistence and the user-visible completion event.

Only after all seven hops are supported will the same turn be extended through
one tool call and its follow-up model request.

## Current Unknowns

- Which public CLI entry point reaches each coordinator?
- Which object owns the authoritative loop state?
- Is a no-tool response terminal by stop reason, absence of tool calls, an
  explicit runtime state, or a combination?
- Which state updates happen before the final user-visible event?
- Which Claude Code findings can be verified against runtime observations or
  public contracts without relying on the version-unverified snapshot?

## Next Step

Extend Pi through one tool call, then trace the same no-tool slice in Codex.
Use Pi's vocabulary as a comparison aid—not as a template imposed on Codex,
OpenCode, or Claude Code.
