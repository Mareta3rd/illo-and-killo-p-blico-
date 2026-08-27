import base64
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from core.evidence_state import EvidenceState
from core.execution_artifact import read_execution_artifact
from core.real_evidence_provider import RealEvidenceProviderError
from scripts import run_groq_qwen_real_experiment as runner


KEY = "gag/001/composition/illo_primary"
IMAGE_BYTES = b"fake-image-bytes"
ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = {
    "characters": ["illo", "killo"],
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


class FakeResponses:
    def __init__(self, output_text=None, error=None):
        self.output_text = output_text
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return type("Response", (), {"output_text": self.output_text})()


class FakeClient:
    instances = []
    output_text = json.dumps({"observations": [{
        "claim_key": KEY,
        "statement": "The image is insufficient for a reliable observation.",
        "verdict": "unknown",
        "supporting_sources": [],
        "contradicting_sources": [],
    }]})

    def __init__(self, *, api_key=None, base_url=None, max_retries=None):
        self.api_key = api_key
        self.base_url = base_url
        self.max_retries = max_retries
        self.responses = FakeResponses(self.output_text)
        self.__class__.instances.append(self)


class GroqQwenRealExperimentTests(unittest.TestCase):
    def setUp(self):
        FakeClient.instances.clear()

    def run_cli(self, *extra_args, key="test-groq-secret"):
        with tempfile.NamedTemporaryFile(suffix=".png") as image:
            image.write(IMAGE_BYTES)
            image.flush()
            argv = ["run_groq_qwen_real_experiment.py", image.name, KEY, "--run-id", "run-001", *extra_args]
            output = io.StringIO()
            with patch.object(sys, "argv", argv), patch.dict(os.environ, {"GROQ_API_KEY": key}, clear=False), redirect_stdout(output):
                result = runner.main()
        return result, json.loads(output.getvalue()), image.name

    @patch.object(runner, "OpenAI", FakeClient)
    def test_cli_reads_image_and_outputs_one_structured_observation(self):
        result, output, image_name = self.run_cli()

        self.assertEqual(result, 0)
        self.assertEqual(output["model"], "qwen/qwen3.8-27b")
        self.assertEqual(output["image"], image_name)
        self.assertEqual(output["run_id"], "run-001")
        self.assertEqual(output["records"], [{
            "claim_key": KEY,
            "state": "UNKNOWN",
            "statement": "The image is insufficient for a reliable observation.",
            "supporting_sources": [],
            "contradicting_sources": [],
        }])
        output_text = json.dumps(output).lower()
        self.assertNotIn("decision", output_text)
        self.assertNotIn("accept", output_text)
        self.assertNotIn("continue", output_text)
        self.assertNotIn("human_review", output_text)
        client = FakeClient.instances[0]
        self.assertEqual(client.api_key, "test-groq-secret")
        self.assertEqual(client.max_retries, 0)
        content = client.responses.calls[0]["input"][0]["content"]
        self.assertEqual(content[1]["image_url"], "data:image/png;base64," + base64.b64encode(IMAGE_BYTES).decode())

    @patch.object(runner, "OpenAI", FakeClient)
    def test_model_and_endpoint_are_configurable(self):
        self.run_cli("--model", "qwen/qwen3.8-27b", "--base-url", "https://example.test/v1")

        client = FakeClient.instances[0]
        self.assertEqual(client.base_url, "https://example.test/v1")
        self.assertEqual(client.responses.calls[0]["model"], "qwen/qwen3.8-27b")

    @patch.object(runner, "OpenAI", FakeClient)
    def test_artifact_path_persists_the_existing_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "execution.json"
            result, output, image_name = self.run_cli("--artifact-path", str(artifact_path))

            artifact = read_execution_artifact(artifact_path)
            self.assertEqual(result, 0)
            self.assertEqual(artifact.run_id, "run-001")
            self.assertEqual(artifact.provider, "groq_qwen")
            self.assertEqual(artifact.model, "qwen/qwen3.8-27b")
            self.assertEqual(artifact.image, image_name)
            self.assertEqual(artifact.claims[0].claim_key, KEY)
            self.assertEqual(artifact.claims[0].state, EvidenceState.UNKNOWN)
            self.assertEqual(artifact.canonical_evaluations, ())
            self.assertIsNone(artifact.core_decision)
            self.assertNotIn("test-groq-secret", artifact_path.read_text(encoding="utf-8"))
            self.assertEqual(output["records"][0]["state"], "UNKNOWN")

    @patch.object(runner, "OpenAI", FakeClient)
    def test_without_artifact_path_keeps_current_output_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "missing.json"
            result, output, _ = self.run_cli()
            self.assertEqual(result, 0)
            self.assertEqual(output["records"][0]["claim_key"], KEY)
            self.assertFalse(artifact_path.exists())

    @patch.object(runner, "OpenAI", FakeClient)
    def test_invalid_artifact_path_is_a_clear_cli_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(SystemExit, "Unable to write execution artifact"):
                self.run_cli("--artifact-path", str(Path(directory) / "missing" / "run.json"))

    @patch.object(runner, "OpenAI", FakeClient)
    def test_provider_failures_reach_boundary_without_exposing_key(self):
        class ProviderFailure(Exception):
            status_code = 400
            code = "invalid_request"

        failure = ProviderFailure("request rejected")
        FakeClient.responses_error = failure

        def client_with_failure(**kwargs):
            client = FakeClient(**kwargs)
            client.responses.error = failure
            return client

        with patch.object(runner, "OpenAI", side_effect=client_with_failure):
            with self.assertRaises(RealEvidenceProviderError) as raised:
                self.run_cli(key="super-secret-groq-key")

        self.assertIn("ProviderFailure", str(raised.exception))
        self.assertNotIn("super-secret-groq-key", str(raised.exception))
        self.assertNotIn("accept", str(raised.exception).lower())
        self.assertNotIn("decision", str(raised.exception).lower())

    def test_groq_qwen_observation_snapshot_and_provider_metadata(self):
        client = FakeClient()
        observation, snapshot = runner.collect_groq_qwen_observation(
            client,
            model="qwen/qwen3.8-27b",
            image_bytes=IMAGE_BYTES,
            mime_type="image/png",
            claim_key=KEY,
            run_id="run-observation",
            root=ROOT,
        )

        self.assertEqual(observation.provider, "groq_qwen")
        self.assertEqual(observation.run_id, "run-observation")
        self.assertEqual(snapshot.get(KEY).state, EvidenceState.UNKNOWN)
        self.assertNotIn("provider", snapshot.claims)
        self.assertNotIn("run_id", snapshot.claims)
        self.assertEqual(snapshot.canonical_evaluations, ())

    def test_three_segment_states_reach_core_and_decision_is_core_owned(self):
        cases = (
            ("confirmed", EvidenceState.CONFIRMED, "accept"),
            ("unknown", EvidenceState.UNKNOWN, "human_review"),
            ("contradicted", EvidenceState.CONTRADICTED, "continue"),
        )
        for verdict, state, decision in cases:
            with self.subTest(verdict=verdict):
                FakeClient.output_text = json.dumps({"observations": [{
                    "claim_key": "fauna/mosquito_tigre/readable_as_mosquito",
                    "statement": f"Perceptual explanation for {verdict}.",
                    "verdict": verdict,
                    "supporting_sources": ["image"] if verdict == "confirmed" else [],
                    "contradicting_sources": ["image"] if verdict == "contradicted" else [],
                }]})
                result = runner.run_groq_qwen_evidence_pipeline(
                    FakeClient(),
                    idea="Crear un gag nuevo de Illo y Killo",
                    root=ROOT,
                    model="qwen/qwen3.8-27b",
                    image_bytes=IMAGE_BYTES,
                    mime_type="image/png",
                    claim_key="fauna/mosquito_tigre/readable_as_mosquito",
                    run_id=f"run-{verdict}",
                    proposal=PROPOSAL,
                )
                self.assertEqual(result.observation.records[0].state, state)
                self.assertEqual(result.snapshot.get("fauna/mosquito_tigre/readable_as_mosquito").state, state)
                self.assertEqual(result.pipeline.evaluation.evaluation.decision, decision)
                self.assertEqual(result.observation.records[0].supporting_sources, ("image",) if verdict == "confirmed" else ())
                self.assertEqual(result.observation.records[0].contradicting_sources, ("image",) if verdict == "contradicted" else ())
        FakeClient.output_text = json.dumps({"observations": [{
            "claim_key": KEY,
            "statement": "The image is insufficient for a reliable observation.",
            "verdict": "unknown",
            "supporting_sources": [],
            "contradicting_sources": [],
        }]})

    def test_gag001_four_segment_claim_remains_without_contract_evaluation(self):
        result = runner.run_groq_qwen_evidence_pipeline(
            FakeClient(),
            idea="Crear un gag nuevo de Illo y Killo",
            root=ROOT,
            model="qwen/qwen3.8-27b",
            image_bytes=IMAGE_BYTES,
            mime_type="image/png",
            claim_key=KEY,
            run_id="run-gag001",
            proposal=PROPOSAL,
        )
        self.assertEqual(result.snapshot.canonical_evaluations, ())


if __name__ == "__main__":
    unittest.main()