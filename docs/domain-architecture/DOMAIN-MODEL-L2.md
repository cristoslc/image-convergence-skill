# Domain Model (L2)

Precise definitions, mirroring `engine/image_convergence.py` (the executable authority):

- **Attempt**: record {number: int >= 1, scores: map<dimension, 0-10>, tactic: menu-tactic, prompt: str, revision: str = ""}. Invariants: all five dimensions scored; `overall == min(scores.values())`.
- **Overall**: the convergence score of an attempt = min over dimensions.
- **Best**: `max(overall)` over the ledger so far.
- **Stall**: `attempts_since_improvement >= stall_limit` where `attempts_since_improvement` counts attempts after the most recent strictly-new best. A scored repeat (equal to the best) counts as flat, exactly as the prose's "flat or lower".
- **Decision** (in order): best >= threshold -> deliver(`converged`); ledger length >= max_attempts -> deliver(`attempt_cap`); stalled -> rotate to the next menu tactic, delivering(`tactics_exhausted`) when every menu tactic has appeared; otherwise regenerate on the current tactic (or `baseline-revision` on an empty ledger).
- **Holding window**: a new tactic is held at least 2 attempts before judging it; encoded in prose and pinned by tests as `HOLDING_WINDOW = 2`.
