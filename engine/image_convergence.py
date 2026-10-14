"""Reference implementation of the image-convergence loop decision rule.

`skill/image-convergence/SKILL.md` states this rule in prose for the agent;
this module states it in code for the test suite. One decision rule, two
renderings: when the prose and the code drift apart, the structural tests
in `tests/test_skill.py` catch threshold drift, and this module is the
authority on behavior.

The module is dependency-free and pure: given the attempt ledger and the
loop parameters, `decide_next` returns the next action. It performs no
image work, no scoring, and no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, Tuple

TACTIC_MENU: Tuple[str, ...] = (
    "baseline-revision",
    "restructure",
    "scene-decomposition",
    "style-anchor",
    "concretize",
    "reseed",
)

CONVERGENCE_THRESHOLD = 8.0
STALL_LIMIT = 3
MAX_ATTEMPTS = 6
# Enforced in prose: each new tactic gets at least this many attempts
# before the judge looks at it. The decision rule holds a tactic via the
# stall counter, so this value is a documented cross-check surface.
HOLDING_WINDOW = 2
DIMENSIONS: Tuple[str, ...] = (
    "subject",
    "composition",
    "style",
    "detail",
    "palette-and-lighting",
)


@dataclass(frozen=True)
class Attempt:
    """One reviewed generation: per-dimension scores plus the tactic used."""

    number: int
    scores: dict[str, float]
    tactic: str
    prompt: str
    revision: str = ""

    @property
    def overall(self) -> float:
        """Convergence score: the weakest dimension holds the attempt back."""
        missing = [d for d in DIMENSIONS if d not in self.scores]
        if missing:
            raise ValueError(
                f"attempt {self.number} is missing scores for: {', '.join(missing)}"
            )
        return min(self.scores.values())


@dataclass(frozen=True)
class Decision:
    """What the loop does next, and why the rule produced it."""

    action: str  # "regenerate", "change_tactic", or "deliver"
    tactic: str | None
    stop_reason: str | None  # "converged", "attempt_cap", "tactics_exhausted"
    best_overall: float | None
    notes: list[str] = field(default_factory=list)


def best_score(ledger: Sequence[Attempt]) -> float | None:
    return max((a.overall for a in ledger), default=None)


def _current_tactic(ledger: Sequence[Attempt]) -> str | None:
    return ledger[-1].tactic if ledger else None


def _menu_index(tactic: str | None) -> int:
    if tactic is None:
        return -1
    return TACTIC_MENU.index(tactic)


def _attempts_since_improvement(ledger: Sequence[Attempt]) -> int:
    """Count attempts after the most recent new-best overall score."""
    last_improvement = -1
    for i, a in enumerate(ledger):
        if i == 0 or a.overall > max(x.overall for x in ledger[:i]):
            last_improvement = i
    return (len(ledger) - 1) - last_improvement


def decide_next(
    ledger: Sequence[Attempt],
    *,
    convergence_threshold: float = CONVERGENCE_THRESHOLD,
    stall_limit: int = STALL_LIMIT,
    max_attempts: int = MAX_ATTEMPTS,
) -> Decision:
    """Apply the loop rule to the ledger and return the next action.

    Order of evaluation: convergence, attempt cap, stall, plain regenerate.
    """
    best = best_score(ledger)

    if best is not None and best >= convergence_threshold:
        return Decision(
            action="deliver",
            tactic=None,
            stop_reason="converged",
            best_overall=best,
        )

    if ledger and len(ledger) >= max_attempts:
        return Decision(
            action="deliver",
            tactic=None,
            stop_reason="attempt_cap",
            best_overall=best,
        )

    attempts_since = _attempts_since_improvement(ledger)
    stalled = best is not None and attempts_since >= stall_limit

    if stalled:
        current = _current_tactic(ledger)
        next_index = (_menu_index(current) + 1) % len(TACTIC_MENU)
        tried = {a.tactic for a in ledger}
        if set(TACTIC_MENU) <= tried:
            return Decision(
                action="deliver",
                tactic=None,
                stop_reason="tactics_exhausted",
                best_overall=best,
                notes=[
                    "every menu tactic has had its turn and stalled; "
                    "delivering the best-scoring image"
                ],
            )
        notes = []
        if next_index == 0:
            notes.append(
                "reseed was the last menu tactic; rotating back to "
                "baseline-revision with accumulated ledger wording"
            )
        return Decision(
            action="change_tactic",
            tactic=TACTIC_MENU[next_index],
            stop_reason=None,
            best_overall=best,
            notes=notes,
        )

    return Decision(
        action="regenerate",
        tactic=_current_tactic(ledger) or TACTIC_MENU[0],
        stop_reason=None,
        best_overall=best,
    )