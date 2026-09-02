---
applyTo: "**"
description: "Route meaningful code changes through the Architecture Fidelity skill and keep mechanical edits on the fast path."
---

# Architecture Fidelity routing

This file is a router, not the skill. The canonical rules live in
`.github/skills/architecture-fidelity/SKILL.md`.

Apply this significance gate before implementing or reviewing a change. It is
deliberately cheap: read the request, the changed-file names, and the diff
summary, then decide.

## Run the skill when the task or its diff

- adds or changes a production module, service, domain type, closed option or state, or variant;
- adds or replaces a runtime dependency;
- changes an orchestration or persistence flow;
- crosses a dependency boundary, or duplicates or moves shared policy;
- refactors two or more implementations of one concept.

Run it once during planning when that is evident from the request. Otherwise run
it once against the final diff before handoff or pull request preparation.

## Take the fast path when the change is

formatting, linting, generated output, documentation, copy, styles, lockfile- or
version-only updates, a mechanical rename, or an isolated fix that adds no
concept and moves no boundary.

On the fast path, find the nearest analogue, match it, test it, and stop. Do not
load the skill or produce an architecture report.

## Gate notes

- Diff size does not decide. A one-line state transition can qualify; a large generated diff may not.
- An upcoming pull request is not by itself a trigger.
- Do not re-run per edit, commit, or test run. Re-run only if scope materially expands into another responsibility or boundary after a prior pass.

## When the gate passes

Read `.github/skills/architecture-fidelity/SKILL.md` and follow it end to end,
including the reference files it links for pattern selection, Python specifics,
the review rubric, and project memory. Report the architectural decisions it
asks for rather than only the behavior change.
