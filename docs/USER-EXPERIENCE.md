# User Experience

Users of this project are agents (and the operators who direct them).

- **Onboarding:** install the bundle into your skills dir (`scripts/staging/deploy.sh`); the harness picks it up by description trigger.
- **Interface shape:** one skill file, self-contained; the agent runs the loop and returns one delivery — best image, ledger, stop reason, final prompt.
- **Promises:** the loop stops by itself (converged, cap, or tactics exhausted); every mid-loop change appears in the ledger; review language stays positive.
