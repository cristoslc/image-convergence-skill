#!/usr/bin/env bash
# Install the image-convergence skill bundle into a filesystem skills dir.
#
# Staging identity is the branch name ($1, default: current branch).
#
# Env:
#   IMGCONV_SKILLS_DIR    target skills root. Default: ~/.claude/skills
#   IMGCONV_DEPLOY_ENV    "staging" (default) or "production".
#                         Staging  -> <skills>/.staging-<branch>/image-convergence/
#                         Production -> <skills>/image-convergence/
set -euo pipefail

BRANCH="${1:-$(git rev-parse --abbrev-ref HEAD)}"
: "${BRANCH:?branch name is required (pass it or run inside the repo)}"

IMGCONV_DEPLOY_ENV="${IMGCONV_DEPLOY_ENV:-staging}"
case "$IMGCONV_DEPLOY_ENV" in
  staging)    SLOT="image-convergence"; DEST_SUB=".staging-${BRANCH}" ;;
  production) SLOT="image-convergence"; DEST_SUB="" ;;
  *) echo "FATAL: IMGCONV_DEPLOY_ENV must be staging or production, got '${IMGCONV_DEPLOY_ENV}'" >&2; exit 1 ;;
esac

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${REPO_ROOT}/skill/image-convergence"
SKILLS_DIR="${IMGCONV_SKILLS_DIR:-$HOME/.claude/skills}"
DEST="${SKILLS_DIR}/${DEST_SUB:+${DEST_SUB}/}${SLOT}"

if [[ ! -f "${SRC}/SKILL.md" ]]; then
  echo "FATAL: skill bundle not found at ${SRC}/SKILL.md" >&2
  exit 1
fi

mkdir -p "$DEST"
cp "${SRC}/SKILL.md" "${DEST}/SKILL.md"

diff <(cat "${SRC}/SKILL.md") <(cat "${DEST}/SKILL.md") >/dev/null || {
  echo "FATAL: install verification failed: ${DEST}/SKILL.md differs from source" >&2
  exit 1
}

echo "$DEST"
echo "OK: staged image-convergence at ${DEST} (env=${IMGCONV_DEPLOY_ENV}, branch=${BRANCH})"