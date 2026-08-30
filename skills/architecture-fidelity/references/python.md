# Python Architecture Choices

Read this reference only for Python work. Respect the repository's supported Python version and existing public/serialization contracts.

## Closed string options

Use `enum.StrEnum` when values are:

- a finite domain-defined set;
- meaningful at runtime, not only to a type checker;
- compared, serialized, parsed, iterated, or documented across multiple call sites;
- stable enough to be one source of truth.

Prefer it to bare `str` constants or `class X(str, Enum)` when the supported Python version includes `StrEnum`. Choose explicit string values when they are stored or sent externally; use generated values only when renaming members cannot silently break compatibility.

Do not use `StrEnum` for arbitrary user input, extensible third-party identifiers, or values whose set is intentionally open. At boundaries, validate with the domain enum and deliberately convert to the wire or persistence representation expected by the framework. Confirm serializer behavior rather than assuming every library treats string enums identically.

Use `Literal[...]` for a small static type-checking constraint with no runtime identity, behavior, iteration, parsing, or central ownership. Promote repeated `Literal` definitions or runtime checks to an enum or value object when they become a domain concept.

## Pick the narrowest expressive type

| Need | Python mechanism | Architectural signal |
| --- | --- | --- |
| Distinct scalar identity | `NewType` or validated value object | Prevent IDs or units from being mixed |
| Immutable validated concept | Frozen dataclass or small custom value object | Co-locate validation and domain behavior |
| Structural capability | `typing.Protocol` | Consumers depend on behavior, not ancestry |
| Runtime-enforced family or shared lifecycle | `abc.ABC` | Implementations intentionally inherit a contract |
| Closed alternatives carrying data | Enum plus value objects, or explicit tagged models | Make exhaustive variants visible |
| Internal sentinel | `object()` or a private enum member | Distinguish missing from valid `None` |
| Stateless transformation | Typed function | Avoid classes without identity or invariant |

Do not use `Any`, dictionaries, or strings to avoid naming an established domain concept. Do not introduce a class merely to satisfy an OO preference when a typed function owns no state or invariant.

## Protocol versus abstract base class

Prefer `Protocol` when existing or third-party types should satisfy a narrow capability structurally and consumers do not need shared implementation. Prefer an abstract base class when the repository owns the family and must share or enforce a lifecycle, invariant, or implementation skeleton.

In either case:

- type the contract from the consumer's needs;
- avoid exposing methods no consumer requires;
- add contract tests when implementations are intended to be interchangeable;
- avoid `isinstance` branches on concrete implementations after introducing the abstraction.

## Value objects and configuration

Use a value object when validation, normalization, equality, or formatting belongs to a concept rather than to every caller. Keep construction strict in the core and parse permissive external input at the boundary.

Use typed configuration models already established by the repository. Avoid adding a second configuration system or copying environment-variable parsing into feature code.

## Errors and state

- Reuse the repository's error hierarchy and translation boundary.
- Represent meaningful lifecycle states explicitly when transitions have rules; do not spread string comparisons across handlers.
- Centralize state transitions in the owner and test invalid transitions.
- Preserve exception chaining and domain-to-transport translation at existing boundaries.

## Python self-check

Before finishing, search for new raw literals, duplicated validation, parallel factories, concrete-type checks, broad `dict[str, Any]` data flow, and new `utils.py` or `base.py` ownership. Each should be justified by the local design rather than convenience.
