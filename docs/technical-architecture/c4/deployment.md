# Deployment (C4: deployment)

One artifact, two install slots in a filesystem skills directory:

- **Staging:** `<skills>/.staging-<branch>/image-convergence/SKILL.md` — written by `scripts/staging/deploy.sh <branch>`, verified by `e2e.sh <branch>`, removed by `teardown.sh <branch>`. Production (`IMGCONV_DEPLOY_ENV=production`) writes `<skills>/image-convergence/SKILL.md` and refuses teardown by script.
- Nothing runs as a service; the "deployment" is a file copy with diff verification.
