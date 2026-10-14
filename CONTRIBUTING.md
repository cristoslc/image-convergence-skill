# Contributing

## Human process

- Open issues with the templates under `.github/ISSUE_TEMPLATE/` (blank issues are disabled).
- Branch naming: `<topic-slug>` for work branches; worktrees live in `.worktrees/` with the project root on `main`.
- Commit convention: imperative subject line, `DCO` signoff (`git commit -s`).
- PRs: fill `.github/PULL_REQUEST_TEMPLATE.md` verbatim; one logical change per PR.

## Agent requirements

- Read `AGENTS.md` before touching the repo; honor the scope guard and the prose-vs-engine lockstep rule stated there.
- The test command (`python3 -m unittest discover -s tests -v`) runs before every PR and green is a precondition for review.
- Agent-originated fixes arrive with reproduction steps and a failing test written before the fix.
- Skill-prose changes update `CHANGELOG.md` Unreleased in the same PR.
- Behavior changes to the loop rule land as an ADR in `docs/adr/` alongside the mirrored code+prose change.

## Review and merge policy

- A PR merges with one approval (operator for now) when tests pass and templates are filled; squash-merge with the branch subject.
