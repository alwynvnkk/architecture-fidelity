# Assessment and findings

Adapt the deliverable to the user's question. A broad review usually needs a concise verdict, material findings, a plain-language account of functionality and value, and verification limits. A focused audit can lead directly with findings. Do not force empty sections or repeat the same issue under every lens.

## Findings

Include a finding when evidence establishes a meaningful consequence. For each, give:

- Severity and the condition under which it applies.
- The affected behavior or violated guarantee, with precise file/line evidence at the reviewed revision.
- The reachable flow, prerequisites, and practical consequence.
- The smallest useful correction or mitigation, plus verification needed if it matters.

Order by practical impact. For security and correctness, severity follows consequence, exposure, and prerequisites; architecture-fidelity supplies severity for architectural findings. Keep confidence separate from severity. Count one root cause once even when it affects several lenses.

Distinguish confirmed defects, deployment-dependent risks, product limitations, and optional improvements. A disclosed limitation can still block adoption without being a vulnerability. File length, popularity, solo maintenance, and module counts can guide investigation but are not standalone defects.

## Evidence and verdict

Use commit-pinned source links for remote repositories and clickable file/line links for local work. Anchor important conclusions in implementation evidence rather than README quotations. Give credit to controls that are actually wired and to limitations the project discloses.

State reviewed revision and scope, checks run, checks blocked or omitted, and assumptions that could change the recommendation. If there are no actionable findings, say so within those limits. Do not imply a full test suite, dependency audit, HTTP exploit, or live deployment check when only static or focused verification occurred.

Make the recommendation decision-specific: adopt, pilot under stated conditions, borrow particular ideas, or pass. Explain the decisive benefit or mismatch and any prerequisite fix. Avoid generic production-hardening lists and automatic pilot recommendations unrelated to the user's intended use.
