# Skills

Small, installable skills for repeatable agent workflows. Each package keeps
its instructions, templates, and any deterministic helper scripts together.

These skills complement native Codex task tools. They do not reimplement task
creation, messaging, naming, or archiving when Codex already owns those
capabilities.

## Included

- [`issue-to-thread`](issue-to-thread/): turns one approved tracker issue into
  a clean execution task with a validated brief, callback, and delivery
  contract.

## Install

Copy or symlink a package into your Codex skills directory. For example:

```bash
ln -s "$(pwd)/skills/issue-to-thread" ~/.codex/skills/issue-to-thread
```

Restart or refresh Codex after installing. Read the package's `SKILL.md` before
use; its helper commands are intentionally limited to deterministic validation
and rendering.
