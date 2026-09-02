import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_groq_qwen_candidate.py"
SPEC = importlib.util.spec_from_file_location("run_groq_qwen_candidate", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FakeOpenAI:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.calls = 0

    def __call__(self, *args, **kwargs):
        return self


class FakeResult:
    def __init__(self, *, stopped=False, stop_reason=None, core=None, artifact=None):
        self.stopped = stopped
        self.stop_reason = stop_reason
        self.core = core
        self.artifact = artifact


class GroqQwenCandidateRunnerTests(unittest.TestCase):
    def test_cli_defaults(self):
        args = MODULE.build_argument_parser().parse_args([
            "Crear un gag con Illo y Killo",
            "--run-id",
            "run-01",
        ])
        self.assertEqual(args.model, MODULE.DEFAULT_GROQ_QWEN_CANDIDATE_MODEL)
        self.assertEqual(args.base_url, MODULE.DEFAULT_GROQ_BASE_URL)
        self.assertEqual(args.idea, "Crear un gag con Illo y Killo")
        self.assertEqual(args.run_id, "run-01")

    def test_build_application_request_injects_executor(self):
        fake_client = object()
        request = MODULE.build_application_request(
            "Crear un gag",
            "run-002",
            "qwen/qwen3.8-27b",
            proposal={"characters": ["illo"], "elements": []},
            claim_keys=("gag/001/composition/illo_primary",),
            artifact_path=Path("artifact.json"),
            client=fake_client,
        )

        self.assertEqual(request.run_id, "run-002")
        self.assertEqual(request.proposal["characters"], ["illo"])
        self.assertEqual(request.requested_claims, ("gag/001/composition/illo_primary",))
        self.assertEqual(request.artifact_path, Path("artifact.json"))
        self.assertIsNotNone(request.executor)
        self.assertEqual(request.model, "qwen/qwen3.8-27b")

    def test_main_runs_application_once(self):
        fake_result = FakeResult(stopped=False, core=None, artifact=None)
        with patch.object(MODULE, "OpenAI", return_value=object()), patch.object(MODULE, "run_application", return_value=fake_result) as run_mock:
            with patch.dict(os.environ, {"GROQ_API_KEY": "secret"}, clear=False):
                code = MODULE.main([
                    "Crear un gag",
                    "--run-id",
                    "run-003",
                ])
        self.assertEqual(code, 0)
        self.assertEqual(run_mock.call_count, 1)

    def test_main_prints_safe_summary_without_secret_values(self):
        fake_result = FakeResult(
            stopped=False,
            stop_reason=None,
            core=SimpleNamespace(
                loop=SimpleNamespace(iterations=[SimpleNamespace(evaluation=SimpleNamespace(decision="accept"))]),
                pipeline=SimpleNamespace(evaluation=SimpleNamespace(evaluation=SimpleNamespace(decision="accept"))),
            ),
            artifact={"ok": True},
        )
        with patch.object(MODULE, "OpenAI", return_value=object()), patch.object(MODULE, "run_application", return_value=fake_result):
            with patch.dict(os.environ, {"GROQ_API_KEY": "super-secret"}, clear=False):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = MODULE.main([
                        "Crear un gag",
                        "--run-id",
                        "run-004",
                    ])
        output = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn('"model":', output)
        self.assertIn('"run_id": "run-004"', output)
        self.assertIn('"core_decision": "accept"', output)
        self.assertIn('"attention": null', output)
        self.assertNotIn("super-secret", output)
        self.assertNotIn("Authorization", output)
        self.assertNotIn("GROQ_API_KEY", output)

    def test_missing_groq_api_key_exits(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as exc:
                MODULE.main([
                    "Crear un gag",
                    "--run-id",
                    "run-005",
                ])
        self.assertIn("GROQ_API_KEY", str(exc.exception))

    def test_provider_error_exits_after_client_initialization(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "secret"}, clear=False):
            with patch.object(MODULE, "OpenAI", side_effect=RuntimeError("provider unavailable")):
                with self.assertRaises(SystemExit) as exc:
                    MODULE.main([
                        "Crear un gag",
                        "--run-id",
                        "run-006",
                    ])
        self.assertIn("Groq Qwen candidate runner failed", str(exc.exception))

    def test_artifact_path_is_forwarded(self):
        captured = {}

        def run_application(request):
            captured["artifact_path"] = request.artifact_path
            return FakeResult(stopped=False, core=None, artifact=None)

        with patch.object(MODULE, "OpenAI", return_value=object()), patch.object(MODULE, "run_application", side_effect=run_application):
            with patch.dict(os.environ, {"GROQ_API_KEY": "secret"}, clear=False):
                MODULE.main([
                    "Crear un gag",
                    "--run-id",
                    "run-007",
                    "--artifact-path",
                    "tmp_artifact.json",
                ])
        self.assertEqual(captured["artifact_path"], Path("tmp_artifact.json"))

    def test_proposal_json_is_loaded_and_injected(self):
        captured = {}

        def run_application(request):
            captured["proposal"] = request.proposal
            return FakeResult(stopped=False, core=None, artifact=None)

        proposal = {"characters": ["illo", "killo"], "elements": []}
        with patch.object(MODULE, "OpenAI", return_value=object()), patch.object(MODULE, "run_application", side_effect=run_application):
            with patch.dict(os.environ, {"GROQ_API_KEY": "secret"}, clear=False):
                MODULE.main([
                    "Crear un gag",
                    "--run-id",
                    "run-008",
                    "--proposal",
                    json.dumps(proposal),
                ])
        self.assertEqual(captured["proposal"], proposal)

    def test_summary_uses_core_decision_without_recalculation(self):
        fake_core = SimpleNamespace(
            loop=SimpleNamespace(iterations=[SimpleNamespace(evaluation=SimpleNamespace(decision="human_review"))]),
            pipeline=SimpleNamespace(evaluation=None),
        )
        result = FakeResult(stopped=True, stop_reason="prompt_blocked", core=fake_core)
        summary = MODULE._safe_result_summary(result)
        self.assertEqual(summary["core_decision"], "human_review")
        self.assertEqual(summary["iterations"], 1)

    def test_no_provider_branching_in_core_application(self):
        core_app_source = Path(__file__).resolve().parents[1] / "core" / "application.py"
        text = core_app_source.read_text(encoding="utf-8")
        self.assertNotIn("groq_qwen", text.lower())
        self.assertNotIn("GroqQwen", text)


if __name__ == "__main__":
    unittest.main()
