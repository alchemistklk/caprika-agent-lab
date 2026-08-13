# Agent Implementation Study

## Purpose

This is a personal, implementation-first study of how production-oriented
agents and agent frameworks work. The goal is to understand the code paths,
runtime state, control boundaries, and engineering tradeoffs behind each
system—not to produce a feature checklist, framework tutorial, leaderboard, or
premature evaluator.

The initial study set is:

- Codex
- Pi
- OpenCode
- Claude Code
- LangChain and LangGraph

The study is related to the public course under
`content-workflows/agent-from-understanding-to-practice`, but it is not governed
by the course's episode or production schedule. Findings may inform the course
later only after they are verified, sanitized, and deliberately adapted.

## Category Boundary

The systems are not equivalent categories.

- Codex, Pi, OpenCode, and Claude Code are studied as complete coding-agent
  products or harnesses.
- LangChain and LangGraph are studied as libraries for building agent runtimes
  and workflows.

Cross-system comparisons must name the layer being compared. A product-level
behavior must not be presented as directly equivalent to a framework API.

## Research Principles

1. **Follow the implementation.** Start from an exact local version and public
   source revision, then trace real entry points and call paths.
2. **Separate evidence from inference.** Record what source, tests, runtime
   traces, or documentation prove. Mark every architectural inference.
3. **Trace one path at a time.** Establish a minimal happy path before studying
   retries, compaction, subagents, or other branches.
4. **Study boundaries, not only abstractions.** Pay special attention to where
   model output becomes a tool call, filesystem change, process, network call,
   or approval request.
5. **Verify behavior.** Use a minimal experiment or trace when source reading
   alone cannot prove runtime behavior.
6. **Preserve uncertainty.** Record `unknown` when an implementation is closed,
   unavailable, version-dependent, or not observable.
7. **Do not publish private evidence.** Local paths, credentials, private
   prompts, session contents, and unreleased behavior must not enter this
   public repository.
8. **Delay judgment.** Explain the constraints and tradeoffs of a design before
   deciding whether it is reusable or preferable.

## Default Learning Pattern

Every bounded mechanism is learned using the same sequence:

```text
pseudocode → abstract specification → concrete agent implementation
```

The complete discussion, visualization, evidence, and retrieval protocol is in
[Agent Implementation Learning Pattern](./LEARNING-PATTERN.md). This is the
default for all future Claude Code, Codex, Pi, OpenCode, and LangChain/LangGraph
study slices.

## Evidence Model

Every important claim should carry one or more evidence labels:

| Label | Evidence | What it can support |
|---|---|---|
| `SOURCE` | Source code at an exact repository and revision | Static implementation facts |
| `TEST` | A project-owned test and its observed result | Behavior covered by that test |
| `TRACE` | A captured, sanitized runtime path | Behavior in the recorded setup |
| `DOC` | Versioned official documentation | Publicly documented contract |
| `OBSERVATION` | Visible local product behavior | User-visible behavior, not hidden internals |
| `INFERENCE` | Reasoning from other evidence | A bounded explanation that still needs proof |
| `UNKNOWN` | Missing or inaccessible evidence | An explicit research limit |

For each source, record the repository or product, version or commit, local
version when applicable, access date, and relevant path or URL. Recheck these
before resuming a study after an upgrade.

## Core Implementation Questions

Each system is investigated using the same questions, while allowing its own
architecture to determine the actual path.

### 1. Process and entry points

- What executable, CLI command, service, or library call starts a run?
- Which processes exist, and how do CLI, TUI, desktop, daemon, and child
  processes communicate?
- Where are configuration and project instructions loaded?

### 2. Agent loop

- Where is the main model-call/tool-call loop?
- What are its explicit states and transitions?
- How are completion, continuation, interruption, cancellation, and failure
  represented?
- Which decisions belong to the model and which belong to deterministic code?

### 3. Model and provider layer

- How are models, providers, capabilities, and request options represented?
- Where are messages translated into provider-specific requests?
- How are streaming events normalized?
- How are provider errors, rate limits, and retries handled?

### 4. Instructions and context

- How are system instructions, user input, project files, skills, memory, and
  tool results assembled and ordered?
- How are token limits estimated?
- What triggers selection, truncation, summarization, or compaction?
- What information survives into the next turn or resumed session?

### 5. Tools and environment

- How are tools registered, described, validated, and dispatched?
- Where does a model tool request become a real side effect?
- How are shell, filesystem, browser, MCP, and custom tools isolated?
- How are tool output, errors, and partial results returned to the model?

### 6. Permissions and safety controls

- What is allowed automatically, sandboxed, denied, or sent for approval?
- Where is policy evaluated, and what data enters that decision?
- How are secrets and sensitive output prevented from leaking?
- Can policy be bypassed accidentally through another execution path?

### 7. Session state and persistence

- What objects represent a run, turn, message, event, tool call, and artifact?
- What is stored in memory, on disk, or remotely?
- How do resume, rollback, branching, and concurrent updates work?
- What identities connect model events, tool executions, and user-visible state?

### 8. Control, recovery, and concurrency

- How are timeouts, cancellation, retries, and stop conditions implemented?
- What happens after a crash or interrupted tool call?
- How are concurrent tools, tasks, or subagents scheduled and joined?
- Which operations are idempotent, replayable, or recoverable?

### 9. Extension surfaces

- How do skills, plugins, hooks, commands, MCP servers, and subagents extend the
  system?
- Which extension contracts are stable and which depend on internal details?
- How are extension permissions, lifecycle, and failures contained?

### 10. Observability and verification

- Which events, logs, traces, and artifacts are available?
- Can a full run be reconstructed from retained evidence?
- Which behaviors are covered by unit, integration, provider, or behavioral
  tests?
- What is telemetry, what is product regression testing, and what is formal
  agent evaluation?

## Standard Study Sequence

Study one system at a time using this order.

### Phase 0: Lock the target

Record the exact product, repository, local executable, version, commit or tag,
configuration boundary, and source-availability limits. Resolve ambiguous names
such as “Pi” before drawing conclusions.

**Exit condition:** the subject and evidence boundary are reproducible.

### Phase 1: Build the surface map

Identify packages, processes, entry points, configuration, persistence, tool
surfaces, extension points, and owned tests. Do not explain the full
architecture yet.

**Exit condition:** a source map shows where each core question is likely
answered.

### Phase 2: Trace the minimal happy path

Follow one simple request from input through instruction assembly, model call,
stream handling, optional tool execution, state update, and final output.

**Exit condition:** every hop has a code pointer, trace, documented boundary, or
explicit `UNKNOWN`.

### Phase 3: Inspect state and context

Study message types, session state, persistence, context construction,
compaction, resume behavior, and versioning.

**Exit condition:** the lifetime of one turn and one multi-turn session can be
explained without hand-waving.

### Phase 4: Inspect tools and side effects

Trace tool registration, schema validation, dispatch, environment access,
result handling, approval, and sandbox decisions.

**Exit condition:** the exact boundary where generated intent becomes an
external action is identified.

### Phase 5: Inspect control and recovery

Trigger or trace a bounded failure, cancellation, retry, interrupted stream, or
failed tool call. Then inspect concurrency and subagent behavior where present.

**Exit condition:** at least one failure path is supported by source plus a test
or sanitized observation when possible.

### Phase 6: Inspect extension and observability

Map skills, plugins, hooks, MCP, logs, events, traces, and test layers. Identify
what an external developer can safely depend on.

**Exit condition:** stable public contracts are separated from internal or
version-sensitive seams.

### Phase 7: Synthesize the system model

Produce a compact architecture diagram, one end-to-end sequence, the main data
types, important control boundaries, unresolved questions, and design
tradeoffs.

**Exit condition:** another reader can verify the explanation from retained
evidence.

### Phase 8: Compare only the completed slice

Compare the studied system with previously completed systems only along the
same implementation question and evidence level. Do not fill missing cells
with assumptions.

**Exit condition:** comparisons distinguish product behavior, framework
abstraction, implementation fact, and inference.

## Per-System Study Record

Use the following structure when a system study begins:

```markdown
# <System> Implementation Study

## Scope Lock

- System:
- Category:
- Local version:
- Source repository:
- Commit or tag:
- Access date:
- Included surfaces:
- Excluded surfaces:
- Known source limits:

## Current Phase

- Phase:
- Status: `planned | researching | verified | blocked`
- Next question:

## Source Map

| Concern | Primary path or surface | Evidence | Confidence |
|---|---|---|---|

## Minimal Execution Path

1. Input:
2. Instruction and context assembly:
3. Model request:
4. Stream or response handling:
5. Tool dispatch:
6. State update:
7. Completion:

## Main Types and Contracts

## Boundary Findings

### Model versus deterministic runtime

### Intent versus side effect

### Automatic action versus approval

### Ephemeral versus persisted state

## Failure and Recovery Path

## Minimal Verification Experiment

- Question:
- Setup:
- Expected evidence:
- Observed result:
- Limitations:

## Findings

| Claim | Label | Evidence pointer | Confidence | Open question |
|---|---|---|---|---|

## Design Tradeoffs

## Reusable Ideas

## Unknowns and Next Questions
```

## Cross-System Comparison Contract

A comparison row is valid only when all entries share:

- the same implementation question;
- a named version or revision;
- a compatible evidence level;
- a clearly stated product or framework layer;
- a recorded `UNKNOWN` instead of an inferred implementation when evidence is
  unavailable.

The comparison should answer “how is this boundary implemented and why?” before
asking “which is better?”

## Unified Comparative Research Model

Use two connected axes instead of finishing one project before opening the
next.

### Vertical axis: system model

Build enough of each system's own architecture to understand its vocabulary,
process boundaries, state model, and complete execution path. This prevents a
shared comparison table from flattening different designs into misleading
feature names.

### Horizontal axis: implementation slice

Choose one engineering question, trace it independently through every locked
system, and compare only after each trace has reached its evidence boundary.
The first shared slice is **one complete agent turn**.

For every horizontal slice:

1. state the exact shared question;
2. lock the relevant version of every system;
3. identify its primary types and entry point;
4. trace the happy path;
5. trace one stop, error, or recovery branch when available;
6. record source facts and runtime observations separately;
7. compare control ownership, state transitions, and tradeoffs;
8. carry `UNKNOWN` forward instead of completing missing implementations by
   analogy.

## Comparison Systems and Evidence Boundaries

The current cross-system version baseline is recorded in
[`version-lock-2026-08-07.md`](./version-lock-2026-08-07.md).

| System | Study role | Primary evidence | Boundary |
|---|---|---|---|
| [Codex](./systems/codex/) | Coding-agent product and harness | Exact public source revisions plus separately versioned local runtimes | Stable source, terminal CLI, desktop bundle, and cloud behavior remain separate evidence lanes |
| Claude Code | Coding-agent product and harness | Versioned official behavior, local runtime observation, and a locally held static source snapshot | The snapshot is unofficial, lacks Git history, and must remain local-only evidence |
| OpenCode | Open-source coding-agent product | Exact public source revision | No matching executable is installed; the existing local fork is a separate evidence lane |
| [Pi](./systems/pi/) | Compact coding-agent runtime and product reference | Exact public source revision | No local executable is installed; runtime claims require a later experiment |
| LangChain / LangGraph | Agent-framework reference | Exact public source revision, official contracts, and minimal experiments | Compare framework primitives, not whole-product behavior |

Claude Code source-map material must not be copied into this public repository.
Only sanitized architectural findings that are independently supportable or
clearly labeled as bounded local observations may be promoted later.

## Horizontal Study Tracks

| Order | Shared implementation question | Primary output | Status |
|---:|---|---|---|
| 1 | How does one agent turn start, loop, invoke tools, and stop? | [End-to-end sequence and state-transition comparison](./tracks/01-agent-turn/source-navigation.md) | In progress |
| 2 | How are instructions and context assembled? | Prompt-layer and context-lifecycle comparison | Planned |
| 3 | How is the model/provider boundary implemented? | Request, streaming, normalization, and fallback comparison | Planned |
| 4 | How does generated intent become a tool side effect? | Tool registry, validation, dispatch, and result comparison | Planned |
| 5 | Where are permissions, approvals, and sandbox policy enforced? | Control-boundary and bypass-risk comparison | Planned |
| 6 | How are sessions, messages, and artifacts persisted and resumed? | State-lifetime and recovery comparison | Planned |
| 7 | How are truncation, compaction, and memory handled? | Context-pressure strategy comparison | Planned |
| 8 | How are errors, cancellation, retries, and stop conditions handled? | Failure-state comparison | Planned |
| 9 | How do skills, plugins, hooks, and MCP extend the runtime? | Extension-contract comparison | Planned |
| 10 | How are subagents and concurrent work coordinated? | Ownership, scheduling, and join-semantics comparison | Planned |
| 11 | What logs, events, tests, and traces make behavior inspectable? | Observability and verification comparison | Planned |

## System Baseline Progress

| System | Baseline status | Next requirement |
|---|---|---|
| Codex | `rust-v0.147.0` clean checkout and full source index ready | Trace the smallest no-tool turn from `run_turn` |
| Claude Code | Local runtime locked at `2.1.224`; local snapshot indexed separately | Record a formal scope lock without claiming that the snapshot matches `2.1.224` |
| OpenCode | `v1.18.14` clean checkout and full source index ready; existing fork preserved | Trace the prompt/processor boundary for a no-tool turn |
| Pi | `v0.84.1` indexed; [no-tool turn source trace complete](./systems/pi/) | Extend the trace through one tool call and run a minimal verification |
| LangChain / LangGraph | Deferred reference | Introduce only after the product-harness comparison is stable |

A system does not become “complete” all at once. Progress is recorded both by
its vertical baseline phase and by completed horizontal implementation slices.

## Expected Output of This Lab

For each completed system slice, retain:

- an exact scope and version record;
- a verified source map;
- one end-to-end execution path;
- one failure or recovery path when observable;
- a minimal sanitized verification experiment;
- an architecture diagram or sequence diagram;
- evidence-labeled findings and explicit unknowns;
- reusable implementation ideas separated from product-specific behavior.

These outputs are research artifacts. Turning them into a public pattern,
course episode, implementation recommendation, or evaluation is a separate
decision.
