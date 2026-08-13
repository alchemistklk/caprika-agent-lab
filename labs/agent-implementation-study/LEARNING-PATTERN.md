# Agent Implementation Learning Pattern

> This is the default learning protocol for the implementation study. Unless a
> study note explicitly says otherwise, every mechanism is learned in the order
> **pseudocode → abstract specification → concrete agent implementation**.

## Why This Pattern Exists

Source code is evidence, but reading symbols first can make one implementation
look like the concept itself. This pattern first builds an executable mental
model, then defines a reusable contract, and only then maps that contract onto
Claude Code, Codex, Pi, OpenCode, LangChain, or another system.

The unit of study is one bounded mechanism, not an entire subsystem. Examples
include History Snip, Microcompact, Auto Compact, and Context Collapse.

## Source-First Sequencing Rule

Before dividing a subsystem into lessons, first trace its caller and build the
complete source-backed execution sequence.

- The learner's remembered list is a useful hypothesis and recall checkpoint,
  but it is not evidence of completeness or ordering.
- The source-backed execution order is the default study order because it
  preserves data dependencies and state transitions.
- If a concept must be introduced out of execution order, label that explicitly
  as a teaching prerequisite and return to the source sequence afterward.
- Conditional, mutually exclusive, recovery-only, and unavailable stages must
  be marked rather than flattened into one unconditional pipeline.
- Newly discovered stages are inserted at their proven call position; the
  sequence is revised instead of protecting the original outline.

The sequence itself uses the same evidence labels as any other claim. It may be
`SOURCE`, `TRACE`, `INFERENCE`, or `UNKNOWN`; it is never established only from
memory.

## The Three-Layer Learning Order

### Layer 1 — Pseudocode: What happens?

Write the smallest control flow that explains the mechanism without using the
target system's symbol names.

The pseudocode must show:

- the input;
- the trigger or eligibility condition;
- the transformation or decision;
- the output and state change;
- the no-op, failure, or retry path.

Template:

```text
input = current_state

if mechanism_is_not_eligible(input):
    return unchanged(input)

result = apply_mechanism(input)

if result succeeded:
    return next_state(result)

return failure_or_fallback(input)
```

Exit check: I can predict what happens in a small example before looking at the
real source code.

### Layer 2 — Abstract Specification: What contract must any Agent satisfy?

Remove product-specific names and describe the mechanism as a reusable Agent
contract.

Record all of the following:

1. **Responsibility** — the single problem the mechanism owns.
2. **Non-responsibility** — nearby problems it deliberately does not solve.
3. **Inputs and outputs** — including unchanged, success, retry, and terminal
   outcomes.
4. **Preconditions and trigger** — when it is allowed or required to run.
5. **State transition** — state before and after the operation.
6. **Invariants** — message ordering, tool-use/tool-result pairing, identity,
   persistence, cache, or retry properties that must remain valid.
7. **Information policy** — what is retained, transformed, summarized,
   removed, recoverable, or permanently lost.
8. **Failure and recovery** — what happens if the mechanism cannot complete.
9. **Tradeoffs** — token savings, latency, cost, accuracy, complexity, and
   recoverability.

Suggested interface shape:

```text
Mechanism.apply({
    currentState,
    policy,
    persistedEvidence,
    cancellationSignal
}) ->
    Unchanged
  | Transformed { nextState, evidence }
  | Retry { nextState, reason }
  | Terminal { error }
```

Exit check: I can use the specification to look for an equivalent mechanism in
another Agent without searching for the same class or function name.

### Layer 3 — Concrete Agent Implementation: How does this system realize it?

Map each abstract responsibility onto exact source symbols and runtime state.
Do not start by reading an entire file. Find the smallest source path that
proves the control flow.

For each implementation, capture:

- the caller and the execution position in the larger pipeline;
- the guard or trigger;
- the central function call;
- the important input and return types;
- the before/after state mutation;
- persistence and Resume behavior;
- failure, retry, and terminal branches;
- model decisions versus deterministic runtime decisions;
- three to five essential source excerpts with stable code pointers.

Use a mapping table:

| Abstract concept | Concrete symbol | Evidence | Notes |
|---|---|---|---|
| Trigger | exact guard/function | `SOURCE`/other label | version boundary |
| Transformation | exact function | evidence label | information effect |
| State transition | exact type/assignment | evidence label | before → after |
| Recovery | retry/fallback path | evidence label | loop guard |

Exit check: every important arrow in the pseudocode has either a concrete code
pointer or an explicit `UNKNOWN`.

## The Discussion Loop

The three layers are followed by a fixed learning loop.

### 1. Work one example by hand

Use a minimal message chain or state transition and write the before/after
views. Keep these views separate when relevant:

```text
Persisted transcript
Runtime state
Model-facing context
Provider request
```

### 2. Test a boundary or counterexample

Ask at least one question that would expose a false mental model, such as:

- What happens when the mechanism is not eligible?
- What happens to tool-use/tool-result pairs across the transformation?
- Does Resume replay the decision or recompute it?
- Is removed model context still retained locally?
- Can retry repeat forever?

### 3. Draw the mechanism

Each completed topic should have:

- one small workflow or state-transition diagram;
- one before/after data-view diagram when information changes;
- code screenshots only for the smallest excerpts that prove the central
  guard, transformation, and state update.

Identifiers remain visible in screenshots so the visual explanation stays
traceable to source.

### 4. Record an evidence ledger

Every important claim uses the repository evidence model:

- `SOURCE`, `TEST`, `TRACE`, `DOC`, or `OBSERVATION` for direct evidence;
- `INFERENCE` for bounded reasoning;
- `UNKNOWN` when the source, runtime, or version cannot prove the claim.

Never silently promote an inference into an implementation fact. A missing
module is a research boundary, not permission to reconstruct its internals.

### 5. Retrieve, do not only reread

Close each topic with:

1. a three-sentence teach-back: problem, mechanism, tradeoff;
2. one state-transition reconstruction from memory;
3. three to five closed-book questions;
4. one comparison question that transfers the abstraction to another Agent.

Wrong answers are saved as corrections to the mental model, not overwritten.

## Standard Topic Note

Use this structure for every future mechanism:

```text
# <Mechanism>

## 0. Question and evidence boundary
## 1. Pseudocode
## 2. Abstract specification
## 3. <Agent> implementation
### Pipeline position
### Essential code
### State before and after
### Persistence and recovery
## 4. Worked example
## 5. Boundary case or counterexample
## 6. Diagram and code screenshots
## 7. Evidence ledger
## 8. Teach-back and closed-book check
## 9. Open questions
```

## Definition of Learned

A topic is not complete merely because its source file was read. It is learned
when the learner can:

1. reproduce the pseudocode without the source;
2. state the abstract contract and at least two invariants;
3. trace the concrete implementation from trigger to state update;
4. distinguish retained state from the model-facing projection;
5. explain one failure or recovery path;
6. name the implementation's evidence boundary and unresolved unknowns;
7. use the same abstract questions to inspect another Agent.

Only after a topic reaches this boundary should it enter the cross-system
comparison table.

## Current Claude Code Part 2 Sequence

The current study follows this source-backed pre-request pipeline:

```text
Agent State messages
→ Compact Boundary selection
→ Tool Result Budget
→ History Snip
→ Microcompact
→ Context Collapse
→ Auto Compact
→ System/User Context assembly
→ Provider request
```

Some stages are guarded or mutually constraining. Their presence in the call
sequence does not mean every stage transforms every request. Reactive Compact
is studied afterward as a recovery-only branch because it reacts to provider
overflow after the normal pre-request pipeline has run.

This sequence is a current source-backed checkpoint, not a promise that the
four mechanisms first recalled by the learner are the complete Part 2 scope.
