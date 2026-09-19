import unittest
from pathlib import Path

from core.creative_feedback import build_creative_feedback


ROOT = Path(__file__).resolve().parents[1]


class CreativeFeedbackTests(unittest.TestCase):
    def test_new_mechanism_has_no_revision_finding(self):
        candidate = {
            "content": "Pisha tries to hide a beach umbrella and Arsa accidentally opens it indoors.",
            "characters": ["arsa", "pisha"],
            "elements": [
                {"id": "beach_umbrella", "intention": "comic_prop", "role": "scene_support"},
            ],
        }
        report = build_creative_feedback(candidate, root=ROOT)
        self.assertFalse(report.revision_required)

    def test_object_substitution_is_flagged_as_mechanism_reuse(self):
        candidate = {
            "content": "Arsa uses a chorizo like a boxing target, Pisha reacts to the punch.",
            "characters": ["arsa", "pisha"],
            "elements": [
                {"id": "chorizo", "intention": "comedic_prop_target", "role": "primary_comedic_object"},
                {"id": "pisha_reaction", "intention": "reaction", "role": "secondary"},
            ],
        }
        report = build_creative_feedback(candidate, root=ROOT)
        self.assertTrue(report.revision_required)
        self.assertTrue(any(item.code == "CREATIVE_OBJECT_SUBSTITUTION" for item in report.findings))
        self.assertTrue(any("causal mechanism" in item for item in report.guidance))

    def test_feedback_is_non_scoring_and_does_not_mutate_candidate(self):
        candidate = {
            "content": "Arsa punches a ham while Pisha reacts.",
            "characters": ["arsa", "pisha"],
            "elements": [
                {"id": "ham", "intention": "comedic_prop_target", "role": "primary_comedic_object"},
            ],
        }
        before = dict(candidate)
        report = build_creative_feedback(candidate, root=ROOT)
        self.assertTrue(report.findings)
        self.assertEqual(candidate, before)
        self.assertTrue(all(not isinstance(value, (int, float)) for value in report.__dict__.values()))


if __name__ == "__main__":
    unittest.main()
