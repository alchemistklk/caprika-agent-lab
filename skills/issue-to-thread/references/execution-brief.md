# Execution Brief Template

Fill required sections. Omit optional risk sections when empty. Validate the
completed brief with `scripts/issue-thread brief` before creating a thread.

````md
# Execution Brief

You are a clean Codex execution thread. Treat this issue as the execution source
of truth. Do not reopen settled planning. Preserve unrelated changes, validate,
and keep execution status separate from delivery work.

## Issue

<title and URL/path/number>

## Thread

Title: `<validated title>`
Target: `<project and local | worktree | projectless>`

## Goal / What To Build

<one or two sentences describing the end-to-end outcome>

## Acceptance Criteria

- [ ] <checkable criterion>

## Validation

- `<command or manual check>`

Required validation without an approved equivalent must pass before `done`.

## Delivery Contract

Commit required: `<yes | no>`
Commit owner: `<child | parent | user | none>`
Git capability: `<writable | read-only | unknown | not-applicable>`

Resolve capability from this task's permission profile. A read-only `.git`
entry overrides filesystem owner/mode. Git delivery failure does not make
completed implementation `blocked` unless delivery is an acceptance criterion.

## Out Of Scope

- <explicit non-goal or do-not-touch area>

## Callback

Mode: `<automatic | manual>`
Explicit parent: `<parent-thread-id | omitted>`

For `create_thread`, use automatic mode and resolve the delegation source id
before the explicit parent. Never target this child thread itself.

At closeout, run `scripts/issue-thread callback --example` only if the input
schema is needed. Pass completed JSON to `scripts/issue-thread callback`, then:

- automatic: send its stdout once with `send_message_to_thread`;
- manual: print its stdout once with the exact fallback reason.

Do not archive this thread.

## Optional Risk Context

### Parent / Source

<stable links or paths>

### Current Repo State

<branch, relevant paths, WIP, and assumptions>

### Decisions Already Made

- <settled decision the child must not revisit>

### Suggested Skills

Required:
- `<skill>` — <why>

Recommended:
- `<skill>` — <why>

Optional:
- `<skill>` — <when>

### Blocked By

- <dependency URL/id>

### Escalation

- <specific condition requiring a parent decision>
````

