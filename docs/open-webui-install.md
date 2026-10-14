# Installing the skill in Open WebUI

Open WebUI v0.11 stores each skill as one row: `id`, `name`, `description`, `content` (a single markdown blob), `meta.tags`, `is_active`, `access_grants`. A mentioned skill inlines its `content` in full, so the blob is the whole install. There is no references-folder mechanism; the blob is self-contained.

## Content blob decision

The bundle is `skill/image-convergence/SKILL.md`. The install mirrors its YAML frontmatter into the row columns and puts the body in `content`:

- `name` (`image-convergence`) → row `name` and row `id`. Both matter: the `id` is the mention path.
- `description` → row `description`, verbatim.
- Body (everything after the frontmatter block, starting with the `# Image Convergence Loop` heading) → row `content`, byte for byte; the install is the SKILL.md body as-is.
- The frontmatter block itself is stripped: its two fields live in the row columns, and YAML packaging inside a mention-inlined blob carries nothing a chat can use.
- `meta.tags` → `["image-generation", "review-loop"]`; `is_active` → `true`; `access_grants` follows the API defaults.

## Create — one run per instance

Requires the OWUI API with a key of the administrator role or `workspace.skills` permission. Base URL and key come from the environment; they never belong in a file.

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

The script needs only the Python standard library. It fetches SKILL.md from GitHub (main), strips the frontmatter, and posts the row.

## Verify, update, delete

```bash
# verify: the row exists, is active, and the blob starts with the loop heading
curl -fsS -H "Authorization: Bearer $OWUI_API_KEY" \
  "$OWUI_BASE_URL/api/v1/skills/id/image-convergence" \
  | jq -r '.name, .is_active, (.content | startswith("# Image Convergence Loop"))'
# -> image-convergence, true, true

# update (after a skill-prose change): POST the same create payload to the /update endpoint, id unchanged
curl -fsS -X POST -H "Authorization: Bearer $OWUI_API_KEY" -H "Content-Type: application/json" \
  -d "$( [paste the same JSON payload] )" \
  "$OWUI_BASE_URL/api/v1/skills/id/image-convergence/update"

# delete
curl -fsS -X DELETE -H "Authorization: Bearer $OWUI_API_KEY" \
  "$OWUI_BASE_URL/api/v1/skills/id/image-convergence/delete"
```

## Using it in chat

Mention the skill with `<$image-convergence|label>…</image-convergence>` in a chat message; the full content blob inlines into the system prompt for that turn. Attach it permanently to a model through the model's `meta.skillIds`.