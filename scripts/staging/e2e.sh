#!/usr/bin/env bash
# E2E verification of a staged (or production) image-convergence install.
#
# Identity: branch name ($1, matching the deploy.sh call). Recomputes the
# slot the same way deploy.sh does. Verifies the installed SKILL.md matches
# the in-repo bundle bit-for-bit and that the install parses as a skill.
set -euo pipefail

BRANCH="${1:?branch name required (the one passed to deploy.sh)}"

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${REPO_ROOT}/skill/image-convergence/SKILL.md"
SKILLS_DIR="${IMGCONV_SKILLS_DIR:-$HOME/.claude/skills}"
DEST="${SKILLS_DIR}/.staging-${BRANCH}/image-convergence/SKILL.md"
if [[ "${IMGCONV_DEPLOY_ENV:-staging}" == "production" ]]; then
  DEST="${SKILLS_DIR}/image-convergence/SKILL.md"
fi

if [[ ! -f "$DEST" ]]; then
  echo "FATAL: staged SKILL.md missing at ${DEST} — run scripts/staging/deploy.sh ${BRANCH} first" >&2
  exit 1
fi

if diff <(cat "$SRC") <(cat "$DEST") >/dev/null; then
  echo "OK: installed SKILL.md matches ${SRC#"$REPO_ROOT"/}"
else
  echo "FATAL: installed SKILL.md differs from ${SRC#"$REPO_ROOT"/} — run scripts/staging/deploy.sh ${BRANCH}" >&2
  exit 1
fi

python3 - "$DEST" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
assert re.match(r"^---\nname: image-convergence\n", text), "frontmatter missing or wrong skill name"
assert "## Autonomy rules" in text and "## Stop conditions" in text, "loop sections missing"
print("OK: SKILL.md parses with name=image-convergence and loop sections")
PY

echo "OK: e2e passed for staging slot ${DEST}"