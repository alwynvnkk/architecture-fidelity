# Pattern Selection

Use this reference only when a change presents a real abstraction choice. Patterns are consequences of variation and ownership, not goals.

## First test the candidate abstraction

An abstraction is credible when most answers are yes:

- Do the cases share a domain invariant, not just a code shape?
- Would they change for the same business reason?
- Can the common contract be named without `helper`, `common`, `manager`, or `base`?
- Can callers use the contract without checking the concrete case?
- Does centralization remove coordinated edits or prevent invalid states?
- Is the variation axis visible in current requirements or code?

If only syntax is shared, prefer small local duplication. If concepts are shared but behavior is not stable, delay the abstraction and keep ownership clear.

## Match the mechanism to the variation

| Change pressure | Prefer | Evidence | Avoid |
| --- | --- | --- | --- |
| Closed set of named values | Enum or sealed/tagged union | Values are finite, meaningful, validated, and reused | Raw strings, booleans with unclear meaning |
| One concept made of validated values | Immutable value object | Values travel and validate together | Primitive parameter clusters |
| Same operation, independently varying behavior | Strategy via composition | Callers need one contract and interchangeable policies | Growing mode flags or subtype checks |
| Shared capability across unrelated types | Protocol/interface/trait | Callers need only that capability | Inheritance solely to share a method |
| Stable algorithm skeleton with controlled steps | Template method or composed pipeline | Ordering is invariant; selected steps vary | Copying orchestration into each variant |
| Stable substitutable family with shared invariant/state | Base class | A genuine is-a relation and inherited contract exist | Speculative abstract base classes |
| Concrete implementation selection | Factory or registry | Creation rules are centralized and have multiple cases | Scattered constructors and switches |
| Mostly data-to-data transformation | Plain function or table | Little identity, lifecycle, or mutable state | Class wrappers with no owned invariant |
| Framework/vendor boundary | Adapter | External vocabulary or lifecycle must not leak inward | Vendor types throughout domain code |
| Cross-cutting collaboration assembled at a boundary | Dependency injection | Ownership and test seams are clearer | Service locator or hidden globals |

## Composition versus inheritance

Default to composition when behaviors vary independently, may be combined, or have distinct lifecycles. Use inheritance only when all of these hold:

- the subtype is substitutable everywhere the parent is promised;
- the parent defines a meaningful stable contract;
- shared state or lifecycle is part of that contract, not an implementation convenience;
- overriding behavior cannot weaken preconditions, strengthen required inputs, or violate postconditions;
- consumers do not need concrete-type checks.

If only implementation code is shared, extract a collaborator or function instead of inventing a taxonomy.

## Generalization and specialization

When a new case resembles an existing concrete implementation:

1. Separate the invariant core from the new variation.
2. Move only the proven common contract upward or inward.
3. Keep case-specific policy in explicit specializations or collaborators.
4. Add shared contract tests before relying on interchangeability.
5. Ensure the original case remains readable after generalization.

Avoid a base class whose methods are mostly optional, raise "not supported," or require flag-controlled behavior. That is usually multiple capabilities or compositions disguised as one hierarchy.

## Common architectural traps

- **Compensating for an incorrect producer.** A conversion layer, alias map, or fallback keeps owned callers sending incorrect inputs. Trace the first contract violation and evaluate a source correction using [Correct the producer](design-decisions.md#correct-the-producer).
- **Parallel path:** adding a new service or flow beside the existing orchestrator instead of extending it.
- **Parameter soup:** one implementation accumulates booleans and nullable options for unrelated variants.
- **Utility gravity:** unrelated responsibilities gather in a generic helper module because it is easy to import.
- **Interface ceremony:** an interface exists only to mirror one implementation and provides no boundary, variation, or test seam.
- **Inheritance for reuse:** types share code but not a substitutable contract.
- **Premature framework:** a registry, plugin system, or generalized engine appears before a second concrete requirement.
- **Leaky domain:** framework models, transport strings, or persistence details become the application's core vocabulary.
- **Dual truth:** a new enum, registry, or mapping is added while the old literals or switches remain authoritative elsewhere.

The preferred correction is the smallest one that restores one owner and one path.
