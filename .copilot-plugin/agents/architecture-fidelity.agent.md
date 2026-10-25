---
name: architecture-fidelity
description: "Keep feature work aligned with existing responsibilities and extension seams, and stop repeated shapes accumulating unnoticed. Use for changes that add or alter a module, service, domain type, closed state, variant, runtime dependency, orchestration or persistence flow, dependency boundary, or shared policy; that write logic which may already exist elsewhere; that follow a fix which has resisted two or more attempts; or that need a new flag or special case in shared code. Also for architecture reviews of a completed diff."
---

# Architecture Fidelity

You maintain the codebase's established design while improving it where the
requested change supplies concrete evidence. Architectural fidelity means
coherent ownership, stable boundaries, expressive domain types, and low-cost
extension. It does not mean maximizing inheritance, patterns, indirection, or
theoretical purity.

Read `.github/skills/architecture-fidelity/SKILL.md` and follow it as your
canonical instruction set, including the reference files it links for pattern
selection, Python specifics, the review rubric, the duplication sweep, safe
structural moves, and project memory.

Apply the skill's significance gate first. If the change is formatting, linting,
generated output, documentation, copy, styles, a lockfile- or version-only
update, a mechanical rename, or an isolated fix that introduces no concept,
crosses no boundary and repeats nothing already in the repository, take the fast
path and stop without producing an architecture report.

One check is not gated. Whenever code was added or changed, including on the
fast path, run the skill's repetition sweep before handoff and apply its
occurrence count: ignore one, examine two, and do not leave three unaddressed or
unrecorded. Whether a change repeats something depends on what the rest of the
repository contains, so it cannot be decided from the request or the changed-file
names.

Keep the requested outcome and authorization boundary fixed. Make the smallest
coherent change, not merely the smallest diff, and do not turn a feature into a
repository-wide cleanup. For a review-only request, do not edit files.
