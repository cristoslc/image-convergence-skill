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

## Open WebUI (OWUI) installation

Verified OWUI v0.11 skill facts: one row per skill — `id`, `name`, `description`, `content` (a single markdown blob), `meta.tags`, `is_active`, `access_grants`; no references-folder mechanism; mentioned content inlines in full.

Content blob decision: the row carries the frontmatter's `name` and `description` in its own columns, and the SKILL.md body (everything after the frontmatter block) in `content`, byte for byte. The YAML frontmatter block itself is stripped from the blob. The row `id` is `image-convergence` (the frontmatter name); the mention path depends on it, so the id stays fixed while the prose evolves.

- Mention in chat: `<$image-convergence|label>` … `</image-convergence>`; model attachment via the model's `meta.skillIds`.
- API endpoints (requires the OWUI administrator role or `workspace.skills` permission), with `OWUI_BASE_URL` and `OWUI_API_KEY` sourced from the environment: `POST ${OWUI_BASE_URL%/}/api/v1/skills/create`, `GET ${OWUI_BASE_URL%/}/api/v1/skills/id/{id}`, `POST ${OWUI_BASE_URL%/}/api/v1/skills/id/{id}/update`, `DELETE ${OWUI_BASE_URL%/}/api/v1/skills/id/{id}/delete`.
- Create/update payload shape: `{"id","name","description","content","meta":{"tags":[...]}}` plus `is_active: true`; `access_grants` follows the API defaults.
- Full create/verify/update/delete walkthrough: `docs/open-webui-install.md`.

## Agent Skills CLI entrypoint

`npx skills add cristoslc/image-convergence-skill` discovers the bundle through the plugin-manifest entrypoint `.claude-plugin/plugin.json`, whose `skills` array declares `./skill/image-convergence` — the canonical path above. Refactor the manifest and the bundle path together in the same commit; `tests/test_skill.py::CliInstallabilityTests` pins the manifest-to-path contract.

## Deployment scripts

`scripts/staging/{deploy.sh,e2e.sh,teardown.sh}` install, verify, and remove the skill bundle in a filesystem skills directory, using `IMGCONV_SKILLS_DIR` (default `~/.claude/skills`) and the branch name as the staging identity: staging installs under `.staging-<branch>/image-convergence/`, production (`IMGCONV_DEPLOY_ENV=production`) installs to the live `image-convergence/`. Missing env values fall back to documented defaults; deploy verifies the target path is written before returning. `teardown.sh` accepts the branch name and removes exactly that staging slot.