---
description: "Run an Architecture Fidelity pass on the current task or diff."
---

# Architecture Fidelity pass

Run one Architecture Fidelity pass over the current task, or over the diff the
user names.

Follow `.github/skills/architecture-fidelity/SKILL.md` as the canonical
instruction set, including the reference files it links.

Because this prompt was invoked explicitly, treat the significance gate as
already satisfied and proceed to the workflow: establish the change pressure,
reconnoiter the repository by responsibility, state the design decision, then
either implement the smallest coherent delta or, for a review-only request,
report findings without editing files.

Where code was added or changed, run the repetition sweep before verifying:
three to five distinctive tokens from what was written, searched across the
whole repository, then the skill's occurrence count applied to each real hit.

If `.architecture-fidelity/ledger.json` exists, plan incrementally from its Git
baseline and distinguish new, changed, carried, resolved, reopened, and stale
findings. Do not initialize or write a ledger unless asked.

Close with the reporting section from the skill: reused constructs, introduced
abstractions and their evidence, preserved boundaries, what the repetition sweep
searched for and found, anything deliberately not written, and deliberately
deferred opportunities. Omit empty categories.
