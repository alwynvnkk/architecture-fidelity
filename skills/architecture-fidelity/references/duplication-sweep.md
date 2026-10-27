# Duplication Sweep

Use when choosing search tokens or interpreting repetition hits. Keep the sweep to three to five searches; it reveals candidates outside the task's context, not exhaustive semantic coverage.

## Select tokens

Prefer:

- literal error, log, or user-facing prose;
- a distinctive key, column, header, constant, or regex;
- two identifiers that co-occur;
- a sequence of two or three calls, searched as separate terms within a file;
- a new helper/type/configuration name, also searched by responsibility for near-synonyms.

Avoid keywords, framework methods, common verbs, and short identifiers. If a token returns more than about thirty hits, narrow it rather than reading noise. For interpolated strings, use the longest plain-prose segment; expression fragments match syntax rather than the message.

## Search and count

Search the whole repository, including tests. Tracked-file literal search usually suffices; use structural search when available for shapes that differ textually. Exclude generated output, vendored dependencies, lockfiles, build artifacts, snapshots, and pinned predecessor copies. Confirm actual search coverage: four copies of one module at different dates are not four independent implementations.

Read each plausible hit and classify it:

| Evidence | Decision |
| --- | --- |
| Same invariant and reason to change | Count semantic occurrences, including the new code; examine two, address or record three. |
| Similar shape, different owners/invariants | Keep separate; explain a material decision once. |
| Coincidental syntax | Ignore. |
| Existing owner plus independent reimplementation | Check whether the caller bypasses that owner; route through it if the contract applies. |

An occurrence count warrants examination, not automatic extraction. A clean search is not proof of absence.

## Examples

**Repeated upload constraints:** `unsupported media type` finds two other modules; `content_type` is too broad; `max_bytes` alongside `mime` finds the same modules. Read all three. If accepted types and size ceilings implement one rule but already disagree, report the missing constraint owner and divergent limits.

**Possible bypass:** a literal SQL migration-fence statement appears beside different per-module table locks. The local locks may be distinct while the fence protects one invariant. Follow the surrounding names to definitions and callers to establish whether a shared owner already exists. Report counts, divergence, and any unresolved ownership question; the search alone cannot settle semantics.

## Record a deferral

When correction exceeds scope, report the count, occurrences, missing owner, and reason for deferral. For an authorized ledger update, follow [project-ledger.md](project-ledger.md): anchor the concept stably and keep the changing occurrence list in `impact`, so finding identity survives a rising count. Review-only work reports the proposed delta without writing it.
