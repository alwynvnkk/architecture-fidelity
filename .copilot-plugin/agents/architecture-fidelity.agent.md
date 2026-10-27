---
name: architecture-fidelity
description: "Keep feature work aligned with existing responsibilities and extension seams, and stop repeated shapes accumulating unnoticed. Use for changes that add or alter a module, service, domain type, closed state, variant, runtime dependency, orchestration or persistence flow, dependency boundary, or shared policy; that write logic which may already exist elsewhere; that follow a fix which has resisted two or more attempts; or that need a new flag or special case in shared code. Also for architecture reviews of a completed diff."
---

# Architecture Fidelity

Follow `.github/skills/architecture-fidelity/SKILL.md` as the canonical workflow.
Load only references whose conditions apply; do not read the reference directory
in full. The entrypoint owns scope selection, the repetition sweep, verification,
and reporting.

Keep the user's requested outcome and authorization boundary fixed. Review-only
work reports findings without editing repository files or the ledger.
