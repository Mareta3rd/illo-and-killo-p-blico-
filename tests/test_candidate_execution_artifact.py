import json
import tempfile
import unittest
from pathlib import Path

from core.candidate_execution_artifact import (
    build_candidate_execution_artifact,
    deserialize_candidate_execution_artifact,
    serialize_candidate_execution_artifact,
    write_candidate_execution_artifact,
    read_candidate_execution_artifact,
)
from core.loop import Evaluation, IterationRecord
from core.prompt_compiler import CompiledPrompt
from core.semantic_context import SemanticContext


class CandidateExecutionArtifactTests(unittest.TestCase):
    def setUp(self):
        self.prompt = CompiledPrompt(
            route="gag",
            task="Develop the requested gag.",
            constraints=("Preserve canon.",),
            checks=("Check invariants.",),
            context_summary=("legacy-context-summary",),
            semantic_context=SemanticContext(
                entries=(
                    "character=arsa; hands=black,3_finger; hooves=black,hoof",
                    "character=pisha; hands=black,3_finger; hooves=black,hoof",
                    "relationship=arsa_pisha; dynamics=mutual_trust,shared_mischief",
                    "historical_material=reference_only; excluded_from_active_canon",
                )
            ),
        )
        self.initial = {
            "characters": ["arsa", "pisha"],
            "elements": [{"id": "clavel", "intention": "character_identity"}],
        }
        self.iterations = (
            IterationRecord(
                1,
                {
                    "content": "Arsa starts a harmless gag.",
                    "characters": ["arsa", "pisha"],
                },
                Evaluation("continue", "needs another pass"),
            ),
            IterationRecord(
                2,
                {
                    "content": "Arsa and Pisha complete the gag.",
                    "characters": ["arsa", "pisha"],
                },
                Evaluation("accept", "candidate satisfies the Core checks"),
            ),
        )

    def build(self):
        return build_candidate_execution_artifact(
            run_id="qwen-audit-001",
            provider="groq_qwen_candidate",
            model="qwen/qwen3.8-27b",
            image="textual-run",
            idea="Create a new gag with Arsa and Pisha.",
            route="gag",
            compiled_prompt=self.prompt,
            loop_iterations=self.iterations,
            initial_candidate=self.initial,
            final_status="accepted",
            stop_reason=None,
            core_decision="accept",
        )

    def test_records_exact_compiled_context_and_each_request_prompt(self):
        artifact = self.build()

        self.assertIn("character=arsa", artifact.compiled_prompt)
        self.assertIn(
            "historical_material=reference_only; excluded_from_active_canon",
            artifact.semantic_context_entries,
        )
        self.assertEqual(len(artifact.iterations), 2)

        first = artifact.iterations[0]
        second = artifact.iterations[1]
        self.assertIn("PREVIOUS CANDIDATE (for reference/improvement):", first.request_prompt)
        self.assertIn("Arsa starts a harmless gag.", second.request_prompt)
        self.assertNotEqual(first.request_prompt_digest, second.request_prompt_digest)
        self.assertNotEqual(first.candidate_digest, second.candidate_digest)

    def test_round_trip_is_stable(self):
        artifact = self.build()
        payload = serialize_candidate_execution_artifact(artifact)
        loaded = deserialize_candidate_execution_artifact(payload)
        self.assertEqual(loaded, artifact)
        self.assertEqual(serialize_candidate_execution_artifact(loaded), payload)

    def test_file_persistence(self):
        artifact = self.build()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate-audit.json"
            write_candidate_execution_artifact(path, artifact)
            self.assertEqual(read_candidate_execution_artifact(path), artifact)

    def test_tampered_prompt_digest_is_rejected(self):
        payload = self.build().to_dict()
        payload["compiled_prompt_digest"] = "tampered"
        with self.assertRaises(ValueError):
            deserialize_candidate_execution_artifact(json.dumps(payload))

    def test_tampered_candidate_digest_is_rejected(self):
        payload = self.build().to_dict()
        payload["iterations"][0]["candidate_digest"] = "tampered"
        with self.assertRaises(ValueError):
            deserialize_candidate_execution_artifact(json.dumps(payload))

    def test_closed_schema_rejects_extra_fields(self):
        payload = self.build().to_dict()
        payload["secret"] = "do-not-accept"
        with self.assertRaises(ValueError):
            deserialize_candidate_execution_artifact(json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
