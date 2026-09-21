import unittest

from core.codex_execution_bridge import CodexExecutionBridge
from core.codex_task import CodexTask, CodexTaskResult


def build_task(**overrides):
    data = {
        "task_id": "codex-bridge-001",
        "issuer": "digital_ricard",
        "mode": "implementation",
        "objective": "Implement the bounded execution bridge.",
        "context": "The bridge must protect task authority and repository scope.",
        "allowed_paths": ("core/", "tests/"),
        "protected_paths": ("data/characters.yaml", "docs/CANON_100.md"),
        "constraints": ("Keep Core authority outside Codex.",),
        "acceptance_criteria": ("Bridge validates the returned task result.",),
        "verification_commands": ("PYTHONPATH=. pytest -q",),
        "base_ref": "feature/semantic-model",
        "base_commit": "abc123",
        "human_approval_required": True,
    }
    data.update(overrides)
    return CodexTask(**data)


class RecordingTransport:
    def __init__(self, result=None):
        self.calls = []
        self.result = result

    def execute(self, task):
        self.calls.append(task)
        return self.result(task) if callable(self.result) else self.result


class CodexExecutionBridgeTests(unittest.TestCase):
    def test_unapproved_task_is_blocked_without_calling_transport(self):
        transport = RecordingTransport()
        bridge = CodexExecutionBridge(transport)

        result = bridge.execute(build_task(), human_approved=False)

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.changed_files, ())
        self.assertEqual(result.blockers, ("human_approval_required",))
        self.assertEqual(transport.calls, [])

    def test_approved_task_reaches_transport_and_preserves_result(self):
        task = build_task()
        expected = CodexTaskResult(
            task_id=task.task_id,
            task_digest=task.digest(),
            status="completed",
            summary="Bridge executed the task.",
            changed_files=("core/example.py", "tests/test_example.py"),
            tests_run=("PYTHONPATH=. pytest -q",),
            diff_digest="abc",
        )
        transport = RecordingTransport(expected)

        result = CodexExecutionBridge(transport).execute(task, human_approved=True)

        self.assertEqual(result, expected)
        self.assertEqual(transport.calls, [task])

    def test_transport_result_outside_scope_is_rejected(self):
        task = build_task()
        invalid = CodexTaskResult(
            task_id=task.task_id,
            task_digest=task.digest(),
            status="completed",
            summary="Changed a protected file.",
            changed_files=("data/characters.yaml",),
            tests_run=(),
        )

        with self.assertRaises(ValueError):
            CodexExecutionBridge(RecordingTransport(invalid)).execute(
                task, human_approved=True
            )

    def test_transport_result_with_wrong_digest_is_rejected(self):
        task = build_task()
        invalid = CodexTaskResult(
            task_id=task.task_id,
            task_digest="wrong",
            status="completed",
            summary="Wrong digest.",
            changed_files=(),
            tests_run=(),
        )

        with self.assertRaises(ValueError):
            CodexExecutionBridge(RecordingTransport(invalid)).execute(
                task, human_approved=True
            )

    def test_transport_must_return_a_codex_task_result(self):
        task = build_task()

        with self.assertRaises(TypeError):
            CodexExecutionBridge(RecordingTransport({})).execute(
                task, human_approved=True
            )

    def test_human_approved_argument_must_be_boolean(self):
        task = build_task()

        with self.assertRaises(TypeError):
            CodexExecutionBridge(RecordingTransport()).execute(task, human_approved="yes")


if __name__ == "__main__":
    unittest.main()
