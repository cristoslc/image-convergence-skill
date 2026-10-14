# Developer Workflows

- **Test:** `python3 -m unittest discover -s tests -v` (offline, stdlib-only).
- **Deploy (staging):** `scripts/staging/deploy.sh <branch>` — prints the staging slot, then `scripts/staging/e2e.sh <branch>` verifies bit-for-bit identity with the repo bundle.
- **Deploy (production):** `IMGCONV_DEPLOY_ENV=production scripts/staging/deploy.sh main` writes the live slot; teardown script refuses production by design.
- **Teardown:** `scripts/staging/teardown.sh <branch>` removes only that branch's slot.
- **CI:** none wired yet; wire the unittest command as the first gate.
Detail in [`developer-workflows/README.md`](developer-workflows/README.md).
