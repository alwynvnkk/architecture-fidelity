# Architecture Review Rubric

Use this reference for explicit code reviews, architecture audits, or design assessments. Review-only requests do not authorize edits.

If `.architecture-fidelity/ledger.json` exists, also read [project-ledger.md](project-ledger.md). Validate prior claims against the changed architectural blast radius and report the lifecycle delta; do not relabel carried findings as new.

## Evidence standard

Report a finding only when it has:

- a concrete location and affected responsibility;
- evidence from definitions plus callers, tests, or an analogous path;
- a credible maintenance, correctness, compatibility, or extension cost;
- a count wherever the cost is one of scale — occurrences, call sites, modules affected, readers and writers of the contested type — rather than an adjective;
- the smallest viable direction for correction.

Do not report a pattern preference without a demonstrated consequence. Distinguish confirmed defects from forward-looking opportunities.

A measured finding also survives disagreement. "Many modules write SQL directly" invites an argument about taste; "190 modules outside the persistence boundary hold 1,576 SQL statements, and the most-read table has 4 writers and 52 readers" states a cost. The same count later shows whether the correction is working.

## Review order

1. **Competing implementations:** two sources of truth, bypassed orchestrators, duplicated policy, or new paths that overlap existing ones. Search for the shapes the diff writes rather than judging from the diff alone — a third instance of a validation, mapping, or error sequence is this finding, and it is invisible without a search. State the occurrence count; three copies of one invariant that already disagree is a defect, not a preference.
2. **Broken boundaries:** inward dependencies on frameworks/vendors, misplaced ownership, cross-layer state mutation, or dependency cycles.
3. **Invalid domain states:** raw literals, boolean combinations, primitive clusters, or unvalidated mappings that should be one typed concept.
4. **Unmodeled variation:** growing switches, flags, or copy-pasted flows where a proven extension seam exists.
5. **Unsound abstraction:** inheritance without substitution, broad interfaces, optional base methods, utility dumping grounds, or speculative frameworks.
6. **Contract drift:** incompatible public, serialized, schema, configuration, error, or lifecycle changes. Also inspect downstream conversions or fallbacks that preserve an owned producer's contract violation. Cite the producer, receiving contract, and compensation, and check compatibility constraints before recommending a source correction. Follow [Correct the producer](design-decisions.md#correct-the-producer).
7. **Test architecture:** variants without shared contract tests, invariants tested only through UI/transport, or wiring with no integration coverage. Where the boundary carries delivery, concurrency, or lifecycle, also look for absent failure-mode coverage: duplicate delivery, concurrent claims, out-of-order events, cancellation races, restart recovery, and failure immediately either side of an external side effect. A rule that arrived after its violations and is enforced only by prose, rather than by a ratcheted list of the known ones, is a finding of this kind.
8. **Unnecessary surface area:** new files, dependencies, wrappers, or concepts that an existing construct can absorb — and code that should not exist at all: an unused parameter or extension point, an interface with one implementation, configuration for a value nothing changes, a forwarding wrapper that adds no invariant, handling for a state already excluded, or a generalization justified only by a future nobody has stated. Also the inverse: a hand-rolled implementation of what the standard library, framework, or an installed dependency already does.

## Severity

- **High:** creates or deepens a competing source of truth, violates a dependency boundary, breaks substitutability or compatibility, or permits invalid state in a core path.
- **Medium:** makes the next expected variant require coordinated edits, duplicates durable policy, or places responsibility with the wrong owner.
- **Low:** a bounded design inconsistency with real maintenance cost but no current behavioral risk.
- **Opportunity:** a plausible future improvement lacking enough present evidence for a finding. Keep these separate and sparse.

## Finding format

Lead with findings ordered by severity. For each, state:

1. the violated invariant in one sentence;
2. exact evidence and affected callers or flows;
3. why the current shape matters;
4. the smallest architectural correction.

Then list assumptions or unanswered questions. If there are no actionable findings, say so and mention any verification gap. Do not bury findings beneath a general summary.

For a ledger-backed audit, add the finding ID and lifecycle state. A stable finding may change wording or severity without receiving a new ID. Report unresolved findings outside the revalidated scope as carried, not reconfirmed.

## Design assessment questions

- What owns this behavior today, and does the proposal preserve that owner?
- Which existing path is extended rather than duplicated?
- What is the actual variation axis?
- Is the proposed abstraction based on a shared invariant and reason to change?
- Can every implementation honor the same contract without subtype checks?
- Are domain values closed or open, and is the type choice honest about that?
- Which public or serialized contracts must remain stable?
- Does the proposal reduce the number of places future changes must touch?
- What is deliberately not generalized yet, and why?
