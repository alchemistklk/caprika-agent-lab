# Caprika Agent Lab

Small, runnable AI product patterns from agent work.

This repository is a public lab for documenting how an idea becomes a usable AI
product capability: tools, files, models, reviews, recovery paths, and final
artifacts.

It is not a collection of prompts. It is a collection of workflows that can be
inspected, repeated, improved, and eventually turned into product surfaces.

## Focus

- Tool-integrated agents with clear permission, schema, and error boundaries.
- Local-first runtimes that work with files, CLIs, desktop sidecars, and real
  project folders.
- Multimodal workflows for images, video, audio, documents, previews, and
  exports.
- Content workflows that move from source material to reviewed, publishable
  artifacts.
- Agent UX patterns for progress, cancellation, retry, recovery, and human
  control.

## Repository Shape

| Directory | Purpose |
|---|---|
| `labs/` | Small runnable experiments and minimal product slices. |
| `patterns/` | Reusable engineering and product patterns extracted from labs. |
| `case-notes/` | Evidence-backed notes about public or approved work. |
| `content-workflows/` | Content-generation workflows, production notes, and publishable writeups. |
| `skills/` | Installable agent skills with bounded, inspectable automation contracts. |
| `templates/` | Reusable formats for adding new labs, case studies, and workflow notes. |
| `assets/` | Images, diagrams, screenshots, and other public-safe supporting assets. |

## What Belongs Here

Each entry should show at least one of these:

- A real workflow boundary: inputs, tools, model calls, files, outputs, and
  review points.
- A product capability: something a user can run, inspect, recover from, or
  reuse.
- A technical pattern: an implementation detail that makes agent behavior more
  reliable, controllable, or understandable.
- A content production path: how source material becomes a reviewed public
  artifact.

## What Does Not Belong Here

- Private project names, private customer details, credentials, unreleased
  business logic, or sensitive operational context.
- One-off screenshots without the workflow behind them.
- Prompt-only notes that cannot be connected to a repeatable process.

## Starting Map

Planned areas:

- `tool-boundaries`: adapters, schemas, auth, retries, and failure handling.
- `multimodal-artifacts`: files, images, audio, video, previews, and exports.
- `content-production`: source evidence, drafting, review, publishing, and
  readback.
- `local-agent-runtime`: CLIs, daemons, filesystem state, and desktop bridges.
- `agent-ux`: visible state, human control, cancellation, retry, and recovery.
- `issue-to-thread`: approved Issue to clean executor task, callback, and delivery lifecycle.

## Entry Template

Use the templates in `templates/` when adding new material:

- `templates/lab.md` for runnable experiments.
- `templates/pattern.md` for reusable engineering patterns.
- `templates/case-note.md` for public-safe project evidence.

## License

MIT for repository code and written patterns unless a subdirectory states
otherwise.
