# Contribution Guidelines (agents)

- Read `AGENTS.md` (hub) first: scope guard, prose-vs-engine lockstep, phrasing discipline.
- Run `python3 -m unittest discover -s tests -v` before every PR; green is a precondition.
- Skill-rule changes: ADR in `docs/adr/` + mirrored prose, engine, and test changes in one commit.
- Fixes arrive with reproduction steps and a failing test written first.
- Worktrees under `.worktrees/`; project root stays on `main`.
- Every PR adds its `CHANGELOG.md` Unreleased entry.
