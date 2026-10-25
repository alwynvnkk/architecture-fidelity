# Safe Structural Moves

Use this reference when a change relocates, splits, or reshapes existing behavior rather than adding new behavior. It applies to extracting a pure core, moving policy behind an owner, splitting a read from a judgement, and consolidating duplicated logic.

The goal is a move whose correctness is demonstrated rather than argued. A refactor that cannot be shown to preserve behavior is a rewrite with an optimistic commit message.

## Pin the output before changing it

Write a characterisation test of the current function before editing, and generate its expected output from the existing code. It records what the code does, including behavior nobody intended.

- **Fake below the code that is going to move**, not the code itself. Fake the store readers, the clock, and the transport — not the functions about to be replaced. A fake of the moving function pins nothing once that function is gone.
- Prefer seeded real rows to fakes wherever the store allows it. A fake encodes the author's belief about the data; a seeded row encodes the data.
- Cover every branch and gate flipping on its own, plus one case where all of them pass. A pin in which every case fails the same way pins nothing — assert that the cases reach *different* outcomes.
- Run the pin against the unchanged code and read the output before trusting it.

A pin that was never run against the old code is a guess about the old code.

## Expect the pin to find bugs, and separate them

A characterisation pin on real code usually exposes latent defects. Fix each one in its own commit, before the move, and say in the message that the pin found it. A behavior fix smuggled inside a structural move destroys the only property that made the move verifiable.

If the defect must stay for compatibility, pin the current behavior and record why.

## Make the move, and accept only an unchanged pin

Perform the structural change and run the pin. The acceptance criterion is that the expected output does not change.

If it has to change, the move was not a pure move. Stop, and state exactly what changed and why, rather than updating the expected output to match the new code. Updating the pin to match the result being tested removes the test.

## Split a read from a judgement

When separating I/O from a decision:

- the **read** returns raw observations as plain data, with no derived value;
- the **judgement** is a pure function of those observations and its configuration, with no I/O and no clock;
- the original function becomes `judge(read(...))`.

There is then one implementation of the decision, so a check that also runs in another context — inside a transaction, at submission time, in a preview — cannot drift from it. Two copies of a rule drift silently; one implementation with two callers cannot.

Keep inputs that depend on the request out of the read, so one read serves every variant.

## Watch the shared-fake trap

Patching a reader onto a shared module replaces it for every caller in the process, including code the test is not about. Unrelated reads then silently observe test data.

Wrap the real reader and override only the ports under test, so everything else still sees real behavior.

## Delete what the pin proves is dead

Code the pin shows can never execute is removed in the same commit as the move, and named in the commit message. A retained unreachable branch is indistinguishable from a branch someone still depends on, and the next reader will preserve it.

Verify callers before removal; a pin covers the paths it exercises, not the whole repository.

## Checklist

- [ ] The pin ran against the unchanged code and its output was read.
- [ ] Fakes sit below the code being moved, not around it.
- [ ] Cases reach different outcomes, not one shared failure.
- [ ] Latent bugs the pin found were fixed in separate commits.
- [ ] The pin's expected output is unchanged after the move.
- [ ] Any required change to it is explained, not absorbed.
- [ ] Proven-dead code is deleted and named.
