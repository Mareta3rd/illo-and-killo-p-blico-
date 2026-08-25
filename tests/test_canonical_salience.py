import unittest

from core.canonical_salience import CanonicalSalience, NarrativeRole, VisualSalience


class CanonicalSalienceTests(unittest.TestCase):
    def test_narrative_roles_are_qualitative_and_ordered(self):
        self.assertLess(NarrativeRole.INCIDENTAL, NarrativeRole.SUPPORTING)
        self.assertLess(NarrativeRole.SUPPORTING, NarrativeRole.SECONDARY)
        self.assertLess(NarrativeRole.SECONDARY, NarrativeRole.PRIMARY)
        self.assertEqual(NarrativeRole.PRIMARY.label, "primary")

    def test_visual_salience_is_qualitative_and_ordered(self):
        self.assertLess(VisualSalience.LOW, VisualSalience.MEDIUM)
        self.assertLess(VisualSalience.MEDIUM, VisualSalience.HIGH)
        self.assertLess(VisualSalience.HIGH, VisualSalience.DOMINANT)
        self.assertEqual(VisualSalience.DOMINANT.label, "dominant")

    def test_profile_exposes_integer_weight_only_as_derived_rank(self):
        profile = CanonicalSalience(NarrativeRole.PRIMARY, VisualSalience.DOMINANT)
        self.assertEqual(profile.narrative_weight, 3)
        self.assertEqual(profile.visual_weight, 3)
        self.assertEqual(profile.narrative_role.label, "primary")
        self.assertEqual(profile.visual_salience.label, "dominant")


if __name__ == "__main__":
    unittest.main()
