# Ledger Format

Read only when authoring or inspecting ledger JSON. For audit scope, identity, and authorization, use [project-ledger.md](project-ledger.md).


The repository file has this top-level structure:

```json
{
  "schema_version": 1,
  "project": {"name": "example"},
  "audit": {
    "last_complete_commit": null,
    "completed_at": null
  },
  "landmarks": [],
  "findings": [],
  "history": []
}
```

A landmark contains `id`, `kind`, `statement`, one or more `anchors`, `first_seen_commit`, and `last_verified_commit`. Allowed kinds are `canonical-owner`, `dependency-rule`, `extension-seam`, `domain-vocabulary`, and `approved-analogue`.

A finding contains:

```json
{
  "id": "AF-0001",
  "fingerprint": "<sha256>",
  "status": "open",
  "severity": "high",
  "category": "competing-implementation",
  "summary": "Two routes own the same mutation policy",
  "invariant": "A domain mutation has one canonical owner",
  "impact": "Validation and audit behavior can diverge",
  "correction": "Route both callers through the canonical service",
  "owner": null,
  "external_ref": null,
  "anchors": [
    {"path": "src/domain/service.py", "symbol": "save_entry"}
  ],
  "first_seen_commit": "<git commit>",
  "last_verified_commit": "<git commit>",
  "events": []
}
```

An audit delta accepted by `apply-delta` contains a required `audit` object and optional landmark and finding upserts:

```json
{
  "completed_at": "2026-08-30T12:00:00Z",
  "audit": {
    "mode": "incremental",
    "complete": false,
    "base_commit": "<previous commit>",
    "commit": "<assessed commit>",
    "scope": ["src/domain/service.py"]
  },
  "landmarks": [],
  "findings": []
}
```

For a new finding, `id` and `fingerprint` may be omitted from a delta; the helper allocates them. For an existing finding, identify it by `id` or fingerprint. Include `transition_reason` when changing status. To record new evidence on an existing finding without changing status, supply `evidence_reason` (non-empty text). The helper preserves `first_seen_commit` and prior events, and stamps appended events with the resulting status, delta completion time, and last verified commit. If both reasons are supplied during a transition, both events are retained. Existing findings' `events` are helper-managed; supplying a replacement array does not append evidence.

### Evidence update

Send the existing finding fields with revised `impact` and an `evidence_reason`, for example `"Count increased from 3 to 4: src/d.py repeats the guard"`. Keep its category, invariant, and anchors unchanged. The reason is a delta instruction, not a stored finding field; the helper appends it to lifecycle history.

### Coverage

`audit.complete` controls baseline advancement independently of `mode`. Set it explicitly when authoring a delta:

| Pass | `mode` | `complete` |
| --- | --- | --- |
| Targeted first seed or partial full audit | `full` | `false` |
| Finished full audit | `full` | `true` |
| Targeted incremental pass | `incremental` | `false` |
| Entire planned incremental scope assessed | `incremental` | `true` |

For compatibility, omission defaults to true for `full` and false for `incremental`. A partial first seed must explicitly use false; mode alone does not establish coverage. Every pass enters history; only a complete pass updates `audit.last_complete_commit` and its completion time.
