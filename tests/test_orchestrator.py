from pathlib import Path
import unittest

from core.evidence_state import EvidenceClaim, EvidenceState
from core.orchestrator import run_vertical_slice
from core.decision_provider import DecisionRequest, DecisionResult


ROOT = Path(__file__).resolve().parents[1]


INITIAL = {
    "characters": ["xoxo", "pisha"],
    "elements": [
        {"id": "clavel", "intention": "character_identity"},
        {"id": "black_spots", "count": 2, "intention": "character_identity"},
    ],
}

COMPLETE_EVIDENCE = {
    "intention": EvidenceClaim("intention", EvidenceState.CONFIRMED),
    "canon": EvidenceClaim("canon", EvidenceState.CONFIRMED),
    "coherence": EvidenceClaim("coherence", EvidenceState.CONFIRMED),
    "reuse_intention": EvidenceClaim("reuse", EvidenceState.CONFIRMED),
}


class OrchestratorTests(unittest.TestCase):

    def test_advisory_decision_is_exposed_without_authority(self):
        calls = []

        class AdvisoryProvider:
            def decide(self, request):
                calls.append(request)
                return DecisionResult(
                    request.question_id,
                    request.kind,
                    False,
                    "fixture",
                    0.8,
                )

        result = run_vertical_slice(
            "Crear un gag nuevo de Xoxo y Pisha",
            ROOT,
            lambda prompt, iteration, previous: {**INITIAL},
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL,
            decision_provider=AdvisoryProvider(),
        )

        self.assertFalse(result.stopped)
        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(result.advisory_decision.result.value, False)
        self.assertEqual(result.advisory_decision.result.provider_id, "fixture")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].question_id, "core.route.advisory")
        self.assertEqual(calls[0].kind, "boolean")
        self.assertEqual(calls[0].context["route"], result.pipeline.context.route)
        self.assertEqual(result.pipeline.context.route, "gag")
        self.assertIs(result.execution_audit.advisory_decision, result.advisory_decision)

    def test_no_provider_preserves_backward_compatible_behavior(self):
        result = run_vertical_slice(
            "Crear un gag nuevo de Xoxo y Pisha",
            ROOT,
            lambda prompt, iteration, previous: {**INITIAL},
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL,
        )

        self.assertIsNone(result.advisory_decision)
        self.assertIsNone(result.execution_audit.advisory_decision)

    def test_advisory_provider_failure_propagates(self):
        class BrokenProvider:
            def decide(self, request):
                raise RuntimeError("provider unavailable")

        with self.assertRaisesRegex(RuntimeError, "provider unavailable"):
            run_vertical_slice(
                "Crear un gag nuevo de Xoxo y Pisha",
                ROOT,
                lambda prompt, iteration, previous: {**INITIAL},
                evidence_claims=COMPLETE_EVIDENCE,
                initial_candidate=INITIAL,
                decision_provider=BrokenProvider(),
            )


    def test_vertical_slice_accepts_candidate(self):
        prompts = []

        def executor(prompt, iteration, previous):
            prompts.append(prompt)
            return {**INITIAL}

        result = run_vertical_slice(
            "Crear un gag nuevo de Xoxo y Pisha",
            ROOT,
            executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL,
        )

        self.assertFalse(result.stopped)
        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 1)
        self.assertIs(prompts[0], result.pipeline.compiled_prompt)

    def test_compiled_prompt_is_stable_across_iterations(self):
        prompts = []

        def executor(prompt, iteration, previous):
            prompts.append(prompt)
            if iteration == 1:
                return {
                    "characters": ["xoxo", "pisha"],
                    "elements": [
                        {"id": "clavel", "intention": "character_identity"},
                        {"id": "black_spots", "count": 1, "intention": "character_identity"},
                    ],
                }
            return {**INITIAL}

        result = run_vertical_slice(
            "Crear un gag nuevo de Xoxo y Pisha",
            ROOT,
            executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL,
            max_iterations=3,
        )

        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 2)
        self.assertIs(prompts[0], prompts[1])
        self.assertEqual(prompts[0].render(), prompts[1].render())

    def test_failed_candidate_continues_and_passes_previous_candidate(self):
        previous_values = []

        def executor(prompt, iteration, previous):
            previous_values.append(previous)
            if iteration == 1:
                return {
                    "characters": ["xoxo", "pisha"],
                    "elements": [
                        {"id": "clavel", "intention": "character_identity"},
                        {"id": "black_spots", "count": 1, "intention": "character_identity"},
                    ],
                }
            return {**INITIAL}

        result = run_vertical_slice(
            "Crear un gag nuevo de Xoxo y Pisha",
            ROOT,
            executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL,
            max_iterations=3,
        )

        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 2)
        self.assertEqual(previous_values[0], INITIAL)
        self.assertEqual(previous_values[1]["elements"][1]["count"], 1)

    def test_creative_feedback_requests_new_mechanism(self):
        prompts = []

        first = {
            "content": "Arsa uses a chorizo like a boxing target, Pisha reacts to the punch.",
            "characters": ["arsa", "pisha"],
            "elements": [
                {"id": "chorizo", "intention": "comedic_prop_target", "role": "primary_comedic_object"},
                {"id": "pisha_reaction", "intention": "reaction", "role": "secondary"},
                {"id": "clavel", "intention": "character_identity"},
                {"id": "black_spots", "count": 2, "intention": "character_identity"},
            ],
            "checks": {
                "intention": True,
                "canon": True,
                "coherence": True,
                "reuse_intention": True,
            },
        }
        second = {
            "characters": ["arsa", "pisha"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {"id": "black_spots", "count": 2, "intention": "character_identity"},
            ],
            "checks": {
                "intention": True,
                "canon": True,
                "coherence": True,
                "reuse_intention": True,
            },
        }

        def executor(prompt, iteration, previous):
            prompts.append(prompt)
            return first if iteration == 1 else second

        result = run_vertical_slice(
            "Crear un gag nuevo de Arsa y Pisha alrededor de un jamón",
            ROOT,
            executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=second,
            max_iterations=2,
        )

        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 2)
        self.assertNotEqual(prompts[0].render(), prompts[1].render())
        self.assertIn("CREATIVE ITERATION GUIDANCE:", prompts[1].render())
        self.assertTrue(result.audit_trail[0].creative_revision_required)

    def test_missing_evidence_blocks_before_loop(self):
        evidence = dict(COMPLETE_EVIDENCE)
        evidence.pop("reuse_intention")

        def executor(prompt, iteration, previous):
            raise AssertionError("executor must not run when Evidence is incomplete")

        result = run_vertical_slice(
            "Crear un gag nuevo de Xoxo y Pisha",
            ROOT,
            executor,
            evidence_claims=evidence,
            initial_candidate=INITIAL,
        )

        self.assertTrue(result.stopped)
        self.assertIsNone(result.loop)
        self.assertEqual(result.stop_reason, "evaluation_requires_human_review")
        self.assertIsNotNone(result.pipeline.evaluation)

    def test_unknown_evidence_blocks_before_loop(self):
        evidence = dict(COMPLETE_EVIDENCE)
        evidence["coherence"] = EvidenceClaim("coherence", EvidenceState.UNKNOWN)

        def executor(prompt, iteration, previous):
            raise AssertionError("executor must not run when Evidence requires review")

        result = run_vertical_slice(
            "Crear un gag nuevo de Xoxo y Pisha",
            ROOT,
            executor,
            evidence_claims=evidence,
            initial_candidate=INITIAL,
        )

        self.assertTrue(result.stopped)
        self.assertIsNone(result.loop)
        self.assertEqual(result.stop_reason, "evaluation_requires_human_review")
