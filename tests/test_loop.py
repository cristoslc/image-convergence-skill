"""Decision-rule tests for engine/image_convergence.py.

Each case maps to a loop rule in SKILL.md. The suite covers the happy,
sad, edge, and corner shapes of: convergence, the attempt cap, stall
detection, tactic rotation, tactics-exhausted, and the weakest-dimension
overall score.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "engine"))

from image_convergence import (  # noqa: E402
    Attempt,
    TACTIC_MENU,
    decide_next,
)


def scores(value: float) -> dict[str, float]:
    return {d: value for d in (
        "subject", "composition", "style", "detail",
        "palette-and-lighting",
    )}


def attempt(n: int, overall: float, tactic: str = "baseline-revision") -> Attempt:
    # Give one dimension the low value and the rest a passing value so
    # the attempt sits at `overall` when the weakest link wins.
    scores_dict = {d: overall for d in scores(overall)}
    return Attempt(number=n, scores=scores_dict, tactic=tactic, prompt="p")


def flat_ledger(values: list[float]) -> list[Attempt]:
    return [attempt(i + 1, v) for i, v in enumerate(values)]


class ConvergenceTests(unittest.TestCase):
    def test_threshold_reached_delivers_as_converged(self):
        d = decide_next(flat_ledger([6.0, 7.5, 8.0]))
        self.assertEqual(("deliver", "converged"), (d.action, d.stop_reason))

    def test_above_threshold_delivers_on_first_attempt(self):
        d = decide_next(flat_ledger([9.0]))
        self.assertEqual("converged", d.stop_reason)

    def test_one_weak_dimension_holds_the_attempt_back(self):
        a = Attempt(
            number=1,
            scores={**scores(9.0), "detail": 6.0},
            tactic="baseline-revision",
            prompt="p",
        )
        self.assertEqual(6.0, a.overall)
        d = decide_next([a])
        self.assertEqual("regenerate", d.action)


class RegenerateTests(unittest.TestCase):
    def test_empty_ledger_starts_baseline_revision(self):
        d = decide_next([])
        self.assertEqual(("regenerate", "baseline-revision"), (d.action, d.tactic))

    def test_below_threshold_with_fresh_improvement_keeps_tactic(self):
        d = decide_next(flat_ledger([6.0, 7.0]))
        self.assertEqual("regenerate", d.action)
        self.assertEqual("baseline-revision", d.tactic)


class StallTests(unittest.TestCase):
    def test_three_flat_attempts_after_best_triggers_tactic_change(self):
        # Best 7.0 at attempt 2, then 7.0, 7.0, 7.0 -> three elapsed.
        d = decide_next(flat_ledger([6.0, 7.0, 7.0, 7.0, 7.0]))
        self.assertEqual("change_tactic", d.action)
        self.assertEqual("restructure", d.tactic)

    def test_score_drop_without_new_best_counts_toward_stall(self):
        d = decide_next(flat_ledger([7.0, 6.0, 5.0, 4.0]))
        self.assertEqual("change_tactic", d.action)

    def test_fresh_best_resets_the_stall_counter(self):
        # Each attempt sets a new best, so the counter never reaches 3.
        d = decide_next(flat_ledger([5.0, 6.0, 7.0, 7.5]))
        self.assertEqual("regenerate", d.action)

    def test_two_flat_attempts_hold_short_of_stall(self):
        d = decide_next(flat_ledger([7.0, 7.0, 7.0]))
        self.assertEqual("regenerate", d.action)

    def test_rotation_follows_menu_order_from_current_tactic(self):
        ledger = [attempt(i + 1, 5.0, tactic=t)
                  for i, t in enumerate(TACTIC_MENU[:3])]
        d = decide_next(ledger)
        self.assertEqual("scene-decomposition", d.tactic)


class TacticsExhaustedTests(unittest.TestCase):
    def test_full_menu_cycle_with_no_best_change_delivers(self):
        # Best 5.0 at attempt 1, then every menu tactic gets an attempt
        # and stalls; with the cap relaxed the menu itself exhausts.
        ledger = [attempt(i + 1, 5.0, tactic=t) for i, t in enumerate(TACTIC_MENU)]
        d = decide_next(ledger, max_attempts=7)
        self.assertEqual(("deliver", "tactics_exhausted"), (d.action, d.stop_reason))
        self.assertEqual(5.0, d.best_overall)

    def test_partial_menu_rotation_with_stall_rotates_instead(self):
        # Only three tactics tried so far; rotation keeps going.
        ledger = [attempt(i + 1, 5.0, tactic=t) for i, t in enumerate(TACTIC_MENU[:3])]
        ledger += [attempt(4, 5.0, tactic=TACTIC_MENU[2])]
        d = decide_next(ledger, max_attempts=7)
        self.assertEqual("change_tactic", d.action)

    def test_reseed_rotation_returns_to_baseline_with_note(self):
        ledger = [attempt(1, 9.0, tactic="baseline-revision")]
        ledger += [attempt(2, 9.0, tactic="reseed"),
                   attempt(3, 9.0, tactic="reseed"),
                   attempt(4, 9.0, tactic="reseed")]
        d = decide_next(ledger, convergence_threshold=10.0, max_attempts=7)
        self.assertEqual("change_tactic", d.action)
        self.assertEqual("baseline-revision", d.tactic)
        self.assertTrue(d.notes)


class AttemptCapTests(unittest.TestCase):
    def test_cap_reached_delivers_best_below_threshold(self):
        d = decide_next(flat_ledger([5.0] * 6))
        self.assertEqual(("deliver", "attempt_cap"), (d.action, d.stop_reason))

    def test_cap_evaluates_after_convergence(self):
        d = decide_next(flat_ledger([8.0] * 6))
        self.assertEqual("converged", d.stop_reason)

    def test_empty_ledger_hits_cap_never(self):
        self.assertEqual("regenerate", decide_next([]).action)

    def test_operator_cap_tightens_delivery(self):
        d = decide_next(flat_ledger([5.0, 5.0, 5.0]), max_attempts=3)
        self.assertEqual("attempt_cap", d.stop_reason)


class EdgeAndCornerTests(unittest.TestCase):
    def test_missing_dimension_fails_loud(self):
        a = Attempt(
            number=1,
            scores={"subject": 5.0},
            tactic="baseline-revision",
            prompt="p",
        )
        with self.assertRaises(ValueError):
            _ = a.overall


if __name__ == "__main__":
    unittest.main()