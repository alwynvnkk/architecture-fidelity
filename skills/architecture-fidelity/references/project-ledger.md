# Project Architecture Ledger

Read when `.architecture-fidelity/ledger.json` exists, the user requests architectural memory, or an authorized implementation should seed it. It is a cache of claims; current code, tests, and repository documentation override it.

A review-only request authorizes no ledger writes. Report a proposed delta instead. For authorized implementation, create or update only load-bearing memory already established by the pass; mention it in the handoff.

## Helper

Locate the packaged script relative to this skill:

```bash
python3 <skill-directory>/scripts/architecture_ledger.py --root <repository> plan
```

| Command | Purpose |
| --- | --- |
| `init` | Optional empty ledger creation; refuses to overwrite. |
| `validate` | Check the ledger before relying on it and after edits. |
| `plan` | Compare the completed baseline to HEAD plus tracked/untracked working changes; select changed anchors and carry untouched open findings. |
| `fingerprint` | Compute identity from category, invariant, and path/symbol anchors. |
| `apply-delta --delta <file>` | Atomically merge authorized updates, creating the ledger if absent; retain identities, finding events, and the latest 20 audit records. |

Read [ledger-format.md](ledger-format.md) only when authoring or inspecting JSON. Run the helper without reading its implementation unless debugging it. If unavailable, follow the same format and rules manually.

## First seed and coverage

Seed from what the current pass established; do not start a repository inventory to fill memory. Include canonical owners, enforced boundaries, extension seams, closed vocabularies, and findings that are high severity or span modules. Omit mechanical rules, obvious local facts, low/opportunity findings, and approved analogues on a first seed. Aim for roughly ten landmarks and ten findings at most; create nothing if none qualify.

**A targeted first seed uses `audit.mode: "full"` with `audit.complete: false`.** List the inspected surfaces in `scope`. Findings and landmarks persist, but no completed baseline is established; `plan` continues to require a full audit. A missing baseline is not permission to expand an implementation task into a full audit.

Set `complete: true` only after the entire full-audit scope, or the entire planned incremental scope and its architectural blast radius, has been assessed. Always specify the flag in new deltas. For compatibility, omitted flags default to true for full mode and false for incremental mode.

Only a complete pass advances the baseline; every pass enters history. Advancing after a targeted review would hide unexamined changes before that commit from future plans.

## Subsequent audits

1. Validate and run `plan`. If the baseline is absent or unavailable, a complete audit requires a full scan; never guess a diff range. A scoped task may still record a partial pass.
2. Inspect changed surfaces and their owners, callers, consumers, registration points, tests, and nearest analogue. Git paths are the starting set, not the entire blast radius.
3. Revalidate selected landmarks and findings. Missing or moved anchors require investigation, not automatic resolution.
4. Carry untouched open, accepted, planned, and reopened findings without calling them new. Check touched resolved/dismissed findings for regression.
5. Report new, changed, carried, resolved, reopened, accepted/dismissed, and stale claims as applicable.

A full audit is appropriate when requested, history was rewritten, the ledger is invalid, or dependencies changed broadly. Do not invent a fixed audit cadence.

## Identity and lifecycle

Fingerprints use normalized category and invariant plus sorted repository-relative path/symbol anchors. Avoid line numbers. A materially different invariant or ownership needs a new identity; summary, impact, correction, and severity can change without one. Keep fingerprinted fields stable for evidence updates.

Statuses: `open` is actionable; `accepted` records why a concern remains; `planned` names remediation; `resolved` requires verified correction; `dismissed` requires evidence the concern is invalid; `reopened` records regression. Every transition needs a reason, time, assessed commit when available, and a matching lifecycle event. Retain resolved/dismissed records.

### Repetition findings

Anchor the stable concept: the intended owner location plus the first occurrence. Put the full changing occurrence list and count in `impact`; adding every occurrence to fingerprinted anchors would fork identity as the count rises.

On a count increase, update impact/severity and supply `evidence_reason`; the helper appends an event without requiring a status change. Use `transition_reason` for actual status changes. See [ledger-format.md](ledger-format.md) for the delta contract.

`plan` cannot detect new instances in unanchored files: the repetition sweep finds them. Resolve only after verifying centralization and naming removed instances; accepted duplication records distinct owners or reasons to change.
