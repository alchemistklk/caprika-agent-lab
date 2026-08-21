# Pi Design and Runtime Study Roadmap

## Purpose

This study explains how Pi's design philosophy became a working agent runtime,
how its intentionally small default surface is extended by plugins and external
tools, and how those boundaries evolved over time.

The study is not a product ranking, a feature checklist, or a generic Pi
tutorial. Its central question is:

> How did Pi turn a preference for visible, predictable, minimal defaults into
> an extensible coding-agent runtime, and which parts of that philosophy still
> hold as the project grows?

The implementation trace already recorded in [README.md](./README.md) remains
valid research evidence. The interactive learning sequence restarts from Pi's
origin and design constraints so that the runtime is understood as a response
to those constraints rather than as an isolated loop.

## Scope and Evidence Boundary

- **Locked implementation baseline:** Pi `v0.84.1`, commit
  `53fa77ccd8a279eb87e92294ef3687b03ff80112`.
- **Current source scope:** `packages/ai`, `packages/agent`,
  `packages/coding-agent`, and `packages/tui`, with other packages introduced
  only when a bounded question requires them.
- **Historical evidence:** official posts, versioned documentation, release
  notes, changelogs, exact tags, and source diffs at selected milestones.
- **Plugin evidence:** exact repository, version or commit, installation state,
  extension seam, runtime behavior, and explicit unknowns.
- **Runtime evidence:** no behavior is promoted from source fact to observed
  behavior without a sanitized trace or executed test.

Every important claim uses one or more of these labels:

| Label | Meaning |
|---|---|
| `SOURCE` | Exact source, changelog, or release artifact at a named revision |
| `TEST` | Project-owned test and its observed result |
| `TRACE` | Sanitized runtime path captured in a named setup |
| `DOC` | Versioned official documentation or an author explanation |
| `INFERENCE` | Bounded interpretation derived from other evidence |
| `UNKNOWN` | Missing, inaccessible, ambiguous, or not yet verified evidence |

## The Complete Learning Narrative

```text
origin and dissatisfaction
    -> design constraints
    -> minimal architecture
    -> minimal coding-agent surface
    -> agent runtime implementation
    -> coding-agent product shell
    -> intentional omissions
    -> extension system
    -> representative plugins
    -> versioned evolution
    -> current architectural tensions
```

The narrative has two connected axes:

- **Vertical system model:** understand Pi's own vocabulary, layers, and
  boundaries before comparing it with another agent.
- **Longitudinal evolution:** revisit the same boundary at selected historical
  tags to see why it moved, split, or became extensible.

## Part 0 — Lock the Subject and Provenance

### Questions

- Which Pi repository, package scope, tag, and commit are under study?
- What changed when the repository and npm packages moved from the original
  `badlogic` / `@mariozechner` locations to `earendil-works` /
  `@earendil-works`?
- Which facts belong to the locked `v0.84.1` baseline, and which belong to
  earlier or later versions?
- What can source prove without an installed matching runtime?

### Exit condition

The subject, source provenance, historical checkpoints, and evidence limits are
reproducible without relying on the learner's memory.

## Part 1 — Why Pi Exists

### Questions

- Was Pi reacting to the number of features, or to invisible and unstable
  default behavior?
- Why did changing prompts, changing tool definitions, hidden context, and
  limited session observability matter?
- Why was a terminal harness the first product surface?
- Which earlier agent-building experiences shaped the design?

### Intended outcome

Explain Pi as a response to workflow unpredictability and hidden context, not
merely as a smaller competitor to other coding agents.

## Part 2 — The Design Philosophy

Study each principle independently:

1. a minimal default surface rather than minimal possible capability;
2. general primitives before workflow-specific product features;
3. visible and controllable context;
4. files and CLIs as inspectable, composable interfaces;
5. user-owned workflow policy;
6. extension seams instead of one built-in implementation;
7. explicit tradeoffs rather than hidden safety or convenience behavior.

The reusable feature-admission question is:

```text
Does every agent run need this capability?
    yes -> look for the narrowest reusable core primitive
    no  -> can a tool, file, CLI, skill, extension, or package express it?
              yes -> keep the workflow outside the core
              no  -> investigate which general extension seam is missing
```

### Exit condition

The learner can distinguish a minimal product, a minimal default surface, and a
minimal extensible kernel.

## Part 3 — Why the Architecture Has Separate Layers

Study the responsibility and dependency boundary of:

| Layer | Primary responsibility |
|---|---|
| `pi-ai` | Provider-neutral model, message, streaming, tool-call, usage, and authentication contracts |
| `pi-agent-core` | Agent state, event reduction, tool execution, continuation, and termination |
| `pi-tui` | Terminal input, rendering, components, and differential updates |
| `pi-coding-agent` | The coding-agent product: sessions, context, built-in tools, extensions, modes, and user workflow |

### Questions

- Why should provider-specific conversion stay outside the loop?
- Why should the loop not depend on a terminal UI?
- Which coding-agent behaviors would be inappropriate in a reusable agent core?
- How do interactive, print, JSON, RPC, and SDK modes reuse the same lower
  layers?

## Part 4 — The Minimal Coding-Agent Surface

### Topics

1. the default system prompt and its context cost;
2. the four default tools: `read`, `write`, `edit`, and `bash`;
3. the optional read-only tools: `grep`, `find`, and `ls`;
4. why `bash` acts as a capability multiplier;
5. why model familiarity with common tool schemas matters;
6. why a README, skill, or CLI may be preferable to another always-loaded tool;
7. the difference between available tools and default tools.

### Exit condition

The learner can explain why four tools can be sufficient without claiming that
Pi implements only four tool definitions or has only four total capabilities.

## Part 5 — The Agent Runtime

This part is deliberately divided into small mechanisms:

1. user input enters an agent run;
2. an immutable context snapshot is created from mutable agent state;
3. one provider-neutral model request is assembled;
4. streamed deltas become one finalized assistant message;
5. a `toolCall` represents model intent, not a side effect;
6. tool lookup, argument preparation, and validation occur;
7. pre-execution hooks may block a call;
8. `execute()` crosses the side-effect boundary;
9. progress and final results become events;
10. a `toolResult` is paired with its call and returned to context;
11. the next model request starts;
12. no-tool, error, abort, length, and explicit-stop branches terminate;
13. steering and follow-up messages change continuation semantics;
14. parallel execution preserves a deterministic model-facing result order.

The existing no-tool source trace in [README.md](./README.md) is research input
for this part, not permission to teach all fourteen mechanisms in one lesson.

## Part 6 — From a Loop to a Coding-Agent Product

### Topics

- provider and model selection;
- API-key and OAuth resolution;
- system instructions and hierarchical context files;
- session persistence, tree navigation, resume, fork, and clone;
- context estimation and compaction;
- retries and settled-state semantics;
- interactive TUI behavior;
- print, JSON, RPC, and SDK integration modes;
- events, logs, usage accounting, and observable state.

### Boundary question

For each topic, identify whether it belongs to the provider layer, reusable
agent runtime, coding-agent product, UI, persistence layer, or an extension.

## Part 7 — Intentional Omissions

Study each omission as an architectural decision rather than a missing feature:

1. no built-in MCP;
2. no built-in subagent workflow;
3. no built-in plan mode;
4. no built-in to-do state;
5. no built-in permission popups;
6. no built-in background-bash manager.

Each topic asks:

```text
What problem does the omitted feature solve?
How does Pi solve or externalize the same problem?
What complexity stays outside the default runtime?
What cost or risk is transferred to the user?
Which extension seam allows another implementation?
```

## Part 8 — The Extension System

Separate Pi's extension vocabulary before studying ecosystem packages:

| Surface | Role |
|---|---|
| Extension | Runtime TypeScript code that can register tools, commands, events, UI, providers, and policy |
| Skill | Progressively disclosed instructions and domain knowledge |
| Prompt template | Reusable input expansion |
| Theme | Presentation customization |
| Pi package | Distribution container for one or more Pi resources |

### Mechanisms

- extension discovery and lifecycle;
- command and tool registration;
- input, agent, tool-call, tool-result, and session events;
- custom provider registration;
- resource discovery and reload;
- extension-provided UI;
- built-in tool replacement;
- package discovery, installation, pinning, and updates;
- trust, full-process access, and supply-chain boundaries.

## Part 9 — Representative Plugin Case Studies

Plugins are selected for architectural coverage, not popularity ranking. The
initial candidate set is intentionally provisional until each repository and
version is locked.

| Capability Pi does not prescribe | Candidate case-study direction | Main question |
|---|---|---|
| Subagents | `pi-subagents` | How are child context, lifecycle, result return, and cost bounded? |
| Agent orchestration | `pi-fabric` | Can orchestration remain user-defined while reusing one Pi process? |
| Durable goals or planning | Goal and workflow packages | Should workflow state live in runtime memory, session state, or files? |
| Parallel code work | Worktree packages | How are task ownership, process identity, and Git isolation connected? |
| MCP access | MCP adapter packages | How is tool-description context cost controlled? |
| Execution isolation | Gondolin and tool-routing extensions | Can the execution environment change without modifying the loop? |
| Repository operations | GitHub tool packages | When is a native tool better than invoking a CLI through `bash`? |
| Desktop interaction | Computer-use packages | How does a non-terminal side effect enter the same tool contract? |

Each case study follows this sequence:

```text
problem without the plugin
    -> abstract plugin contract
    -> exact extension seam
    -> implementation and runtime state
    -> context and side-effect boundary
    -> failure and security boundary
    -> reason it remains outside the core
    -> evidence ledger and unknowns
```

## Part 10 — Versioned Evolution

The study uses selected checkpoints rather than narrating every release:

| Version | Preliminary reason to inspect | Current evidence status |
|---|---|---|
| `v0.10.0` | Initial public coding-agent product shape | `SOURCE` changelog; exact code checkout pending |
| `v0.31.0` | Agent loop moved from `pi-ai` into `pi-agent-core` | `SOURCE` changelog; exact code comparison pending |
| `v0.32.0` | One queue became distinct steering and follow-up semantics | `SOURCE` changelog; exact code comparison pending |
| `v0.72.0` | Explicit graceful stop after a completed turn | `SOURCE` changelog; exact code comparison pending |
| `v0.74.0` | Repository and npm package-scope migration | `SOURCE` changelog; provenance reconstruction pending |
| `v0.77.0` | Tool registry and branch-scoped active tools | `SOURCE` changelog; exact code comparison pending |
| `v0.80.0` | Models, providers, and harness ownership changed | `SOURCE` changelog; exact code comparison pending |
| `v0.84.0` / `v0.84.1` | Durable sessions, telemetry, remote protocol, and new stop semantics | Locked source baseline |

For every checkpoint:

1. identify the pressure or failure that motivated the change;
2. locate the responsibility before and after the change;
3. classify it as a product feature, reusable primitive, extension seam, or
   operational hardening;
4. record compatibility and migration costs;
5. ask whether all users now pay additional default complexity;
6. update the evolution model only after exact-tag source verification.

## Part 11 — Synthesis

The final synthesis keeps three views separate:

```text
original Pi thesis
    personal, visible, predictable, minimal coding harness

current default product surface
    compact prompt, four default tools, explicit user workflow

current toolkit and implementation
    providers, sessions, telemetry, protocols, SDKs, and extension platform
```

The final questions are:

- Which minimalism claims are still supported by the default runtime?
- Which complexity was eliminated, and which was moved to users or plugins?
- Which extension needs became reusable core primitives?
- Where has toolkit growth increased conceptual or maintenance complexity?
- Which ideas are reusable in another agent, and which depend on Pi's risk and
  workflow preferences?

Cross-agent comparison starts only after an equivalent Pi slice has completed
the evidence and learning exit conditions.

## Per-Topic Learning Cadence

Every bounded topic uses the repository-wide learning pattern, at a slower
interactive pace:

```text
1. State one question and its evidence boundary.
2. Explain the smallest product or engineering problem.
3. Write implementation-neutral pseudocode.
4. Work through one example with the learner.
5. Confirm the learner can predict the transition.
6. Define the abstract Agent contract and invariants.
7. Map only one or two Pi source locations.
8. Test one boundary or counterexample.
9. Record SOURCE / TEST / TRACE / DOC / INFERENCE / UNKNOWN.
10. Save the learner's current mental model and open questions.
```

Formal tests, closed-book review, and comparison exercises are deferred during
the initial pass. Lightweight prediction and clarification remain part of each
lesson because a polished source summary is not evidence that the mechanism
has been learned.

## Planned Artifact Layout

All new Pi notes stay under this directory and do not modify Claude Code study
conclusions.

```text
systems/pi/
├── README.md
├── STUDY-ROADMAP.md
├── design-philosophy.md
├── architecture-layers.md
├── minimal-tools.md
├── agent-runtime/
├── product-runtime/
├── intentional-omissions/
├── extension-system/
├── plugin-case-studies/
├── evolution/
└── open-questions.md
```

Directories and notes are created only when their first bounded topic begins;
the roadmap does not pre-fill conclusions that have not yet been studied.

## Current Learning Position

- **Research state:** the locked `v0.84.1` no-tool turn has a source-backed
  trace in [README.md](./README.md).
- **Learning state:** restart at Part 1, "Was Pi reacting to feature count, or
  to invisible and unstable defaults?"
- **Next artifact:** `design-philosophy.md`, created after the first interactive
  topic establishes a learner-owned mental model.
