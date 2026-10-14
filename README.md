# image-convergence-skill

An agent skill that closes the loop on generated images. When an image comes back from any generation step, the agent reviews it against the **original prompt**, scores compliance across five dimensions, and keeps iterating — revising the prompt and regenerating — until the image **converges** (overall score at threshold) or an **attempt cap** ends the run.

The agent owns the loop: it assumes approval for each iteration, stops on the built-in stop conditions, changes tactics creatively when stalled, and delivers one result — the best image — with the attempt ledger that tells the story.

## The loop in one line

`generate -> review(score) -> revise(positive additions) -> generate ...` with a stall detector (three attempts without a new best) that rotates through six creative tactics, and three stop conditions (converged, cap, tactics exhausted).

## Install

One command installs the bundle into any supported agent harness ([Agent Skills CLI](https://skills.sh)):

```bash
npx skills add cristoslc/image-convergence-skill
```

Add `-a <agent>` to target one harness (for example `-a claude-code` or `-a opencode`), `-g` for a user-wide install, or `--copy` to copy files instead of symlinking. The CLI discovers the skill through the manifest at `.claude-plugin/plugin.json`, which points at the canonical bundle path `skill/image-convergence/SKILL.md`.

## Install in Open WebUI

Open WebUI (v0.11) stores a skill as one row. The install mirrors the SKILL.md YAML frontmatter into the row's `name`/`description` columns, strips the frontmatter from the blob, and posts the body (`# Image Convergence Loop` onward) verbatim as the row's `content`. Mention it in chat with `<$image-convergence|label>` … `</image-convergence>`.

Create it once per instance (admin key with `workspace.skills` permission; standard library only):

```bash
export OWUI_BASE_URL=https://chat.example.com   # your instance
export OWUI_API_KEY=sk-...                      # admin key
python3 - <<'PY'
import json, os, re, urllib.request
raw = urllib.request.urlopen(
    "https://raw.githubusercontent.com/cristoslc/image-convergence-skill/main/skill/image-convergence/SKILL.md"
).read().decode()
m = re.match(r"^---\n(.*?)\n---\n", raw, re.DOTALL)
fm, content = {}, raw[m.end():]
for line in m.group(1).splitlines():
    key, _, value = line.partition(":")
    fm[key.strip()] = value.strip()
payload = {
    "id": fm["name"],
    "name": fm["name"],
    "description": fm["description"],
    "content": content,
    "meta": {"tags": ["image-generation", "review-loop"]},
    "is_active": True,
}
req = urllib.request.Request(
    os.environ["OWUI_BASE_URL"].rstrip("/") + "/api/v1/skills/create",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": "Bearer " + os.environ["OWUI_API_KEY"],
        "Content-Type": "application/json",
    },
    method="POST",
)
with urllib.request.urlopen(req) as res:
    print(res.status, json.loads(res.read()).get("id"))
PY
```

Verify, update, and delete commands: [docs/open-webui-install.md](docs/open-webui-install.md).

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
