---
applyTo: "**"
description: "Route architectural work to the shared skill; keep mechanical edits cheap."
---

# Architecture Fidelity routing

Canonical workflow: `.github/skills/architecture-fidelity/SKILL.md`.

Use it for implementation or review that changes responsibilities, domain types
or closed states, variants, runtime dependencies, orchestration, persistence,
dependency boundaries, shared policy, or multiple implementations. Also use it
for potentially repeated validation, mapping, error handling, transitions or call
sequences; fixes resisting two attempts; and new flags, parameters or special
cases inside shared code.

Invoke once during planning when evident, otherwise against the final diff.
Repeat only if architectural scope materially expands. A PR, edit, commit, test
run, or diff size alone is not a trigger.

Formatting, generated output, docs, copy, styles, lockfile/version updates, and
mechanical renames need no architecture pass. For a local code fix, use the
nearest analogue and relevant checks. Whenever code changes, including local
fixes, follow the entrypoint's bounded repetition sweep before handoff; repetition
cannot be decided from file names alone.

Read the entrypoint when needed and load only references whose conditions apply.
Do not preload every reference. Follow its reporting and ledger authorization
rules; review-only work writes no repository files.
