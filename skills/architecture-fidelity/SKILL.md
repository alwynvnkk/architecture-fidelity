---
name: architecture-fidelity
description: Preserve architectural coherence for meaningful code changes and architecture reviews, and stop repeated shapes accumulating unnoticed. Invoke automatically when a task or resulting diff adds or changes a production module, service, domain type, closed option or state, variant, runtime dependency, orchestration or persistence flow; crosses a dependency boundary; duplicates or moves policy; or refactors multiple implementations. Also invoke when the change writes validation, mapping, error handling, state transitions, or a call sequence that may already exist elsewhere in the repository; when a fix has resisted two or more attempts; and when a fix needs a new flag, parameter, or special case inside shared code. Use once during planning when evident, otherwise once before handoff if the diff reveals these signals. Skip formatting, linting, generated files, docs, copy, styles, lockfile- or version-only updates, mechanical renames, and isolated fixes that introduce no concept, cross no boundary, and repeat nothing already present in the repository.
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

One exception: **the repetition sweep in workflow step 5 runs on the fast path too**, whenever code was added or changed. Repetition is the one trigger that cannot be evaluated from the request or the file names, because it depends on what the rest of the repository already contains. Gating the check on a judgment that requires the check's own answer is how a third and fourth instance arrive while every individual pass is correctly classified as insignificant.

## Scope control

- Keep the user's requested outcome and authorization boundary fixed.
- Make the smallest coherent change, not merely the smallest diff.
- Do not turn a feature into a repository-wide cleanup. Fix adjacent structural debt only when the requested behavior would otherwise duplicate it, deepen it, or depend on it.
- Preserve local conventions unless they conflict with a clear domain invariant or established repository boundary.
- Let formatters, linters, and type checkers own mechanical rules. This skill owns design decisions those tools cannot infer.
- For a truly local edit with no new concept, dependency, variant, public behavior, or ownership change, use the fast path: find the nearest analogue, match it, test it, and stop. Matching an analogue means calling it or extending it. Copying its body is not matching it — that is how a second instance becomes a third.

## Project memory

Before broad reconnaissance, look for `.architecture-fidelity/ledger.json`. If it exists, read [references/project-ledger.md](references/project-ledger.md), validate the ledger, and use its Git baseline to plan an incremental audit. Treat landmarks and findings as cached claims: confirm anything touched by the current change, and let current code override stale memory.

If no ledger exists, this pass cleared the significance gate, and repository edits are authorized, create one from what this pass already established. Seed only load-bearing architecture: canonical owners, enforced boundaries, extension seams, closed vocabularies, and findings that are high severity or span more than one module. Keep it to roughly ten landmarks and ten findings, and do not start a repository-wide inventory to fill it. If nothing clears that bar, do not create the file.

A review-only request does not authorize ledger writes, including creating it; report a proposed delta instead. When an existing ledger is in scope for authorized implementation work, keep its relevant landmarks and findings current, and say in the handoff when the ledger was created or changed.

## Invariants

### Earn every line

Before the reuse ladder, answer a prior question: does this need to exist at all? The fact that code *can* be written is not a reason to write it. Every line is a line someone later must read, test, migrate, and debug at an inconvenient hour, so each one has to pay for itself in behavior the request actually asked for.

Delete rather than add when the candidate is:

- a parameter, option, hook, or extension point with no current caller;
- an interface, factory, registry, or base class with one implementation and no second case in sight;
- configuration for a value that has never changed and nothing asks to change;
- a wrapper that forwards its arguments and adds no invariant, translation, or boundary;
- error handling for a state the type system or a prior guard already excludes;
- a generalization justified by a future requirement nobody has stated;
- a field, flag, or status that nothing reads.

"We will need it later" is not evidence. Later can add it, with the real requirement in hand and a real call site to shape it, and will do a better job than a guess made today. The cost of adding it then is one small change; the cost of carrying it meanwhile is paid on every read of the file.

This cuts both ways, and the opposite error is equally real: do not reinvent what the language, standard library, framework, or an installed dependency already does correctly. Spending thirty lines on what one call expresses is also failing to earn them.

Apply this before asking which shape the addition should take. A well-designed construct that should not exist is still waste.

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

### Count the occurrences: one, two, three

Repetition is the most reliable evidence an abstraction is warranted, and the easiest thing to miss while concentrating on something hard. Judgment cannot be trusted here, because the other instances are usually in files this task never opened. Counting can.

Count **semantic** occurrences of the shape, not textual matches, and include the one about to be written.

| Occurrences | What it means | What to do |
|---|---|---|
| **One** | Nothing. A single instance is just code. | Write it. Note nothing, record nothing. |
| **Two** | A possible pattern, or a coincidence. | Look deliberately. Name the shared concept. Then either reuse the first instance, or keep both and know why. |
| **Three** | A pattern. Not a suspicion. | Do not leave it unexamined. Either centralize it, or record the refusal and its reason. |

At two, the question is whether the instances share an invariant and a reason to change, or merely a shape. Deliberate duplication is a legitimate answer: two modules that happen to validate similarly but answer to different owners should stay apart, and coupling them would be the worse outcome. What is not legitimate is duplicating by *not having looked*.

At three, the skill's own abstraction test has its evidence — two or more cases sharing a meaningful contract and a reason to change. Proceeding without addressing it is the failure this skill exists to prevent. Addressing it does not always mean extracting: a third instance may still be genuinely separate, and saying so explicitly, with the reason, is a valid outcome. Silence is not.

Where the correction is larger than the current task should carry, do not abandon it to memory. Record it as a finding with its occurrence count and anchors, so the count is cumulative across sessions rather than restarting at one each time someone opens the file. A repetition rediscovered and re-ignored three times is indistinguishable from one nobody ever saw.

### When the fix is hard, suspect the shape

A problem that resists several attempts is often reporting a structural fact, not a difficult requirement. Concentration on the fix is exactly the condition under which that signal is missed, so treat these as mechanical triggers rather than intuitions:

- the second attempt failed, and the third is in progress;
- the fix requires a new flag, parameter, mode, or special case inside shared code;
- one behavior needs coordinated edits across four or more files;
- a value is being threaded through layers that have no use for it;
- the same guard is being added at several call sites to protect one invariant;
- the fix works but cannot be explained without describing the implementation;
- a test for it needs elaborate setup to reach the state being fixed.

On any of these, stop before continuing and ask one question: **is this hard because the problem is hard, or because the current shape makes it hard?** Name the shape that would make the bug impossible rather than merely fixed — a single owner for the invariant, a type that excludes the invalid state, a seam that already exists one layer up.

Then make a deliberate choice. Restructuring may be out of scope, and shipping the local fix is often correct. But it must be a decision with a recorded reason, not the default that follows from never having lifted the task's head. A fix threaded through five call sites because the owner was in the wrong place is a larger change than the refactor would have been, and it is paid again on the next related bug.

### Keep contracts and migrations explicit

- Preserve public APIs, serialized values, persistence schemas, and configuration compatibility unless the task authorizes a break.
- When centralizing an existing concept, update all in-scope callers or provide an explicit compatibility path. Do not leave two competing sources of truth.
- Test at the abstraction boundary: shared contract tests for variants, invariant tests for value objects, and integration tests for wiring.
- Where the boundary carries delivery, concurrency, or lifecycle, cover its failure modes rather than its happy path: duplicate delivery, concurrent claims, out-of-order events, cancellation races, restart recovery, and failure immediately before and after each external side effect.
- Prefer deleting replaced paths over retaining dead wrappers, but verify callers before removal.

### Enforce a new rule with a ratchet, not a sweep

A boundary introduced after its violations exist is usually written down and then ignored. Neither a repository-wide sweep nor silent grandfathering is the answer.

Enumerate the existing violations in a test, assert that nothing new may join them, and allow the list only to shrink. The frozen list carries the count the rule is meant to drive to zero, so the invariant becomes measurable rather than aspirational, and the next change cannot quietly add to it.

Apply this when a rule arrives late: a closed vocabulary still stored as strings, a dependency cycle, drift between a schema and its migrations, a base type that must not be constructed directly. Prefer it to a conditional exemption inside the production code.

## Workflow

### 1. Establish the change pressure

Identify the requested behavior, likely variation axis, affected boundary, compatibility constraints, and what must remain unchanged. For a review-only request, do not edit files.

When the case for a structural change is that the current shape is costly, count it: occurrences, call sites, modules affected, readers and writers of the contested table or type. A number distinguishes a real boundary problem from a stylistic preference, and it gives a ratchet its starting value.

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

If none of these decisions is material, use the fast path — and still sweep for repetition in step 5 once the edit exists.

Answer "whether semantic duplication already exists" by searching, not by recalling. In a repository of any size the honest answer from memory is "not that I have seen", which is not the same answer and is routinely wrong.

### 4. Implement the smallest coherent delta

Place behavior with its owner. Reuse the central path, consolidate in-scope duplicates, keep boundaries narrow, and avoid parallel frameworks. Add a new abstraction and its first specialization together only when the evidence above justifies it.

When the change moves or reshapes existing behavior rather than adding new behavior, read [references/safe-refactor.md](references/safe-refactor.md) before editing. A structural move with no observable behavior change is verifiable, and that property is worth more than the speed of making the move.

Do not add unused extension points for imagined future cases.

### 5. Sweep for repetition

Run this whenever code was added or changed, including on the fast path. It is mechanical on purpose: it is the one step that does not depend on remembering what the repository contains, which is why it survives a long task spent inside one hard problem.

Pick three to five **distinctive** tokens from what was just written and search the whole repository for each:

- a literal error or log message, or a user-facing string;
- an unusual identifier, key name, or field name;
- a pair of names that co-occur in the new logic;
- the shape of a condition, guard, or status comparison;
- the sequence of two or three calls that do the work.

Distinctive is the whole trick. A language keyword or a common verb returns noise; an error string, a literal key, or two identifiers appearing together returns the other instances or nothing. Read [references/duplication-sweep.md](references/duplication-sweep.md) for token selection, search recipes, and how to judge what comes back.

Five searches are enough. This is a sweep, not an audit, and it is bounded on purpose so there is no excuse to skip it.

For each real hit, apply the occurrence count above. Also search the names of anything new that was introduced — a helper, type, or configuration key with a near-synonym already in the repository is the same finding wearing a different coat.

Report the sweep's outcome even when it is clean, as one line. A sweep that silently found nothing is indistinguishable from one that never ran.

### 6. Verify behavior and structure

Run the repository's relevant tests, type checks, and linters. Then inspect the final diff and ask:

- Did this add a second way to do something the repository already does?
- Is any new string, flag, mapping, or state really a closed domain concept?
- Did a conditional grow because a polymorphic or table-driven seam already exists?
- Does every new type have one clear owner and reason to change?
- Did dependency direction remain intact?
- Could fewer concepts or less code express the same behavior more clearly?
- Are compatibility and shared-contract behavior tested?

### 7. Report architectural decisions

For implementation work, keep the handoff concise and include only material items:

- **Reused:** existing constructs or extension points used.
- **Introduced:** new abstractions or domain types and the evidence for them.
- **Preserved:** important boundaries or compatibility guarantees.
- **Repetition:** what the sweep searched for and what it found, including a clean result in one line. Where an occurrence count reached two or three, say which it was and what was decided.
- **Declined:** anything considered and deliberately not written, where leaving it out was a decision rather than an omission.
- **Deferred:** nearby architectural opportunities intentionally left out of scope, each with the count or evidence that would justify revisiting it.

Omit empty categories. For architecture audits or code reviews, read [references/review-rubric.md](references/review-rubric.md) and lead with evidence-backed findings. When a project ledger exists, distinguish new, changed, carried, resolved, reopened, and stale findings rather than presenting every open item as a fresh discovery.
