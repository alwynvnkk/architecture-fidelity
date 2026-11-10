# Architecture Fidelity

Architecture Fidelity is a shared skill package for Codex, Claude Code, GitHub Copilot, and Pi. It supports coherent implementation and evidence-based decisions about the repositories you use.

| Skill | Purpose |
|---|---|
| [architecture-fidelity](skills/architecture-fidelity/SKILL.md) | Keep feature work aligned with existing responsibilities and extension seams. |
| [repo-review](skills/repo-review/SKILL.md) | Assess implemented functionality, practical value, security, privacy, and adoption fit. |

The skills remain separate entrypoints within one package. `repo-review` uses `architecture-fidelity` for its architecture lens; design rules stay in one place.

It addresses a recurring failure mode in agent-written code: the requested behavior works, but arrives as a parallel service, raw string option, duplicated branch, or new helper even though the repository already contains the right concept.

## What it adds

The skill makes architectural reconnaissance part of implementation and review:

- ask whether the code needs to exist before asking what shape it should take, and delete speculative parameters, single-implementation interfaces, and configuration nothing changes;
- search by responsibility before adding types, modules, services, or dependencies;
- prefer reuse, extension, and evidence-backed generalization over parallel implementation;
- count occurrences of a repeated shape — ignore one, examine two, and refuse to leave three unaddressed or unrecorded;
- sweep the repository for the shapes a change just wrote, mechanically and including on the fast path, so a third copy is caught by search rather than by recall;
- treat a fix that resists several attempts, needs a flag in shared code, or spans four files as evidence about the shape rather than the difficulty;
- recognize semantic duplication in validation, state transitions, mappings, errors, and orchestration;
- choose composition, inheritance, interfaces, strategies, factories, value objects, or plain functions according to the actual variation;
- model closed domain choices with enums such as Python's `StrEnum` when compatibility permits;
- preserve dependency direction, public contracts, serialized values, and one source of truth;
- retain repository-side architectural memory so later audits revalidate changed surfaces instead of rediscovering the whole codebase;
- avoid speculative frameworks, inheritance for code sharing, and abstractions with only superficial similarity;
- enforce a rule that arrived after its violations with a ratcheted list of the known ones, rather than prose or a repository-wide sweep;
- verify a structural move against a characterisation pin instead of asserting that behaviour was preserved;
- report material reuse, new abstractions, preserved boundaries, and deliberately deferred opportunities.

After a solution works, the skill asks whether the same supported behavior can be expressed clearly with less code, and what the change makes unnecessary. This bounded simplification pass considers affected callers and helpers together, looking for redundant decisions, state, and earlier workarounds. Reductions should improve concepts, branches, or maintenance points while preserving readability and contracts. Line count is supporting evidence, with no reduction quota. Relevant checks run against the final simplified change.

Before adding downstream conversions or fallbacks for incorrect inputs, the skill traces the producer and receiving contract. It prefers correcting owned callers when compatibility permits, and requires concrete justification for adapters serving external producers, supported legacy inputs, or intentional vocabulary boundaries. This check also applies to local fixes.

This is intentionally not a replacement for Ruff, formatters, type checkers, or static-analysis rules. Those tools own mechanical consistency. Architecture Fidelity owns repository-level design decisions that require understanding responsibilities, callers, and change pressure.

## Automatic activation

The skill is implicitly invocable: Codex, Claude Code, GitHub Copilot, and Pi can select it from its description without a human naming it. Its routing policy uses a significance gate rather than change frequency.

It should run once during planning when a task clearly introduces or changes a responsibility, domain concept, variant, orchestration or persistence flow, dependency boundary, shared policy, or multi-implementation abstraction. If that only becomes apparent during implementation, it should run once against the final diff before handoff or PR preparation.

It should also run when a change writes logic that may already exist elsewhere, when a fix has resisted two or more attempts, and when a fix needs a new flag or special case inside shared code. Those are the signals of a repeated shape or a misplaced owner, and they are the ones a long task spent inside one hard problem misses.

It should not run after every edit, commit, test, or merely because a PR is approaching. Formatting, linting, generated output, documentation, copy, styles, lockfile- or version-only updates, mechanical renames, and genuinely isolated fixes take the fast path. Adding or replacing a runtime dependency still qualifies. Diff size alone does not decide: a one-line state transition may be architectural, while a large generated diff may not be.

The repetition sweep and bounded simplification pass also apply to local code fixes on the fast path. The sweep runs whenever code was added or changed, because repetition depends on what the rest of the repository contains. It is bounded to a few searches. Simplification follows a working solution, stays within the requested scope, and may conclude that the current implementation is already the clearest.

For repositories that want the same policy reinforced in `AGENTS.md`, `CLAUDE.md`, or `.github/copilot-instructions.md`, use:

```markdown
Use the installed architecture-fidelity skill automatically when a task or its resulting diff changes responsibilities, domain types or closed states, variants, runtime dependencies, orchestration or persistence flows, dependency boundaries, shared policy, or multiple implementations. Also use it when the change writes validation, mapping, error handling, state transitions, or a call sequence that may already exist elsewhere; when a fix has resisted two or more attempts; and when a fix needs a new flag, parameter, or special case inside shared code. Invoke it once during planning when evident; otherwise once before handoff if those signals emerge. Do not invoke it per edit or for formatting, linting, generated files, docs/copy/styles, lockfile- or version-only updates, mechanical renames, or isolated fixes that introduce no concept, cross no boundary, and repeat nothing already in the repository. Re-run only if the scope materially expands after the prior pass. Its repetition sweep runs whenever code changed, including on the fast path, because repetition cannot be judged from the request or the file names. After the solution works, follow its bounded simplification pass, including for local fixes, then run relevant checks against the final change. Seek clearer code with fewer redundant decisions, state, and maintenance points while preserving contracts and task scope.
```

## Structure

```text
.
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── .copilot-plugin/
│   ├── agents/architecture-fidelity.agent.md
│   ├── instructions/architecture-fidelity.instructions.md
│   └── prompts/architecture-fidelity.prompt.md
├── package.json
└── skills/
    ├── repo-review/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   └── references/
    │       ├── assessment.md
    │       ├── functionality-and-value.md
    │       └── security-and-privacy.md
    └── architecture-fidelity/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── scripts/
        │   └── architecture_ledger.py
        └── references/
            ├── design-decisions.md
            ├── duplication-sweep.md
            ├── ledger-format.md
            ├── pattern-selection.md
            ├── project-ledger.md
            ├── python.md
            ├── review-rubric.md
            └── safe-refactor.md
```

Each skill’s short `SKILL.md` entrypoint is canonical across all hosts. It routes to references only when a design choice, review, structural move, or ledger operation needs that detail; agents should not load every reference. Ledger JSON formats live separately from audit planning, and the dependency-free helper executes without loading its source into context.

Product manifests only package that shared implementation, and the Copilot adapters under `.copilot-plugin/` route to it rather than restating it.

## Project memory

Outside GitHub Copilot, Architecture Fidelity can keep a reviewable ledger at `.architecture-fidelity/ledger.json` in the repository being audited. It remembers both healthy architectural landmarks and finding lifecycles, while Git remains the source of truth.

The first audit that clears the significance gate with repository edits authorized creates the ledger itself, seeded from what that pass established. It records only load-bearing architecture — canonical owners, enforced boundaries, extension seams, closed vocabularies, and findings that are high severity or span more than one module — capped at roughly ten of each, so a first ledger stays reviewable in a pull request. A targeted seed explicitly uses `audit.complete: false`, retaining its findings without claiming complete coverage. It does not trigger a repository-wide inventory, and it is not created at all when nothing clears that bar. A review-only request never writes it; the skill reports the proposed delta instead.

To create an empty ledger up front instead:

```bash
python3 /path/to/architecture-fidelity/skills/architecture-fidelity/scripts/architecture_ledger.py \
  --root /path/to/repository init
```

On later audits, the skill plans from the last completed commit, revalidates landmarks and findings whose anchors changed, carries untouched findings without calling them new, and recognizes resolved findings that regress. If the baseline is missing or invalid, it falls back to a full scan.

The helper also supports `validate`, `plan`, `fingerprint`, and `apply-delta`. The ledger is intentionally JSON plus a dependency-free Python helper: portable across Codex, Claude Code, GitHub Copilot, and Pi, easy to review in pull requests, and small enough to replace later if project scale proves that necessary.

## Try it locally

### Codex

For repository-scoped development, symlink or copy the skill into the target repository:

```bash
mkdir -p /path/to/repository/.agents/skills
ln -s "/absolute/path/to/architecture-fidelity/skills/architecture-fidelity" \
  /path/to/repository/.agents/skills/architecture-fidelity
```

Start a new Codex session in that repository, then invoke `$architecture-fidelity` explicitly or ask for a feature implementation, refactor, or architecture review that matches its description.

The `.codex-plugin` manifest is ready for packaging into a Codex marketplace when the repository has a distribution location.

### Claude Code

Load the repository directly as a development plugin:

```bash
claude --plugin-dir "/absolute/path/to/architecture-fidelity"
```

Invoke `/architecture-fidelity:architecture-fidelity`, or let Claude select it for matching work. Run `/reload-plugins` after edits.

### GitHub Copilot

Install the skill once in your personal Copilot skills directory. Copilot CLI discovers personal skills across repositories. See [GitHub's personal skill setup](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills).

```bash
mkdir -p "$HOME/.copilot/skills"
cp -R "/absolute/path/to/architecture-fidelity/skills/architecture-fidelity" "$HOME/.copilot/skills/"
```

Start a new session or run `/skills reload` in Copilot CLI. Invoke `/architecture-fidelity` or let Copilot select the skill for matching work.

Copilot stores architectural findings and their history under `~/.copilot/skills/architecture-fidelity/journals/<project-key>/ledger.json`. The key comes from the local Git common directory, so linked worktrees share a journal and separate clones get separate journals. Contributor checkouts need no skill files, journals, or `.gitignore` entries. Copy the skill for a personal install so the journal directory stays outside the source checkout as well.

To bring forward an existing repository ledger, run the personal helper with `--root <repository> --local plan` and use its `ledger_path`. If that destination has no ledger yet, copy the old JSON there and run `--local validate`. Preserve the installed `journals/` directory when updating the skill.

Teams can still opt into repository routing by installing the adapters from `.copilot-plugin/` into the corresponding `.github/agents/`, `.github/instructions/`, and `.github/prompts/` directories and copying the shared skill into `.github/skills/`. These adapters can run the workflow without persistent memory when a personal installation is unavailable.

### Pi

Load just the skill for a one-off session:

```bash
pi --skill "/absolute/path/to/architecture-fidelity/skills/architecture-fidelity"
```

Or install the repository as a local Pi package:

```bash
pi install /absolute/path/to/architecture-fidelity
```

Invoke `/skill:architecture-fidelity` explicitly or allow Pi to select it from the task description.

## Suggested prompts

- `Use $architecture-fidelity to implement this feature without creating a parallel path.`
- `Decide whether this completed diff crosses the Architecture Fidelity significance gate; if it does, run the skill once before handoff.`
- `Review this diff for duplicated responsibilities, weak domain types, and missed extension seams.`
- `Initialize Architecture Fidelity project memory, then audit this repository.`
- `Run an incremental architecture audit and report only the lifecycle delta.`
- `Refactor these variants into the smallest justified abstraction while preserving compatibility.`

## Design stance

The goal is not more abstraction. It is fewer competing concepts, clearer ownership, and cheaper future change. Local duplication may be better than coupling unrelated responsibilities; composition is usually better than inheritance for independent variation; a plain function is often better than a class with no invariant. The skill asks agents to make those choices from repository evidence rather than habit.

## Repository assessment

Use `repo-review` to decide what a repository actually delivers, whether its claims hold up, and whether to adopt it, pilot it, borrow ideas, or pass. It loads only the requested lenses and keeps source findings distinct from deployment-dependent risks and unverified hypotheses. Reviews do not change the target repository or its architecture ledger.

For example:

```text
Use $repo-review to assess this repository's functionality, practical value, and security: <URL>
```

Codex and Pi installations that copy or link individual skills should include both `skills/repo-review` and `skills/architecture-fidelity`. The package manifests already discover the whole `skills/` directory. Claude Code exposes `/architecture-fidelity:repo-review`; Pi exposes `/skill:repo-review`.

For Copilot, copy `skills/repo-review` into your personal skills directory alongside `architecture-fidelity`. For optional repository routing, copy it into `.github/skills/` and install the adapters as described above. `prompts/repo-review.prompt.md` provides `/repo-review`; `agents/repo-review.agent.md` provides the repository assessment agent. Both route to the canonical skill without duplicating its review guidance.
