import base64
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from core.real_evidence_provider import RealEvidenceProviderError
from scripts import run_groq_qwen_real_experiment as runner


KEY = "gag/001/composition/illo_primary"
IMAGE_BYTES = b"fake-image-bytes"


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

    def __init__(self, *, api_key, base_url, max_retries):
        self.api_key = api_key
        self.base_url = base_url
        self.max_retries = max_retries
        self.responses = FakeResponses(json.dumps({"observations": [{
            "claim_key": KEY,
            "statement": "Illo is the primary visual subject.",
            "verdict": "unknown",
            "supporting_sources": [],
            "contradicting_sources": [],
        }]}))
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
            "statement": "Illo is the primary visual subject.",
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


if __name__ == "__main__":
    unittest.main()