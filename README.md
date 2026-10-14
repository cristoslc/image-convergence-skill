# image-convergence-skill

An agent skill that closes the loop on generated images. When an image comes back from any generation step, the agent reviews it against the **original prompt**, scores compliance across five dimensions, and keeps iterating — revising the prompt and regenerating — until the image **converges** (overall score at threshold) or an **attempt cap** ends the run.

The agent owns the loop: it assumes approval for each iteration, stops on the built-in stop conditions, changes tactics creatively when stalled, and delivers one result — the best image — with the attempt ledger that tells the story.

## The loop in one line

`generate -> review(score) -> revise(positive additions) -> generate ...` with a stall detector (three attempts without a new best) that rotates through six creative tactics, and three stop conditions (converged, cap, tactics exhausted).

## Layout

- `skill/image-convergence/SKILL.md` — the skill bundle (the product).
- `engine/image_convergence.py` — executable reference of the decision rule.
- `tests/` — decision tests + structural tests of the skill prose.
- `scripts/staging/{deploy,e2e,teardown}.sh` — filesystem-style two-stage pipeline.
- `docs/` — architecture and domain surfaces, see `docs/README.md`.

## Quick start

```bash
python3 -m unittest discover -s tests -v     # offline suite
scripts/staging/deploy.sh "$(git rev-parse --abbrev-ref HEAD)"   # stage the skill bundle
scripts/staging/e2e.sh "$(git rev-parse --abbrev-ref HEAD)"      # verify the staged copy
```

Install to the live skills dir: `IMGCONV_DEPLOY_ENV=production scripts/staging/deploy.sh main`.
