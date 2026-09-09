import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from core.execution_artifact import read_execution_artifact
from scripts import run_gag001_gemini_experiment as runner


ROOT = Path(__file__).resolve().parents[1]
CLAIM = "gag/001/composition/xoxo_primary"


class FakeInteractions:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return type("Response", (), {"output_text": json.dumps({"observations": [{
            "claim_key": CLAIM,
            "statement": "The image is insufficient for a reliable observation.",
            "verdict": "unknown",
            "supporting_sources": [],
            "contradicting_sources": [],
        }]})})()


class FakeClient:
    instances = []

    def __init__(self):
        self.interactions = FakeInteractions()
        self.__class__.instances.append(self)


class GeminiRunnerArtifactTests(unittest.TestCase):
    def run_cli(self, *extra_args):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "image.png"
            image.write_bytes(b"image")
            argv = [
                "run_gag001_gemini_experiment.py",
                str(image),
                CLAIM,
                "--run-id",
                "gemini-run-001",
                *extra_args,
            ]
            output = io.StringIO()
            with patch.object(sys, "argv", argv), patch.object(runner.genai, "Client", FakeClient), patch.dict(
                os.environ, {"GEMINI_API_KEY": "test-key"}, clear=False
            ), redirect_stdout(output):
                result = runner.main()
            return result, json.loads(output.getvalue()), image

    def test_artifact_path_persists_the_existing_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "execution.json"
            result, output, image = self.run_cli("--artifact-path", str(artifact_path))

            artifact = read_execution_artifact(artifact_path)
            self.assertEqual(result, 0)
            self.assertEqual(output["observation"]["run_id"], "gemini-run-001")
            self.assertEqual(artifact.run_id, "gemini-run-001")
            self.assertEqual(artifact.provider, "gemini")
            self.assertEqual(artifact.model, "gemini-3.6-flash")
            self.assertEqual(artifact.image, str(image))
            self.assertEqual(artifact.claims[0].claim_key, CLAIM)
            self.assertEqual(artifact.claims[0].state.value, "UNKNOWN")
            self.assertEqual(artifact.canonical_evaluations, ())
            self.assertIsNone(artifact.core_decision)
            self.assertNotIn("test-key", artifact_path.read_text(encoding="utf-8"))

    def test_without_artifact_path_does_not_create_one(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "missing.json"
            result, _, _ = self.run_cli()
            self.assertEqual(result, 0)
            self.assertFalse(artifact_path.exists())

    def test_invalid_artifact_path_is_a_clear_cli_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(SystemExit, "Unable to write execution artifact"):
                self.run_cli("--artifact-path", str(Path(directory) / "missing" / "run.json"))


if __name__ == "__main__":
    unittest.main()
