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
- avoid speculative frameworks, inheritance for code sharing, and abstractions with only superficial similarity;
- report material reuse, new abstractions, preserved boundaries, and deliberately deferred opportunities.

This is intentionally not a replacement for Ruff, formatters, type checkers, or static-analysis rules. Those tools own mechanical consistency. Architecture Fidelity owns repository-level design decisions that require understanding responsibilities, callers, and change pressure.

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
        └── references/
            ├── pattern-selection.md
            ├── python.md
            └── review-rubric.md
```

The single `SKILL.md` is canonical across all hosts. Product manifests only package that shared implementation.

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
- `Review this diff for duplicated responsibilities, weak domain types, and missed extension seams.`
- `Refactor these variants into the smallest justified abstraction while preserving compatibility.`

## Design stance

The goal is not more abstraction. It is fewer competing concepts, clearer ownership, and cheaper future change. Local duplication may be better than coupling unrelated responsibilities; composition is usually better than inheritance for independent variation; a plain function is often better than a class with no invariant. The skill asks agents to make those choices from repository evidence rather than habit.
