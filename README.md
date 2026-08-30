# Architecture Fidelity

Architecture Fidelity is a shared agent skill for Codex, Claude Code, and Pi. It keeps feature work aligned with the codebase's existing responsibilities and extension seams as the system grows.

It addresses a recurring failure mode in agent-written code: the requested behavior works, but arrives as a parallel service, raw string option, duplicated branch, or new helper even though the repository already contains the right concept.

## What it adds

The skill makes architectural reconnaissance part of implementation and review:

- search by responsibility before adding types, modules, services, or dependencies;
- prefer reuse, extension, and evidence-backed generalization over parallel implementation;
- recognize semantic duplication in validation, state transitions, mappings, errors, and orchestration;
- choose composition, inheritance, interfaces, strategies, factories, value objects, or plain functions according to the actual variation;
- model closed domain choices with enums such as Python's `StrEnum` when compatibility permits;
- preserve dependency direction, public contracts, serialized values, and one source of truth;
- retain repository-side architectural memory so later audits revalidate changed surfaces instead of rediscovering the whole codebase;
- avoid speculative frameworks, inheritance for code sharing, and abstractions with only superficial similarity;
- report material reuse, new abstractions, preserved boundaries, and deliberately deferred opportunities.

This is intentionally not a replacement for Ruff, formatters, type checkers, or static-analysis rules. Those tools own mechanical consistency. Architecture Fidelity owns repository-level design decisions that require understanding responsibilities, callers, and change pressure.

## Automatic activation

The skill is implicitly invocable: Codex, Claude Code, and Pi can select it from its description without a human naming it. Its routing policy uses a significance gate rather than change frequency.

It should run once during planning when a task clearly introduces or changes a responsibility, domain concept, variant, orchestration or persistence flow, dependency boundary, shared policy, or multi-implementation abstraction. If that only becomes apparent during implementation, it should run once against the final diff before handoff or PR preparation.

It should not run after every edit, commit, test, or merely because a PR is approaching. Formatting, linting, generated output, documentation, copy, styles, lockfile- or version-only updates, mechanical renames, and genuinely isolated fixes take the fast path. Adding or replacing a runtime dependency still qualifies. Diff size alone does not decide: a one-line state transition may be architectural, while a large generated diff may not be.

For repositories that want the same policy reinforced in `AGENTS.md` or `CLAUDE.md`, use:

```markdown
Use the installed architecture-fidelity skill automatically when a task or its resulting diff changes responsibilities, domain types or closed states, variants, runtime dependencies, orchestration or persistence flows, dependency boundaries, shared policy, or multiple implementations. Invoke it once during planning when evident; otherwise once before handoff if those signals emerge. Do not invoke it per edit or for formatting, linting, generated files, docs/copy/styles, lockfile- or version-only updates, mechanical renames, or isolated fixes with no new concept or boundary change. Re-run only if the scope materially expands after the prior pass.
```

## Structure

```text
.
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── package.json
└── skills/
    └── architecture-fidelity/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── scripts/
        │   └── architecture_ledger.py
        └── references/
            ├── pattern-selection.md
            ├── project-ledger.md
            ├── python.md
            └── review-rubric.md
```

The single `SKILL.md` is canonical across all hosts. Product manifests only package that shared implementation.

## Project memory

Architecture Fidelity can keep a reviewable ledger at `.architecture-fidelity/ledger.json` in the repository being audited. It remembers both healthy architectural landmarks and finding lifecycles, while Git remains the source of truth.

Initialize it only when you want persistent project memory:

```bash
python3 /path/to/architecture-fidelity/skills/architecture-fidelity/scripts/architecture_ledger.py \
  --root /path/to/repository init
```

On later audits, the skill plans from the last completed commit, revalidates landmarks and findings whose anchors changed, carries untouched findings without calling them new, and recognizes resolved findings that regress. If the baseline is missing or invalid, it falls back to a full scan.

The helper also supports `validate`, `plan`, `fingerprint`, and `apply-delta`. The ledger is intentionally JSON plus a dependency-free Python helper: portable across Codex, Claude Code, and Pi, easy to review in pull requests, and small enough to replace later if project scale proves that necessary.

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
