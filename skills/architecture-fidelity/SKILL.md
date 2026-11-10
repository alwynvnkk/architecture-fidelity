---
name: architecture-fidelity
description: Preserve architectural coherence during implementation and review. Use for changes to responsibilities, domain types or closed states, variants, runtime dependencies, orchestration, persistence, dependency boundaries, or shared policy; possible repeated validation, mapping, error handling or call sequences; and fixes that resist two attempts or need special cases in shared code. Skip mechanical and documentation-only edits.
---

# Architecture Fidelity

Keep one owner for each invariant, preserve established boundaries, and add abstractions only when current requirements justify them. Keep the user's scope fixed; a review-only request authorizes no repository or ledger edits.

## Choose the path

Inspect the request, changed paths, and diff summary. Run once during planning when a trigger is evident, otherwise once against the final diff. Repeat only if the architectural scope materially expands.

- **Mechanical work:** formatting, generated output, docs, copy, styles, lockfile/version updates, and mechanical renames need no architecture pass.
- **Local code fix:** use the nearest existing analogue, perform the repetition sweep and bounded simplification pass below, and run relevant checks on the final change. No architecture report is needed unless it reveals a concern.
- **Architectural change or explicit review:** follow the workflow below.

Load references only when their condition applies. Do not read the whole reference directory.

Before adding a conversion, fallback, or special case to compensate for an incorrect input, trace where that input is produced and check the receiving contract. Prefer correcting an owned producer when compatibility permits. Read [Correct the producer](references/design-decisions.md#correct-the-producer) when deciding whether downstream adaptation is justified. Apply this check to local fixes too.

## Workflow

1. **Establish scope and memory.** Identify the requested behavior, affected owners, and compatibility constraints. In GitHub Copilot, use the [personal journal workflow](references/project-ledger.md#github-copilot) for all ledger access. On other clients, if `.architecture-fidelity/ledger.json` exists, read [project-ledger.md](references/project-ledger.md), validate it, and plan from its baseline. Expand changed paths to owners, callers, consumers, registration points, tests, and the nearest analogue; cached claims need current evidence where touched.
2. **Choose the smallest coherent design.** Search by responsibility before adding a construct. Prefer reuse, then extension at an existing seam, then generalization of a proven shared contract. Ask whether the addition needs to exist at all. Preserve dependency direction, substitutability, public APIs, and serialized values. For a material ownership/type/design choice, or a fix resisting two attempts or adding a special case in shared code, read [design-decisions.md](references/design-decisions.md).
3. **Implement or review.** Keep policy with its owner and update all in-scope callers. Before moving or reshaping existing behavior, read [safe-refactor.md](references/safe-refactor.md). For an explicit review or audit, read [review-rubric.md](references/review-rubric.md) and report evidence-backed findings without editing.
4. **Sweep for repetition.** Whenever code changes, including local fixes, search the repository using three to five distinctive tokens from the change. Include tests; exclude generated, vendored, and snapshot copies. Read hits and count semantic occurrences: examine two; at three, centralize or explicitly record why duplication remains. Shared syntax alone does not justify coupling. Use [duplication-sweep.md](references/duplication-sweep.md) when selecting tokens or interpreting ambiguous hits. This is a bounded heuristic, not proof that duplication is absent.
5. **Attempt simplification.** After the solution works, make a bounded simplification pass over the change. Ask whether the same supported behavior can be expressed clearly with less code by reusing existing capabilities, removing redundant decisions or state, and deleting machinery made unnecessary by the final design. Ask what this change makes unnecessary, including earlier workarounds, and verify callers before removal. Consider the total implementation across affected callers and helpers. Prefer reductions that also reduce concepts, branches, or maintenance points. Preserve readability, explicit contracts, and verification. Retain the current design when further reduction would obscure intent or couple unrelated responsibilities. Line count is supporting evidence, with no reduction quota. Keep the pass within the requested scope.
6. **Verify and report.** Run relevant tests, type checks, and linters against the final change, including any simplification. Test shared contracts and invalid states; cover delivery/concurrency/lifecycle failure modes where affected. If a new boundary has existing violations, enforce a shrinking allowlist rather than silently grandfathering them. Inspect the final diff for parallel owners, bypassed seams, unused constructs, and compatibility drift.

## Conditional detail

- Choosing a pattern, inheritance, composition, or interface: [pattern-selection.md](references/pattern-selection.md).
- Choosing Python domain types, enums, protocols, or value objects: [python.md](references/python.md).
- Reading or updating architectural memory, including an authorized first seed: [project-ledger.md](references/project-ledger.md). A partial seed must not establish a complete baseline. Do not inventory the repository just to populate memory.

## Handoff

Lead reviews with findings ordered by severity, evidence, consequence, and smallest correction; distinguish new findings from carried or stale ledger claims. State verification gaps.

For implementation, report material reuse, introduced concepts and their evidence, preserved boundaries, and deliberate deferrals. Include one line saying what the repetition sweep searched and found, even when clean. Mention any ledger creation or update. Omit empty categories and routine design narration.
