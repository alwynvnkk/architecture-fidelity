# Architecture Review Rubric

Use this reference for explicit code reviews, architecture audits, or design assessments. Review-only requests do not authorize edits.

## Evidence standard

Report a finding only when it has:

- a concrete location and affected responsibility;
- evidence from definitions plus callers, tests, or an analogous path;
- a credible maintenance, correctness, compatibility, or extension cost;
- the smallest viable direction for correction.

Do not report a pattern preference without a demonstrated consequence. Distinguish confirmed defects from forward-looking opportunities.

## Review order

1. **Competing implementations:** two sources of truth, bypassed orchestrators, duplicated policy, or new paths that overlap existing ones.
2. **Broken boundaries:** inward dependencies on frameworks/vendors, misplaced ownership, cross-layer state mutation, or dependency cycles.
3. **Invalid domain states:** raw literals, boolean combinations, primitive clusters, or unvalidated mappings that should be one typed concept.
4. **Unmodeled variation:** growing switches, flags, or copy-pasted flows where a proven extension seam exists.
5. **Unsound abstraction:** inheritance without substitution, broad interfaces, optional base methods, utility dumping grounds, or speculative frameworks.
6. **Contract drift:** incompatible public, serialized, schema, configuration, error, or lifecycle changes.
7. **Test architecture:** variants without shared contract tests, invariants tested only through UI/transport, or wiring with no integration coverage.
8. **Unnecessary surface area:** new files, dependencies, wrappers, or concepts that an existing construct can absorb.

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
