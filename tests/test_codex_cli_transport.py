import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.codex_task import CodexTask
from core.codex_cli_transport import (
    CodexCliTransport,
    _build_prompt,
    _parse_jsonl,
    _tests_from_events,
)


def build_task(**overrides):
    data = {
        "task_id": "codex-cli-001",
        "issuer": "digital_ricard",
        "mode": "analysis",
        "objective": "Inspect the repository structure and report the next technical target.",
        "context": "This is a read-only smoke test for the real Codex transport.",
        "allowed_paths": ("docs/CODEX_CLI_TRANSPORT.md",),
        "protected_paths": ("data/characters.yaml", "docs/CANON_100.md"),
        "constraints": ("Do not change files.",),
        "acceptance_criteria": ("Return a concise analysis.",),
        "verification_commands": ("PYTHONPATH=. pytest -q",),
        "base_ref": "feature/semantic-model",
        "base_commit": "abc123",
        "human_approval_required": True,
    }
    data.update(overrides)
    return CodexTask(**data)


class CodexCliTransportTests(unittest.TestCase):
    def test_prompt_contains_scope_and_authority(self):
        prompt = _build_prompt(build_task())
        self.assertIn("Authority: execution_only", prompt)
        self.assertIn("ALLOWED PATHS:", prompt)
        self.assertIn("PROTECTED PATHS:", prompt)
        self.assertIn("Do not commit changes.", prompt)

    def test_parse_jsonl_collects_final_agent_message(self):
        stdout = "\n".join(
            [
                json.dumps({"type": "thread.started", "thread_id": "1"}),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": "First"},
                    }
                ),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": "Final"},
                    }
                ),
            ]
        )
        events, message, errors = _parse_jsonl(stdout)
        self.assertEqual(len(events), 3)
        self.assertEqual(message, "Final")
        self.assertEqual(errors, [])

    def test_parse_jsonl_flags_non_json_output(self):
        events, message, errors = _parse_jsonl("not-json")
        self.assertEqual(events, [])
        self.assertIsNone(message)
        self.assertEqual(errors, ["codex emitted a non-JSON line"])

    def test_tests_from_events_filters_to_declared_verification(self):
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "PYTHONPATH=. pytest -q",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "git status --short",
                },
            },
        ]
        self.assertEqual(
            _tests_from_events(events, build_task()),
            ("PYTHONPATH=. pytest -q",),
        )

    def test_missing_codex_executable_returns_failed_result(self):
        task = build_task()
        transport = CodexCliTransport(root=".")
        with patch(
            "core.codex_cli_transport._run_git",
            side_effect=[task.base_ref, task.base_commit, "", "", "", ""],
        ), patch(
            "core.codex_cli_transport.subprocess.run",
            side_effect=FileNotFoundError,
        ):
            result = transport.execute(task)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.blockers, ("codex_executable_not_found",))

    def test_nonzero_exit_preserves_stderr_as_blocker(self):
        task = build_task()
        fake_completed = type(
            "Completed",
            (),
            {
                "stdout": "",
                "stderr": "usage: codex exec ...\\nerror: invalid flag",
                "returncode": 2,
            },
        )()

        with patch(
            "core.codex_cli_transport._run_git",
            side_effect=[task.base_ref, task.base_commit, "", "", "", ""],
        ), patch(
            "core.codex_cli_transport.subprocess.run",
            return_value=fake_completed,
        ):
            result = CodexCliTransport(root=".").execute(task)

        self.assertEqual(result.status, "failed")
        self.assertIn("codex_exit_code:2", result.blockers)
        self.assertTrue(any(item.startswith("codex_stderr:") for item in result.blockers))

    def test_execute_builds_expected_cli_command_and_trace(self):
        task = build_task()
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp) / "codex.jsonl"
            transport = CodexCliTransport(root=tmp, trace_path=trace)

            git_results = {
                ("rev-parse", "--abbrev-ref", "HEAD"): "feature/semantic-model",
                ("rev-parse", "HEAD"): task.base_commit,
                ("status", "--porcelain", "--untracked-files=all"): "",
                ("diff", "--name-only", task.base_commit): "",
                ("ls-files", "--others", "--exclude-standard"): "",
                ("ls-files",): "",
            }

            def fake_git(_root, *args):
                return git_results.get(tuple(args), "")

            fake_stdout = json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "agent_message",
                        "text": "Repository inspected.",
                    },
                }
            )
            fake_completed = type(
                "Completed",
                (),
                {"stdout": fake_stdout, "stderr": "", "returncode": 0},
            )()

            def fake_run(*args, **kwargs):
                return fake_completed

            with patch("core.codex_cli_transport._run_git", side_effect=fake_git),                 patch("core.codex_cli_transport.subprocess.run", side_effect=fake_run) as run:
                result = transport.execute(task)

            self.assertEqual(result.status, "completed")
            self.assertEqual(result.summary, "Repository inspected.")
            trace_payload = json.loads(trace.read_text(encoding="utf-8"))
            self.assertEqual(trace_payload["stdout"], fake_stdout)
            self.assertEqual(trace_payload["stderr"], "")
            self.assertEqual(
                run.call_args.args[0],
                [
                    "codex",
                    "exec",
                    "--json",
                    "--ephemeral",
                    "--sandbox",
                    "read-only",
                    "-a",
                    "never",
                    _build_prompt(task),
                ],
            )


if __name__ == "__main__":
    unittest.main()
