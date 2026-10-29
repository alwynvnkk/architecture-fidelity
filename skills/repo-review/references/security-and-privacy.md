# Security and privacy

## Establish the trust model

Identify actors, protected resources, deployment defaults, and what an attacker or untrusted input can influence. Distinguish trusted single-user operation from shared tenancy, exposed services, or execution of hostile workloads. State conditions that change severity.

Trace relevant sensitive data from collection through storage, logging, external transmission, retention, and deletion. Record destinations and who can read the data. A local interface can still send content to remote providers; encryption and signatures protect only particular properties under particular key-access assumptions.

## Follow enforcement, not labels

Choose checks from the project's actual attack surface rather than running an unrelated checklist. Typical high-value traces include:

- Authentication through route authorization to resource ownership, including aliases and fallback permissions.
- Untrusted input through command execution, file paths, templates, database queries, or outbound requests.
- Agent or plugin execution through permission configuration, host/container boundaries, mounts, environment, credentials, and network access.
- Sensitive output through logs, observability endpoints, caches, exports, and third-party SDKs.
- Advertised controls through configuration, production callers, and an observable denial or restriction.

Check whether a guard executes before the sensitive action and covers alternate entrypoints. Distinguish workspace separation from process isolation, approval gates from containment, audit integrity from completeness, and authentication from authorization. Describe the property actually guaranteed.

Inspect deployment examples as well as library defaults. Check CI and dependency policy when relevant, but do not infer current vulnerabilities from a dependency name or treat a scanner's silence as a security guarantee. Verify current advisory claims against authoritative sources and exact versions when making them.

## Validate proportionately

For a suspected flaw, establish attacker prerequisites, reachable path, missing or bypassed invariant, and concrete consequence. Search for middleware, ownership resolvers, validation, and deployment constraints that might invalidate it. Missing tests alone do not establish a vulnerability.

Use harmless synthetic data for focused checks. Extracted definitions can verify a local behavior but cannot prove that authentication, middleware ordering, routing, or deployment exposes it. Label that boundary and reserve integration claims for integration evidence.

If evidence remains incomplete, frame a question or conditional risk instead of a confirmed exploit. Do not expose secret values in the report; cite their location and access conditions. A source review supports bounded trust conclusions, not a blanket certification.
