---
name: issue-to-thread
description: Turn one approved issue into a clean Codex execution thread without reopening planning. Use when handing an issue to a child thread, subthread, clean executor, or implementation thread after to-issues, including thread targeting, automatic parent callback, Git/commit ownership, delivery status, title, and archive lifecycle.
---

# Issue To Thread

Turn one approved issue into a clean execution thread. Use `to-issues` first
when the work has not yet been split into approved vertical slices.

The parent owns direction and lifecycle. The child executes one issue without
inheriting or reopening the planning conversation.

## Contract CLI

Use the bundled zero-dependency validator for deterministic checks:

```text
scripts/issue-thread
```

Run it through `with-env`. It validates titles and briefs, and validates/renders
callbacks. It does not create, message, rename, or archive Codex threads.

## Workflow

### 1. Pin one issue

Resolve one approved issue and read only the linked source material required for
safe execution. Do not create an executor while blockers or direction are vague.

### 2. Build and validate the brief

Fill `references/execution-brief.md`. Require Issue, Goal, Acceptance Criteria,
Validation, Out Of Scope, Callback, and Delivery Contract. Add repo state,
settled decisions, skills, blockers, and escalation only when they affect risk.

Delivery Contract records:

```text
Commit required: yes | no
Commit owner: child | parent | user | none
Git capability: writable | read-only | unknown | not-applicable
```

Default local/shared-WIP commits to `parent`; default isolated-worktree commits
to `child`. Record `unknown` rather than infer sandbox capability from POSIX
owner, mode, or `test -w`.

Before creation, validate the final title and brief:

```bash
with-env scripts/issue-thread title "<title>"
with-env scripts/issue-thread brief <brief-file-or-stdin>
```

### 3. Select the target

Call `list_projects` first for repo work.

- `local`: exact saved working tree or shared WIP.
- `worktree`: isolated parallel work from a clear branch/state.
- `projectless`: non-repo work; Git is `not-applicable`.

`create_thread` does not expose a sandbox-permission argument. The child resolves
its actual permission profile after startup.

### 4. Create the clean thread

Create only when the user explicitly asks. Use `create_thread` with the validated
brief. Do not use `fork_thread` unless the user explicitly requests a fork or the
parent explicitly requires completed conversation history.

Record child id, title, issue, target, callback mode, and commit owner. Let Codex
auto-name once, validate the final title with the CLI, then call
`set_thread_title`. Reapply once only if the first child response overwrites it.

### 5. Resolve runtime capability

The child resolves the callback target in this order:

1. delegation source id: `codex_delegation.source_thread_id`,
   `codexDelegation.sourceThreadId`, or `<source_thread_id>`;
2. explicit parent id in the brief;
3. manual forwarding.

Never use the child's own thread id as the parent. Threads created with
`create_thread` default to automatic callback even without an explicit parent id.

Resolve Git capability from the child's `permission_profile`. An explicit
read-only `.git` entry wins over filesystem permissions. Do not create a probe
lock solely to test access. If Git is read-only, transfer commit Delivery to the
parent or user and continue implementation.

### 6. Execute and classify

Do not reopen settled planning. Preserve unrelated changes and validate before
closeout.

- `done`: implementation and acceptance are complete. Parent-owned commit,
  review, merge, or archive remains Delivery, not a blocker.
- `blocked`: implementation or required validation cannot continue.
- `scope-change`: continuing requires materially different approved scope.

Commit/merge failure is `blocked` only when it is an explicit acceptance
criterion owned by the child. The callback CLI rejects contradictory status
combinations.

### 7. Render and deliver one callback

At closeout, inspect the callback input schema only when needed:

```bash
with-env scripts/issue-thread callback --example
```

Pass completed JSON to `issue-thread callback`; use its stdout as the callback.

In automatic mode, call `send_message_to_thread` once with
`{ threadId: parent_thread_id, prompt: callback }`. On success, do not repeat the
full callback. If target discovery or sending fails, render one manual callback
with the exact reason.

### 8. Parent closeout

The parent reviews the callback, completes Delivery, replies to an active child
when needed, and calls `set_thread_archived` only when no child action remains.
The child never archives itself.

## Thread Title

Use `<emoji> <manager>-<scope>[-<relation>-<dependency>]`. Keep one lowercase
hyphen slug, one primary dependency, and about 55 characters. The CLI enforces
the exact shape and manager list.

Examples:

```text
💻 dev-browser-kit-after-profile
🧪 qa-payment-webhook-blocks-release
🌐 browser-valuelist-download-after-login
📝 docs-api-contract
```
