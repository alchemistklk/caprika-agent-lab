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

Record child id, title, issue, target, callback mode, commit owner, and parent
thread id. Let Codex auto-name once, validate the final title with the CLI, then
call `set_thread_title`. Reapply once only if the first child response overwrites
it.

### 5. Resolve runtime capability

The child resolves and pins the callback target once, at initial task startup:

1. the initial `create_thread` delegation source id:
   `codex_delegation.source_thread_id`, `codexDelegation.sourceThreadId`, or
   `<source_thread_id>` from the original task message;
2. explicit parent id in the brief;
3. manual forwarding.

Never use the child's own thread id as the parent. Threads created with
`create_thread` default to automatic callback even without an explicit parent id.
Persist the resolved id as the pinned callback target for the task lifetime.
Later `send_message_to_thread` prompts are steering messages, not new parent
delegations: their `source_thread_id` must never replace the pinned target. If
the original route cannot be recovered after a resume, stop guessing and emit a
manual callback with the routing uncertainty.

Resolve Git capability from the child's `permission_profile`. An explicit
read-only `.git` entry wins over filesystem permissions. Do not create a probe
lock solely to test access. If Git is read-only, transfer commit Delivery to the
parent or user and continue implementation.

### 6. Notify on validation trouble, then execute and classify

Do not reopen settled planning. Preserve unrelated changes and validate before
closeout.

On the first failure of a required full gate, do not silently continue. Before
the next broad rerun or a material repair, inspect the exact failures and send
one `checkpoint` callback to the parent. The checkpoint must state:

- the failing command and exact failed criteria;
- whether each failure is `introduced-regression`, `baseline-existing`, or
  `unknown`; do not call a failure baseline-existing without evidence;
- the child’s next action and whether a parent decision is needed.

Use `Execution: in-progress`, `Validation: failed | partial`,
`Delivery: pending`, and `Archive: keep-active`. A checkpoint is nonblocking:
the child continues safe, in-scope diagnosis and repair after it is delivered.
The callback input must carry `failure_classification` and `failure_evidence`;
the validator rejects a failed checkpoint that marks the classification
`not-applicable`.
Send at most one checkpoint per validation cycle; send another only when the
classification materially changes or a parent decision is newly required.

If repair cannot continue, validation cannot be made to pass, access is needed,
or scope must change, send a closeout callback before ending the turn. Do not
wait for the parent to infer a problem from task silence.

- `done`: implementation and acceptance are complete. Parent-owned commit,
  review, merge, or archive remains Delivery, not a blocker.
- `blocked`: implementation or required validation cannot continue.
- `scope-change`: continuing requires materially different approved scope.

Commit/merge failure is `blocked` only when it is an explicit acceptance
criterion owned by the child. The callback CLI rejects contradictory status
combinations.

### 7. Render and deliver lifecycle callbacks

At closeout, inspect the callback input schema only when needed:

```bash
with-env scripts/issue-thread callback --example
with-env scripts/issue-thread callback --example checkpoint
```

Pass completed JSON to `issue-thread callback`; use its stdout as the callback.
Use `callback_kind: checkpoint` for an in-progress validation alert and
`callback_kind: closeout` for `done`, `blocked`, or `scope-change`.
For automatic delivery, include `callback_target_origin:
initial-delegation | explicit-brief`; the validator rejects an automatic callback
whose parent route is unresolved.

In automatic mode, call `send_message_to_thread` for each required lifecycle
event with the pinned parent id and
`{ threadId: parent_thread_id, prompt: callback }`. On success, do not repeat the
same event. If target discovery or sending fails, render one manual callback
with the exact reason before ending the turn.

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
