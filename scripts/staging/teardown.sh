#!/usr/bin/env bash
# Remove one staged install of the image-convergence skill.
#
# Identity: branch name ($1, matching the deploy.sh call). Production
# installs refuse teardown in this script (that slot belongs to the
# operator, never to a CI run).
set -euo pipefail

BRANCH="${1:?branch name required (the one passed to deploy.sh)}"
if [[ "${IMGCONV_DEPLOY_ENV:-staging}" == "production" ]]; then
  echo "FATAL: teardown refuses the production slot; remove ${IMGCONV_SKILLS_DIR:-$HOME/.claude/skills}/image-convergence by hand when intended" >&2
  exit 1
fi

SKILLS_DIR="${IMGCONV_SKILLS_DIR:-$HOME/.claude/skills}"
DEST="${SKILLS_DIR}/.staging-${BRANCH}/image-convergence"

if [[ -d "$DEST" ]]; then
  rm -rf "$DEST"
  rmdir "${SKILLS_DIR}/.staging-${BRANCH}" 2>/dev/null || true
  echo "OK: removed staging slot for branch ${BRANCH} (${DEST})"
else
  echo "OK: staging slot for branch ${BRANCH} already absent (${DEST})"
fi