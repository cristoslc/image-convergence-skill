# AGENTS.md — image-convergence-skill

This project holds the `image-convergence` agent skill: review a generated image for compliance with its original prompt, then iterate prompt + generation autonomously to convergence or the attempt cap. Read `PURPOSE.md` for the one-paragraph intent.

## Scope guard (project-defining constraint)

`skill/image-convergence/SKILL.md` MUST stay model- and deployment-agnostic: no vendor names, no hostnames, no API shapes, no model family pins, no instance-specific thresholds beyond the stated defaults. The skill teaches the review-and-iterate loop itself. Facts about how any specific image model or harness generates images belong in that system's own docs, never here. `tests/test_skill.py` enforces the forbidden-fragment list; when a new leak class appears, extend the list rather than soften it.

## Single source of truth: prose vs engine

`engine/image_convergence.py` is the authority on the loop decision rule (convergence threshold 8, stall limit 3, attempt cap 6, holding window 2, weakest-dimension overall score, tactic menu order). `SKILL.md` states the same rule in prose for the agent. The mirror tests in `tests/test_skill.py::ThresholdMirrorTests` compare them; a change to one surface MUST land with the matching change in the other in the same commit.

## Phrasing discipline

The skill operates on positive prompting only, in two senses, and both are test-enforced:

1. **Agent instructions:** behavioral clauses state the desired action positively ("assume approval and continue"), with the audit in `tests/test_skill.py::PositivePhrasingTests` forbidding negative imperative vocabulary (`don't`, `do not`, `never`, `ask for permission`, …).
2. **Image-model inputs:** every revision is an addition to the prompt text; the loop has no negative-prompt channel.

## Test command

```bash
python3 -m unittest discover -s tests -v
```

The suite runs offline: structural tests read `SKILL.md` as text, decision tests run the pure engine. Live end-to-end against a skills directory:

```bash
scripts/staging/deploy.sh "$(git rev-parse --abbrev-ref HEAD)"
scripts/staging/e2e.sh "$(git rev-parse --abbrev-ref HEAD)"
```

## Deployment scripts

`scripts/staging/{deploy.sh,e2e.sh,teardown.sh}` install, verify, and remove the skill bundle in a filesystem skills directory, using `IMGCONV_SKILLS_DIR` (default `~/.claude/skills`) and the branch name as the staging identity: staging installs under `.staging-<branch>/image-convergence/`, production (`IMGCONV_DEPLOY_ENV=production`) installs to the live `image-convergence/`. Missing env values fall back to documented defaults; deploy verifies the target path is written before returning. `teardown.sh` accepts the branch name and removes exactly that staging slot.