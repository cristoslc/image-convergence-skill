"""Structural tests for skill/image-convergence/SKILL.md.

These tests pin the contract the agent consumes: frontmatter, required
loop sections, the engine-mirrored thresholds, the tactic vocabulary, the
positive-only phrasing audit, and the deployment-agnostic guard.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_FILE = REPO_ROOT / "skill" / "image-convergence" / "SKILL.md"
sys.path.insert(0, str(REPO_ROOT / "engine"))

import image_convergence as ic  # noqa: E402


def load_skill_text() -> str:
    return SKILL_FILE.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        raise AssertionError("SKILL.md has no frontmatter block")
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


class FrontmatterTests(unittest.TestCase):
    def test_frontmatter_declares_name_and_description(self):
        fm = frontmatter(load_skill_text())
        self.assertEqual(fm.get("name"), "image-convergence")
        self.assertIn("original prompt", fm.get("description", ""))
        self.assertIn("autonomously", fm.get("description", ""))

    def test_frontmatter_description_mentions_iteration_control(self):
        desc = frontmatter(load_skill_text()).get("description", "")
        for phrase in ("iterate", "cap"):
            self.assertIn(phrase, desc, f"description omits '{phrase}'")


class RequiredSectionsTests(unittest.TestCase):
    REQUIRED_SECTIONS = (
        "## Definitions",
        "## Core loop on every attempt",
        "## Stall detection and tactic changes",
        "### Tactic menu (default order)",
        "## Stop conditions",
        "## Autonomy rules",
        "## Positive-only prompting",
    )

    def test_all_required_sections_present_in_order(self):
        text = load_skill_text()
        positions = [text.index(s) for s in self.REQUIRED_SECTIONS]
        self.assertEqual(positions, sorted(positions))

    def test_all_tactic_names_present_as_numbered_menu(self):
        text = load_skill_text()
        for i, tactic in enumerate(ic.TACTIC_MENU, start=1):
            self.assertRegex(text, rf"(?m)^{i}\. \*\*{re.escape(tactic)}\*\*", tactic)

    def test_delivery_names_stop_reason_and_final_prompt(self):
        text = load_skill_text()
        for phrase in ("stop reason", "final prompt"):
            self.assertIn(phrase, text)


class ThresholdMirrorTests(unittest.TestCase):
    """SKILL.md prose must state the same values the engine encodes."""

    def test_convergence_threshold_matches_engine(self):
        text = load_skill_text()
        self.assertRegex(text, rf"score is {int(ic.CONVERGENCE_THRESHOLD)} or higher")

    def test_attempt_cap_matches_engine(self):
        text = load_skill_text()
        self.assertIn("six attempts completed", text)
        self.assertEqual(6, ic.MAX_ATTEMPTS)

    def test_stall_limit_matches_engine(self):
        text = load_skill_text()
        self.assertIn(f"three consecutive attempts elapse", text)
        self.assertEqual(3, ic.STALL_LIMIT)

    def test_holding_window_matches_engine(self):
        text = load_skill_text()
        self.assertIn("at least two attempts", text)
        self.assertEqual(2, ic.HOLDING_WINDOW)


class PositivePhrasingTests(unittest.TestCase):
    """The loop instructs with positive guidance; the audit enforces it."""

    FORBIDDEN_PATTERNS = [
        r"\bdon'?t\b",
        r"\bdo not\b",
        r"\bnever\b",
        r"\bask (the |for )",
        r"\bpermission\b",
        r"\bwait for\b",
        r"\bstop\b(?=[^.]*?(?:ask|user))",
        r"\bunless\b",
        r"\bcannot\b",
    ]

    def test_no_negative_imperatives_in_skill(self):
        text = load_skill_text()
        for pattern in self.FORBIDDEN_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            self.assertEqual([], matches, f"forbidden pattern '{pattern}' hit")

    def test_autonomy_rules_state_preapproved_iteration(self):
        text = load_skill_text()
        self.assertIn("pre-approved work", text)
        self.assertIn("assume approval", text)

    def test_no_negative_prompt_channel_mentioned(self):
        """Changes are prompt-space additions; scoring terms stay positive."""
        text = load_skill_text().lower()
        self.assertNotIn("negative prompt", text)


class AgnosticismTests(unittest.TestCase):
    """The skill is model- and deployment-agnostic."""

    FORBIDDEN_FRAGMENTS = [
        "openai",
        "anthropic",
        "midjourney",
        "ollama",
        "http://",
        "https://",
        "/Users/",
        "localhost",
        "api key",
    ]

    def test_no_deployment_or_model_specific_leaks(self):
        text = load_skill_text().lower()
        for frag in self.FORBIDDEN_FRAGMENTS:
            self.assertNotIn(frag, text, f"leak: '{frag}'")


class CliInstallabilityTests(unittest.TestCase):
    """The Agent Skills CLI (`npx skills add`) must keep finding the bundle.

    The CLI discovers skills at standard container locations (`skills/`,
    repo root) and through plugin-manifest declared paths; our canonical
    `skill/` layout is published through the manifest entrypoint, so the
    manifest must exactly name the canonical path. A refactor that breaks
    either side silently drops the skill from CLI discovery.
    """

    MANIFEST_FILE = REPO_ROOT / ".claude-plugin" / "plugin.json"
    DECLARED_SKILL_PATH = "./skill/image-convergence"

    def test_entrypoint_manifest_declares_canonical_skill(self):
        manifest = json.loads(self.MANIFEST_FILE.read_text(encoding="utf-8"))
        self.assertIn(self.DECLARED_SKILL_PATH, manifest.get("skills", []))
        self.assertTrue(manifest.get("name"), "plugin manifest needs a name")

    def test_declared_path_resolves_to_canonical_bundle(self):
        relative = self.DECLARED_SKILL_PATH.removeprefix("./")
        self.assertEqual(SKILL_FILE, REPO_ROOT / relative / "SKILL.md")
        self.assertTrue((REPO_ROOT / relative / "SKILL.md").is_file())

    def test_declared_bundle_carries_required_frontmatter(self):
        fm = frontmatter(load_skill_text())
        self.assertEqual(fm.get("name"), "image-convergence")
        self.assertTrue(fm.get("description"), "description frontmatter is required")


if __name__ == "__main__":
    unittest.main()