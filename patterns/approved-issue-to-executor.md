# Approved Issue To Executor

## Problem

Planning conversations accumulate context, alternatives, and decisions. An
implementation task needs only the settled contract. Passing the whole
conversation to an executor encourages it to re-plan, lose the real acceptance
criteria, and blur completion with parent-owned review or delivery.

## Pattern

Use a two-stage handoff:

1. Split an approved plan into independently verifiable vertical-slice issues.
   Review the granularity and dependencies before they are assigned.
2. Launch one clean executor task per approved issue with a bounded execution
   brief. The task reports one structured callback to its parent.

The execution brief contains the goal, acceptance criteria, validation,
out-of-scope boundary, callback target, and Git delivery contract. It contains
only prior decisions that materially affect execution.

## When To Use

- Use when work has a settled plan and can be split into independently
  verifiable slices.
- Use when a parent task needs to keep ownership of prioritization, review,
  commit, merge, or archive decisions.
- Avoid when the work is still exploratory or has unresolved product choices.

## Implementation Shape

- Planning: `to-issues` produces reviewed vertical-slice issues in dependency
  order.
- Handoff: `issue-to-thread` validates a brief and creates a clean executor
  through native task tooling.
- Execution: the child implements only the approved issue and does not reopen
  settled planning.
- Callback: the child reports execution, validation, delivery, Git capability,
  acceptance, and archive state separately.
- Delivery: the parent owns any remaining commit, review, merge, or archive
  action.

## Example

An executor can complete implementation and required tests inside a sandbox
that makes `.git` read-only. Its callback is still `done` with
`parent-action-required`, rather than incorrectly reporting `blocked`.

## Tradeoffs

This pattern adds a short briefing step and requires disciplined issue quality.
In return, it makes execution repeatable, limits context drift, and exposes the
difference between implementation completion and final delivery.
