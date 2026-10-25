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
- refactors two or more implementations of one concept;
- writes validation, mapping, error handling, state transitions, or a call sequence that may already exist elsewhere;
- follows a fix that has resisted two or more attempts;
- needs a new flag, parameter, mode, or special case inside shared code.

Run it once during planning when that is evident from the request. Otherwise run
it once against the final diff before handoff or pull request preparation.

## Take the fast path when the change is

formatting, linting, generated output, documentation, copy, styles, lockfile- or
version-only updates, a mechanical rename, or an isolated fix that introduces no
concept, crosses no boundary, and repeats nothing already in the repository.

On the fast path, do not produce an architecture report. Find the nearest
analogue, match it, test it, and stop — where matching means calling or
extending it, since copying its body is how a second instance becomes a third.

## The repetition sweep is not gated

Whenever code was added or changed, including on the fast path, run the sweep
from the skill's workflow step 5 before handoff: pick three to five distinctive
tokens from what was written — a literal error string, a literal key, two
identifiers that co-occur, a short call sequence — and search the whole
repository for each. Then apply the skill's occurrence count: ignore one,
examine two, and do not leave three unaddressed or unrecorded.

Whether a change repeats something cannot be judged from the request or the
changed-file names, because it depends on what the rest of the repository
already contains. Gating that check on the significance decision is how a third
and fourth copy arrive while every individual pass is correctly classified as
insignificant. The sweep is bounded to a few searches, so report its outcome in
one line even when it is clean.

## Gate notes

- Diff size does not decide. A one-line state transition can qualify; a large generated diff may not.
- An upcoming pull request is not by itself a trigger.
- Do not re-run per edit, commit, or test run. Re-run only if scope materially expands into another responsibility or boundary after a prior pass.

## When the gate passes

Read `.github/skills/architecture-fidelity/SKILL.md` and follow it end to end,
including the reference files it links for pattern selection, Python specifics,
the review rubric, the duplication sweep, safe structural moves, and project
memory. Report the architectural decisions it asks for rather than only the
behavior change.
