---
name: architecture-fidelity
description: Preserve architectural coherence for meaningful code changes and architecture reviews. Invoke automatically when a task or resulting diff adds or changes a production module, service, domain type, closed option or state, variant, runtime dependency, orchestration or persistence flow; crosses a dependency boundary; duplicates or moves policy; or refactors multiple implementations. Use once during planning when evident, otherwise once before handoff if the diff reveals these signals. Skip formatting, linting, generated files, docs, copy, styles, lockfile- or version-only updates, mechanical renames, and isolated fixes that add no concept or boundary change.
---

# Architecture Fidelity

Maintain the codebase's established design while improving it where the requested change supplies concrete evidence. Architectural fidelity means coherent ownership, stable boundaries, expressive domain types, and low-cost extension. It does not mean maximizing inheritance, patterns, indirection, or theoretical purity.

## Invocation policy

Use this skill automatically when the request or emerging implementation meets a trigger in the description; human activation is not required.

- If the change clearly qualifies, invoke during planning so reconnaissance can shape the implementation.
- If qualification becomes clear only after editing, invoke once against the final diff before handoff or PR preparation.
- Do not invoke after every file edit, patch, commit, or test run. Re-run only when the scope materially expands into another responsibility or architectural boundary after the prior pass.
- Diff size is not the test. A one-line lifecycle or dependency change can qualify; a large generated, formatting, copy, or mechanical diff may not.
- The existence of code changes or an upcoming PR is not sufficient by itself. If another pass already covered the final scope, do not repeat it for ceremony.

Start with a cheap significance gate: inspect the requested behavior, changed-file names and diff summary, and the project ledger plan when one exists. If no trigger applies, use the fast path and stop without loading optional references or producing an architecture report. If a trigger applies, continue with the workflow below.

## Scope control

- Keep the user's requested outcome and authorization boundary fixed.
- Make the smallest coherent change, not merely the smallest diff.
- Do not turn a feature into a repository-wide cleanup. Fix adjacent structural debt only when the requested behavior would otherwise duplicate it, deepen it, or depend on it.
- Preserve local conventions unless they conflict with a clear domain invariant or established repository boundary.
- Let formatters, linters, and type checkers own mechanical rules. This skill owns design decisions those tools cannot infer.
- For a truly local edit with no new concept, dependency, variant, public behavior, or ownership change, use the fast path: find the nearest analogue, match it, test it, and stop.

## Project memory

Before broad reconnaissance, look for `.architecture-fidelity/ledger.json`. If it exists, read [references/project-ledger.md](references/project-ledger.md), validate the ledger, and use its Git baseline to plan an incremental audit. Treat landmarks and findings as cached claims: confirm anything touched by the current change, and let current code override stale memory.

Do not initialize a ledger during ordinary feature work unless the user asks. A review-only request does not authorize ledger writes; report a proposed delta instead. When an existing ledger is in scope for authorized implementation work, keep its relevant landmarks and findings current.

## Invariants

### Reuse before addition

Search before creating a file, type, helper, service, interface, option, configuration key, or dependency. Search by responsibility and behavior as well as by the proposed name. Inspect definitions, direct callers, tests, and at least one analogous flow.

Prefer, in order:

1. Use the existing construct unchanged.
2. Extend an existing construct at its intended seam.
3. Generalize an existing construct when the new case proves a stable shared contract.
4. Introduce a new construct only when ownership or semantics are genuinely distinct.

Do not force reuse between things that only look similar. Shared syntax is weaker evidence than a shared invariant and a shared reason to change.

### Model the domain explicitly

- Replace repeated, closed, meaningful string or numeric choices with the language's enum or equivalent domain type when repository compatibility permits.
- Replace primitive parameter clusters with value objects when the values form one validated concept.
- Distinguish identifiers, states, commands, events, and configuration from untyped primitives when that distinction prevents invalid states or boundary mistakes.
- Keep external serialization values stable. Convert and validate at boundaries rather than leaking wire-format strings throughout the core.
- Do not turn open-ended user data or third-party values into a closed enum.

For Python-specific choices such as `StrEnum`, `Protocol`, abstract base classes, and value objects, read [references/python.md](references/python.md) when Python is in scope.

### Abstract from change pressure

Create or reshape an abstraction only when at least one of these is true:

- two or more in-scope cases share a meaningful contract and reason to change;
- the repository already defines an extension point the new case belongs to;
- a domain invariant must be enforced in one place;
- current branching represents one explicit variation axis;
- callers currently coordinate changes that should be owned behind one boundary.

Name the contract in domain language. If it can only be named `helper`, `utils`, `manager`, `common`, or `base`, ownership is probably still unclear.

Read [references/pattern-selection.md](references/pattern-selection.md) when choosing among composition, inheritance, protocols/interfaces, strategies, factories, template methods, value objects, or plain functions.

### Preserve substitution and dependency direction

- Prefer composition for independent behavior variation and inheritance only for a stable substitutable relationship.
- A subtype must honor the parent's observable contract; do not require callers to branch on subtype to use it safely.
- Keep domain policy independent from frameworks, transports, persistence, and vendor clients unless the repository intentionally uses a different boundary.
- Put orchestration where the repository already owns the lifecycle. Do not bypass the central path with a parallel implementation.
- Depend on the narrowest stable capability, but do not add an interface that has no meaningful variation or testing value.

### Centralize invariants, not incidental code

Consolidate duplicated validation, state transitions, mapping rules, error semantics, and lifecycle behavior. Repeated one-line syntax may remain duplicated when extracting it would hide intent or couple unrelated modules.

When adding a variant, inspect the full family for:

- parallel conditionals or switches;
- repeated literals, keys, error shapes, and state names;
- constructors or factories that already select implementations;
- tests that encode a common contract;
- registries, adapters, strategies, handlers, or base types intended for extension.

### Keep contracts and migrations explicit

- Preserve public APIs, serialized values, persistence schemas, and configuration compatibility unless the task authorizes a break.
- When centralizing an existing concept, update all in-scope callers or provide an explicit compatibility path. Do not leave two competing sources of truth.
- Test at the abstraction boundary: shared contract tests for variants, invariant tests for value objects, and integration tests for wiring.
- Prefer deleting replaced paths over retaining dead wrappers, but verify callers before removal.

## Workflow

### 1. Establish the change pressure

Identify the requested behavior, likely variation axis, affected boundary, compatibility constraints, and what must remain unchanged. For a review-only request, do not edit files.

### 2. Reconnoiter the repository

Read repository instructions and architecture documentation. Use a valid project ledger to avoid rediscovering unchanged architecture, but expand every changed path to its architectural blast radius. Map the relevant package/module, then search for:

- the same domain nouns and verbs;
- analogous types and flows;
- creation and registration points;
- direct callers and downstream consumers;
- tests expressing current contracts;
- existing dependency direction and naming conventions.

Do not design from one file when the behavior crosses a boundary.

### 3. Make the design decision

Before editing, be able to state internally:

- what existing construct will be reused or extended;
- whether semantic duplication already exists;
- whether the new case strengthens an abstraction or is genuinely separate;
- why the selected mechanism matches the variation;
- which tempting abstraction is deliberately not being added.

If none of these decisions is material, use the fast path.

### 4. Implement the smallest coherent delta

Place behavior with its owner. Reuse the central path, consolidate in-scope duplicates, keep boundaries narrow, and avoid parallel frameworks. Add a new abstraction and its first specialization together only when the evidence above justifies it.

Do not add unused extension points for imagined future cases.

### 5. Verify behavior and structure

Run the repository's relevant tests, type checks, and linters. Then inspect the final diff and ask:

- Did this add a second way to do something the repository already does?
- Is any new string, flag, mapping, or state really a closed domain concept?
- Did a conditional grow because a polymorphic or table-driven seam already exists?
- Does every new type have one clear owner and reason to change?
- Did dependency direction remain intact?
- Could fewer concepts or less code express the same behavior more clearly?
- Are compatibility and shared-contract behavior tested?

### 6. Report architectural decisions

For implementation work, keep the handoff concise and include only material items:

- **Reused:** existing constructs or extension points used.
- **Introduced:** new abstractions or domain types and the evidence for them.
- **Preserved:** important boundaries or compatibility guarantees.
- **Deferred:** nearby architectural opportunities intentionally left out of scope.

Omit empty categories. For architecture audits or code reviews, read [references/review-rubric.md](references/review-rubric.md) and lead with evidence-backed findings. When a project ledger exists, distinguish new, changed, carried, resolved, reopened, and stale findings rather than presenting every open item as a fresh discovery.
