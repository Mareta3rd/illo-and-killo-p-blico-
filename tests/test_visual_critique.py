import unittest

from core.visual_critique import (
    VISUAL_DIMENSIONS,
    VisualCritiqueReport,
    build_visual_critique,
    visual_critique_contract,
)


class VisualCritiqueTests(unittest.TestCase):
    def test_valid_findings_are_normalized_deterministically(self):
        report = build_visual_critique(
            [
                {"dimension": "production_fit", "state": "observed", "observation": "white background", "evidence": "edges fade cleanly", "confidence": "high", "guidance": "keep"},
                {"dimension": "character_fidelity", "state": "observed", "observation": "Arsa recognizable", "evidence": "white body, yellow crest, green scarf", "confidence": "high", "guidance": "retain"},
            ]
        )
        self.assertIsInstance(report, VisualCritiqueReport)
        self.assertEqual([item.dimension for item in report.findings], ["character_fidelity", "production_fit"])

    def test_duplicate_dimension_is_rejected(self):
        findings = [
            {"dimension": "gag_readability", "state": "observed", "observation": "ok", "evidence": "visible", "confidence": "high", "guidance": ""},
            {"dimension": "gag_readability", "state": "uncertain", "observation": "maybe", "evidence": "ambiguous", "confidence": "low", "guidance": ""},
        ]
        with self.assertRaises(ValueError):
            build_visual_critique(findings)

    def test_unknown_dimension_is_rejected(self):
        with self.assertRaises(ValueError):
            build_visual_critique([
                {"dimension": "aesthetic_quality", "state": "observed", "observation": "x", "evidence": "y", "confidence": "high", "guidance": ""}
            ])

    def test_unknown_observation_is_not_a_score(self):
        report = build_visual_critique([
            {"dimension": "motion_and_pose", "state": "uncertain", "observation": "gesture unclear", "evidence": "limb trajectory ambiguous", "confidence": "low", "guidance": "request another pass"}
        ])
        finding = report.findings[0]
        self.assertEqual(finding.state, "uncertain")
        self.assertEqual(finding.confidence, "low")
        self.assertNotIn("score", finding.__dict__)

    def test_missing_guidance_is_rejected(self):
        finding = {
            "dimension": "gag_readability",
            "state": "observed",
            "observation": "reads immediately",
            "evidence": "primary action is clear",
            "confidence": "high",
        }
        with self.assertRaises(ValueError):
            build_visual_critique([finding])

    def test_non_string_dimension_state_confidence_are_rejected(self):
        finding = {
            "dimension": ["gag_readability"],
            "state": "observed",
            "observation": "reads immediately",
            "evidence": "primary action is clear",
            "confidence": "high",
            "guidance": "",
        }
        with self.assertRaises(ValueError):
            build_visual_critique([finding])

    def test_contract_is_closed(self):
        schema = visual_critique_contract()
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["required"], ["findings"])
        item = schema["properties"]["findings"]["items"]
        self.assertFalse(item["additionalProperties"])
        self.assertEqual(item["properties"]["dimension"]["enum"], list(VISUAL_DIMENSIONS))


if __name__ == "__main__":
    unittest.main()
