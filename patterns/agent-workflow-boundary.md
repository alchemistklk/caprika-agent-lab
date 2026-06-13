# Agent Workflow Boundary

## Problem

Agent products become hard to trust when the workflow boundary is hidden inside
a chat transcript: users cannot see what was read, which tools ran, what files
changed, where review happened, or how to recover from a failed step.

## Pattern

Represent an agent workflow as an inspectable boundary:

- inputs
- selected tools
- provider/model constraints
- filesystem artifacts
- progress state
- human review gates
- retry and recovery paths
- final export or handoff

The goal is to make the agent feel less like a black box and more like a
product workflow that can be debugged.

## When To Use

- Use when an agent touches files, external tools, paid APIs, publishable
  content, or user-visible product state.
- Avoid when the task is a one-shot answer with no durable artifact or user
  decision.

## Implementation Shape

- State: explicit progress phases instead of one opaque "running" state.
- Tool boundary: schemas, auth status, timeout, retry policy, and output shape.
- Error handling: recoverable errors should keep partial artifacts visible.
- Human review: users can approve, reject, retry, or edit before final output.
- Artifacts: every durable output has a path, preview, or export record.

## Example

Future labs should link back here when they expose a clear workflow boundary.

## Tradeoffs

This pattern adds product and engineering overhead, but it makes agent behavior
more understandable, reviewable, and reusable.
