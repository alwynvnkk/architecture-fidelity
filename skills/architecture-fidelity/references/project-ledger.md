# Project Architecture Ledger

Use this reference when a repository contains `.architecture-fidelity/ledger.json`, when the user asks to initialize architectural memory, or when an audit should update finding state over time.

The ledger is a committed, reviewable cache of architectural claims. Source code, tests, and current repository documentation remain authoritative. Never suppress a finding solely because a similar title exists in the ledger.

## What the ledger remembers

It carries two kinds of memory:

- **Landmarks:** healthy facts worth reusing, including canonical owners, dependency rules, extension seams, closed domain vocabularies, and approved analogous implementations.
- **Findings:** evidence-backed architectural concerns with stable identity, anchors, status, and lifecycle history.

Use repository-relative paths and symbols as anchors. Include every location needed to identify a multi-owner finding, not only the file where it was first noticed. Do not use line numbers: they are unstable and create false churn. Do not store secrets, credentials, personal data, or large code excerpts.

## Helper

When the packaged script is available, locate it relative to this skill and run:

```bash
python3 <skill-directory>/scripts/architecture_ledger.py --root <repository> plan
```

The commands are:

- `init`: create an empty `.architecture-fidelity/ledger.json` explicitly. This is optional: `apply-delta` creates the ledger when it is absent.
- `validate`: validate the current ledger before relying on it and after changing it.
- `plan`: compare the last completed audit commit with `HEAD` plus tracked and untracked working-tree changes. It lists the landmarks to consult, identifies anchored landmarks and findings that need revalidation, and carries forward untouched open findings.
- `fingerprint`: create a stable SHA-256 identity from a category, invariant, and repository path/symbol anchors.
- `apply-delta`: atomically merge an authorized audit delta, creating the ledger when absent, preserving finding identity and lifecycle events, and retaining the most recent 20 audit history entries. It prints `created:` or `updated:` so the first scan is visible in the handoff.

If Python or the helper is unavailable, follow the same rules manually. Do not make helper availability a prerequisite for the architectural work.

## First scan

When repository edits are authorized and no ledger exists, seed one from the pass you just performed. Do not start a repository-wide inventory to fill it: the first ledger records what this scan already established, and later scans extend it.

Seed only load-bearing architecture. The test for every entry is whether a future change could plausibly violate it and whether that would be expensive to discover again. If an entry fails either half, leave it out.

Record:

- the canonical owner of a domain concept that has more than one plausible home;
- a dependency rule or boundary the repository actually enforces;
- an extension seam a future variant is expected to use;
- a closed domain vocabulary whose values must stay in step with serialization;
- a finding of `high` severity, or one whose invariant spans more than one module.

Leave out:

- anything a formatter, linter, or type checker already enforces;
- local duplication, naming preferences, and single-file cleanups;
- `low` and `opportunity` findings, and `approved-analogue` landmarks, on a first scan;
- restatements of what a single file makes obvious on sight.

Keep the first delta to roughly ten landmarks and ten findings. If more seem to qualify, the bar is being applied too loosely; record the boundaries that explain the rest and let later scans add specifics with evidence. A first ledger that fits on one screen is working as intended.

Write the seed through `apply-delta` with `audit.mode` set to `full` and `audit.scope` listing the surfaces actually inspected. When the helper is unavailable, write the same structure by hand: the helper is not a prerequisite for creating the ledger, only the more reliable way to keep finding identity and lifecycle correct. Mention in the handoff that project memory now exists and where it lives.

## Incremental audit

1. Validate the ledger and read the output of `plan`.
2. If the baseline is missing or unavailable, perform a full audit. Never guess a diff range.
3. Inspect changed and added surfaces against the remembered landmarks. Expand beyond changed files to their owners, direct callers, downstream consumers, registration points, tests, and the nearest analogue. Git paths are a starting set, not the complete architectural blast radius.
4. Revalidate every landmark and finding selected by the plan. A moved or missing anchor is stale and requires investigation; it is not proof of resolution.
5. Carry unchanged open, accepted, planned, and reopened findings without presenting them as newly discovered.
6. Check changed surfaces for genuinely new findings and for regressions of resolved findings.
7. Report the delta as: new, changed, still open, resolved, reopened, dismissed or accepted, and needs revalidation.

Run a full audit when there is no usable baseline, the dependency structure changed broadly, repository history was rewritten, the ledger is invalid, or the user explicitly requests one. Periodic full audits are sensible, but do not invent a fixed cadence without repository evidence.

## Finding identity and lifecycle

A fingerprint consists of the normalized category, invariant, and sorted path/symbol anchors. Materially different ownership, invariant, or anchors require a new identity.

Severity, and the wording of `summary`, `impact` and `correction`, may change freely on an existing finding — that is how a sharpened or re-evidenced finding stays one record. The `invariant` text is **not** free wording: it is fingerprinted, so rephrasing it is refused as an attempted identity change. Sharpen the summary instead, and reserve a new `invariant` for a genuinely different rule.

Supported statuses:

- `open`: actionable and unresolved;
- `accepted`: explicitly accepted with a recorded reason;
- `planned`: linked to concrete remediation work;
- `resolved`: correction verified in the code;
- `dismissed`: evidence showed the finding was invalid or no longer applicable;
- `reopened`: a resolved or dismissed invariant regressed.

Every status change needs current evidence, a reason, a timestamp, and the commit assessed when available. Non-open states must have a matching lifecycle event. Retain resolved and dismissed records so later regressions can be recognized. Do not treat absence, renamed files, or title similarity as resolution.

### Repetition findings

A repeated shape is the finding most worth carrying between sessions, because each individual encounter looks minor and the cost is only visible in the count. It needs care, because the obvious encoding defeats itself.

Anchor a repetition finding on **the concept**, not on every occurrence: the location where the shared owner belongs, plus the first occurrence. Record the full occurrence list in `impact`, with a count.

The reason is the identity rule above. A fingerprint includes the sorted anchors, so anchoring every occurrence means a fifth instance mints a new finding and the count silently restarts at one — the exact failure the finding exists to record. A count that lives in `impact` is wording, which may change freely while the identity holds, so the finding accumulates instead of forking.

This splits the work deliberately: the repetition sweep in the skill's workflow **detects** occurrences, and the ledger **remembers** the running total and what was decided. Do not rely on `plan` to resurface a repetition finding when a new instance lands in an unanchored file; it will not see it, and the sweep is what catches it.

When the count rises, update `impact` and, where warranted, `severity`, and add a lifecycle event recording the new total. When the shape is finally centralized, resolve it against the commit that did so, naming the occurrences removed. An `accepted` repetition finding states why the instances stay apart — different owners, divergent reasons to change — so the next pass does not reopen a decision that was already made with evidence.

## Ledger shape

The repository file has this top-level structure:

```json
{
  "schema_version": 1,
  "project": {"name": "example"},
  "audit": {
    "last_complete_commit": null,
    "completed_at": null
  },
  "landmarks": [],
  "findings": [],
  "history": []
}
```

A landmark contains `id`, `kind`, `statement`, one or more `anchors`, `first_seen_commit`, and `last_verified_commit`. Allowed kinds are `canonical-owner`, `dependency-rule`, `extension-seam`, `domain-vocabulary`, and `approved-analogue`.

A finding contains:

```json
{
  "id": "AF-0001",
  "fingerprint": "<sha256>",
  "status": "open",
  "severity": "high",
  "category": "competing-implementation",
  "summary": "Two routes own the same mutation policy",
  "invariant": "A domain mutation has one canonical owner",
  "impact": "Validation and audit behavior can diverge",
  "correction": "Route both callers through the canonical service",
  "owner": null,
  "external_ref": null,
  "anchors": [
    {"path": "src/domain/service.py", "symbol": "save_entry"}
  ],
  "first_seen_commit": "<git commit>",
  "last_verified_commit": "<git commit>",
  "events": []
}
```

An audit delta accepted by `apply-delta` contains a required `audit` object and optional landmark and finding upserts:

```json
{
  "completed_at": "2026-08-30T12:00:00Z",
  "audit": {
    "mode": "incremental",
    "complete": false,
    "base_commit": "<previous commit>",
    "commit": "<assessed commit>",
    "scope": ["src/domain/service.py"]
  },
  "landmarks": [],
  "findings": []
}
```

For a new finding, `id` and `fingerprint` may be omitted from a delta; the helper allocates them. For an existing finding, identify it by `id` or fingerprint. Include `transition_reason` when changing status. The helper preserves `first_seen_commit` and appends a lifecycle event.

### `complete` governs the baseline

`audit.complete` says whether this pass covered its whole planned scope. Only a complete pass moves `audit.last_complete_commit`; every pass is recorded in `history` either way.

This matters because `plan` computes the next scope as `last_complete_commit..HEAD`. A pass that examined three files and then advanced the baseline makes everything else changed before that commit permanently invisible to later audits — the ledger would report healthy incremental coverage while silently narrowing it. The flag exists so that cannot happen by accident.

Omitted, it defaults to `true` for `mode: "full"` and `false` for `mode: "incremental"`. So a full scan behaves as before, and an incremental pass must assert coverage deliberately: set `"complete": true` when every path `plan` listed was examined, and leave it alone for a targeted pass such as a single-concern sweep or a review of one subsystem.

A targeted pass is still worth recording. Its findings, counts and scope all persist; only the claim about coverage is withheld.

## Authorization

A review-only request does not authorize repository edits, including creating the ledger. In that mode, report the proposed ledger delta in the response or write it only to a user-authorized output location. When repository edits are authorized, create the ledger on the first qualifying scan and keep an existing one current as part of the coherent change. Creating the ledger is a visible part of the change: mention it in the handoff so it can be reviewed or reverted like any other file.
