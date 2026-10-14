# ADR-0001: Engine as decision-rule authority, weakest-link scoring, positive-only constraint

## Context

The loop needs one decision rule (convergence threshold, stall limit, attempt cap, tactic rotation, stop conditions) consumed by two renderings: prose for the agent, code for the test suite. Reviews also had to choose an overall-score semantic, and the phrasing discipline needed a definition precise enough to test.

## Options

- **Prose as authority** — simple, but thresholds drift silently between prose and tests.
- **Engine as authority, prose as mirror** — a small pure module defines the rule; structural tests assert the prose states the same values.
- **Interpreter** — a runtime that executes the loop; rejected, the agent is the executor and a runtime would be dead weight.

## Decision (adopted)

- `engine/image_convergence.py` is the authority. `SKILL.md` mirrors it; `ThresholdMirrorTests` pin threshold, cap, stall limit, holding window, and tactic vocabulary in both.
- **Weakest-link scoring:** the overall score is `min` across the five dimensions, so a single glaring miss holds the attempt back instead of hiding behind averages.
- **Positive-only, two senses:** (1) agent instructions state desired actions positively; the audit forbids negative-imperative vocabulary; (2) prompt revisions are additions in prompt space; the loop has no negative-prompt channel.
- Stale attempts after the last strictly-new best count toward the stall; equal scores count as flat ("flat or lower").

## Consequences

Rule changes are ADR-backed and land as mirrored prose+code+tests in one commit; the skill stays deployable anywhere the SKILL.md protocol is understood.
