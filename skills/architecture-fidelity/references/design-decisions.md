# Design Decisions

Read for a material change to ownership, domain modeling, or shared behavior, or when a difficult fix suggests misplaced responsibility. Use the repository's conventions unless an explicit invariant requires changing them.

## Earn the addition

Before choosing a design, ask whether the construct needs to exist. Remove speculative parameters, unused hooks, unread fields, forwarding wrappers without a boundary or invariant, handling for excluded states, and configuration nothing currently changes. A single-implementation interface needs a concrete boundary or test seam to justify it. Prefer a standard-library or installed-library operation to a hand-rolled equivalent.

Search for the responsibility as well as the proposed name. Inspect the definition, direct callers, tests, and an analogous flow. Reuse unchanged where possible; extend at an existing seam before adding a competing path.

## Establish ownership and variation

An abstraction needs current evidence: a shared invariant and reason to change, an established extension seam, a closed variation axis, or coordinated caller edits that belong behind one boundary. Similar syntax alone is insufficient. Centralize validation, mappings, state transitions, error semantics, and lifecycle policy only when they enforce the same rule.

At two semantic occurrences, name the shared concept and decide whether reuse is justified. At three, either centralize or record the count and reason for keeping them separate. Counts describe evidence; they do not override different owners or reasons to change. If correction exceeds the task, record a finding rather than widening scope.

Read [pattern-selection.md](pattern-selection.md) when selecting the mechanism. Preserve substitutability: callers should not branch on subtype to use a promised contract. Prefer composition for independently varying behavior. Keep core policy independent of frameworks, transports, persistence, and vendor clients unless the repository explicitly chooses another boundary. Keep orchestration on the established lifecycle path.

## Make invalid states explicit

Use the language's enum or equivalent for repeated, closed domain choices; keep arbitrary user and third-party data open. Group primitive values into a value object when they form one validated concept. Distinguish IDs, units, states, and commands where mixing them causes boundary mistakes.

Validate and translate external values at the boundary. Preserve stored and serialized values during centralization, update in-scope callers, and avoid leaving two authoritative mappings. Read [python.md](python.md) for a Python type choice.

## Reconsider a difficult fix

Revisit ownership when a second attempt fails, a new flag or special case appears in shared code, one behavior needs four or more coordinated file edits, a value passes through layers that do not use it, or several callers repeat the same guard. Elaborate test setup can also expose a missing seam.

Identify what would make the invalid state impossible: one invariant owner, an expressive type, or an existing seam one layer up. Choose deliberately between that change and a local fix; restructuring may exceed scope. Record the evidence and reason for a material deferral.

## Make the rule enforceable

Test at the owning boundary: shared contracts for interchangeable variants, invalid states for domain types, and wiring for orchestration. For delivery, concurrency, or lifecycle changes, cover relevant duplicate delivery, concurrent claims, out-of-order events, cancellation, restart, and failure on either side of an external effect.

When introducing a rule after violations already exist, enumerate known violations in a test and prevent additions while allowing removals. A shrinking allowlist makes progress measurable without a repository-wide cleanup. Before a structural move, follow [safe-refactor.md](safe-refactor.md).
