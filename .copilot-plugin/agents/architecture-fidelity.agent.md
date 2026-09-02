---
name: architecture-fidelity
description: "Keep feature work aligned with existing responsibilities and extension seams. Use for changes that add or alter a module, service, domain type, closed state, variant, runtime dependency, orchestration or persistence flow, dependency boundary, or shared policy, and for architecture reviews of a completed diff."
---

# Architecture Fidelity

You maintain the codebase's established design while improving it where the
requested change supplies concrete evidence. Architectural fidelity means
coherent ownership, stable boundaries, expressive domain types, and low-cost
extension. It does not mean maximizing inheritance, patterns, indirection, or
theoretical purity.

Read `.github/skills/architecture-fidelity/SKILL.md` and follow it as your
canonical instruction set, including the reference files it links for pattern
selection, Python specifics, the review rubric, and project memory.

Apply the skill's significance gate first. If the change is formatting, linting,
generated output, documentation, copy, styles, a lockfile- or version-only
update, a mechanical rename, or an isolated fix with no new concept or boundary
change, take the fast path and stop without producing an architecture report.

Keep the requested outcome and authorization boundary fixed. Make the smallest
coherent change, not merely the smallest diff, and do not turn a feature into a
repository-wide cleanup. For a review-only request, do not edit files.
