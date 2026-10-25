# Duplication Sweep

Read this for the mechanics of workflow step 5: how to choose search tokens, what to search for, and how to judge what comes back.

The sweep exists because of a specific failure. Deep in a hard problem, with a handful of a repository's files in context, an agent writes logic that already exists twice elsewhere — in files it never opened. Every judgment it makes is locally correct. The only thing that can see the other instances is a search, so the search is mandatory and the judgment comes after.

Keep it bounded: three to five searches, a minute of work. An audit would be skipped; this should not be.

## Choose distinctive tokens

Distinctiveness is the whole technique. A token that appears in a hundred places teaches nothing; one that appears in three has just found the pattern.

Good tokens, roughly best first:

| Token | Why it works |
|---|---|
| A literal error, log, or user-facing string | Near-unique, and copied verbatim when logic is copied |
| A literal key, header, column, or field name | Survives reformatting and renaming of the surrounding code |
| Two identifiers that co-occur | Individually common, jointly rare — the strongest structural signal |
| An unusual constant, magic number, or regex | Copied rather than rewritten |
| A distinctive call sequence | Two or three calls in order, searched as separate terms within a file |
| The name of anything new introduced | Catches a near-synonym of an existing helper or key |

Weak tokens to avoid: language keywords, framework method names, common verbs like `get`, `create`, `validate`, `handle`, and any single short identifier. If a search returns more than about thirty hits, the token was wrong — pick a narrower one rather than reading the results.

Two traps are worth naming, because both produce confident nonsense rather than obvious noise:

- **An interpolated string is not a literal.** Searching for a fragment of an f-string or a concatenation matches the *syntax around the interpolation*, not the message. Tokens like `": VERSION,"` or `"] if direction =="` are fragments of expressions and will hit dozens of unrelated files. Take the longest run of plain prose inside the string, or use a different token type.
- **Snapshots and pinned copies flood the results.** A repository that keeps vendored dependencies, generated output, pinned predecessor copies of a module, or executable evidence artifacts under a documentation tree will return many hits that are all the same file at different times. Exclude those paths before judging anything: four hits in four snapshot directories is one occurrence, not four, and counting them as four invents a pattern that does not exist.

Confirm what the search actually covered. A result that looks like a strong pattern and comes entirely from one excluded tree is the most misleading outcome available.

## Search the whole repository

Search the repository, not the module. The point is to see outside the task's context, and a sibling module is where a copy most often lives.

Include tests: a duplicated setup block or assertion sequence is evidence of a missing fixture or a shared contract, and tests are where repetition accumulates fastest and is tolerated longest.

Exclude generated output, vendored dependencies, lockfiles, and build artifacts. A hit there is noise, and a hit in a generated file means the generator is the subject, not the code.

Search with whatever the repository provides. A literal-string search over tracked files is usually enough; structural search tools find shape rather than text where they are available, and are worth using for a call sequence or a condition shape that will not match textually.

## Judge what comes back

A hit is only evidence once it is read. Open each one and decide which of these it is:

- **The same invariant, duplicated.** The instances enforce one rule, and a change to that rule must change all of them. This is the real finding — apply the occurrence count.
- **The same shape, different invariants.** Two modules validate similarly but answer to different owners and change for different reasons. Leave them apart; coupling them would be the worse outcome. Say so once, so the next pass does not relitigate it.
- **A genuine coincidence.** Shared syntax, nothing more. Note nothing.
- **Already centralized, and bypassed.** An owner exists and these call sites do not use it. This is more urgent than plain duplication, because the repository already decided and the decision is eroding. Route the new code through the owner.

The middle two are legitimate outcomes. What the sweep rules out is not having looked.

## A worked shape

New code validates an uploaded file and raises on failure. Distinctive tokens: the literal message `"unsupported media type"`, the field name `content_type`, and the pair `max_bytes` with `mime`.

- `"unsupported media type"` → two other modules.
- `content_type` → thirty hits, too broad, discarded.
- `max_bytes` near `mime` → the same two modules, plus a test fixture.

Three semantic occurrences including the new one. Reading them shows one rule — the accepted type set and the size ceiling — enforced three times with two slightly different limits, which is already a latent bug rather than a style problem. The finding is not "this code is duplicated"; it is "the upload constraint has no owner, and the three copies already disagree."

That reframing is the sweep's real output. A count turns a maintenance preference into a defect with evidence.

## A second shape: the bypassed owner

A sweep over a 322k-line repository searched two token types — repeated prose strings and a repeated literal SQL statement — and surfaced one statement appearing in four modules inside a persistence package: a share lock taken on the migration table while importing, each time beside a different exclusive lock on that module's own tables.

The per-module lock is legitimately local. The migration fence is not: it enforces one invariant, that an import cannot run while a migration does, and a change to that rule must change every copy.

Searching the names around it then found five module-level functions sharing one name and three different signatures, where one delegated to a shared owner and another reimplemented forty lines of schema verification independently. Which makes the finding sharper than "this is duplicated": an owner exists and is used in one place and bypassed in another, and one copy's signature admits a write mode the others do not.

Two lessons generalize from it:

- **The name search comes after the token search, not instead of it.** Grepping the function name finds this instantly — but only for someone who already knows the name. The next module to need the guard will not know it, and will write a sixth copy. The literal token is what surfaces the concept without knowing what it is called.
- **Stop at the finding, not the verdict.** Whether the reimplementation is a bypass or a legitimately separate concern turned on whether provider telemetry and exact-history import share an invariant — a question for whoever owns them. Report the count, the divergence, and the question. Deciding it unilaterally from a search result is how a sweep becomes a refactor nobody asked for.

## When the correction is out of scope

Centralizing may be larger than the current task should carry. That is a legitimate decision, and an unrecorded one is not.

Record it as a repetition finding with its count, the occurrences, and the owner the shape is missing — see [project-ledger.md](project-ledger.md) for how to anchor it so the count accumulates instead of restarting. Then say in the handoff that the count reached three and what was decided.

A repetition discovered, left alone, and forgotten three times over is indistinguishable from one nobody ever noticed. The count is the only thing that makes the cost visible, and it only works if it is written down.
