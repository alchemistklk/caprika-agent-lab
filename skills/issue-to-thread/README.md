# Issue To Thread

Turn one approved issue into a clean Codex execution task without reopening the
planning conversation.

This skill is the execution half of a two-stage workflow:

1. Use `to-issues` to turn an approved plan or spec into independently
   executable vertical-slice issues. Review and approve the breakdown before
   publishing or assigning anything.
2. Use `issue-to-thread` for exactly one approved issue. The parent task owns
   direction and lifecycle; the child task implements, validates, and reports
   one callback.

## What It Enforces

- A concise execution brief with goal, acceptance criteria, validation, scope,
  callback mode, and Git delivery ownership.
- A stable task title that exposes the manager, scope, and primary dependency.
- An automatic callback for native Codex-created child tasks when their
  delegation source is available.
- A distinction between completed implementation and parent-owned delivery.
  A read-only `.git` sandbox does not turn a validated implementation into a
  false `blocked` result.

## What Remains Native

Codex creates, renames, messages, and archives tasks through its native tools.
The bundled `scripts/issue-thread` command only validates titles and briefs,
and validates/renders callback text. That keeps the durable, deterministic
parts scriptable without relying on private or unstable app APIs.

## Verify

From this directory:

```bash
ruby scripts/issue-thread self-test
```

Then read [`SKILL.md`](SKILL.md) for the full execution contract and
[`references/execution-brief.md`](references/execution-brief.md) for the brief
template.
