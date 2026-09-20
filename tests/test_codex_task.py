import json
import unittest

from core.codex_task import (
    CodexTask,
    CodexTaskResult,
    codex_task_contract,
    codex_task_result_contract,
    deserialize_codex_task,
    deserialize_codex_task_result,
    serialize_codex_task,
    serialize_codex_task_result,
    validate_codex_task_result,
)


def build_task(**overrides):
    data = {
        "task_id": "codex-001",
        "issuer": "core",
        "mode": "implementation",
        "objective": "Add a controlled adapter without changing canon.",
        "context": "A provider boundary needs a concrete implementation.",
        "allowed_paths": ("core/adapter.py", "tests/"),
        "protected_paths": ("data/characters.yaml", "docs/CANON_100.md"),
        "constraints": (
            "Preserve Core decision authority.",
            "Do not introduce deterministic creative generation.",
        ),
        "acceptance_criteria": (
            "Focused tests pass.",
            "Complete suite remains green.",
        ),
        "verification_commands": (
            "PYTHONPATH=. pytest -q tests/test_adapter.py",
            "PYTHONPATH=. pytest -q",
        ),
        "base_ref": "feature/semantic-model",
        "base_commit": "abc123",
        "human_approval_required": True,
    }
    data.update(overrides)
    return CodexTask(**data)


class CodexTaskTests(unittest.TestCase):
    def test_task_round_trip_is_deterministic(self):
        task = build_task()
        payload = serialize_codex_task(task)
        self.assertEqual(payload, serialize_codex_task(deserialize_codex_task(payload)))
        self.assertEqual(task.digest(), task.digest())

    def test_task_digest_changes_when_scope_changes(self):
        task = build_task()
        changed = build_task(allowed_paths=("core/",))
        self.assertNotEqual(task.digest(), changed.digest())

    def test_protected_and_allowed_paths_must_not_overlap(self):
        with self.assertRaises(ValueError):
            build_task(allowed_paths=("core/",), protected_paths=("core/private.py",))

    def test_repository_path_cannot_escape(self):
        with self.assertRaises(ValueError):
            build_task(allowed_paths=("../secrets",))

    def test_task_requires_acceptance_and_verification(self):
        with self.assertRaises(ValueError):
            build_task(acceptance_criteria=())
        with self.assertRaises(ValueError):
            build_task(verification_commands=())

    def test_codex_never_receives_core_authority(self):
        with self.assertRaises(ValueError):
            build_task(authority="core_decision")
        with self.assertRaises(ValueError):
            build_task(human_approval_required=False)

    def test_digital_ricard_tasks_require_human_approval(self):
        with self.assertRaises(ValueError):
            build_task(issuer="digital_ricard", human_approval_required=False)

    def test_core_orchestrator_tasks_require_human_approval(self):
        with self.assertRaises(ValueError):
            build_task(issuer="core", human_approval_required=False)
        with self.assertRaises(ValueError):
            build_task(issuer="orchestrator", human_approval_required=False)
        with self.assertRaises(ValueError):
            build_task(issuer="reviewer", human_approval_required=False)

    def test_task_schema_is_closed(self):
        schema = codex_task_contract()
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["authority"]["const"], "execution_only")
        self.assertEqual(schema["properties"]["human_approval_required"]["const"], True)

    def test_result_round_trip(self):
        task = build_task()
        result = CodexTaskResult(
            task_id=task.task_id,
            task_digest=task.digest(),
            status="completed",
            summary="Implemented and verified the adapter.",
            changed_files=("core/adapter.py", "tests/test_adapter.py"),
            tests_run=("PYTHONPATH=. pytest -q",),
            diff_digest="deadbeef",
        )
        payload = serialize_codex_task_result(result)
        restored = deserialize_codex_task_result(payload)
        self.assertEqual(result.to_dict(), restored.to_dict())

    def test_result_accepts_blocked_without_changes(self):
        result = CodexTaskResult(
            task_id="codex-blocked",
            task_digest="digest",
            status="blocked",
            summary="Required connector access is unavailable.",
            changed_files=(),
            tests_run=(),
            blockers=("connector unavailable",),
        )
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.changed_files, ())

    def test_result_must_match_task_identity_and_digest(self):
        task = build_task()
        result = CodexTaskResult(
            task_id=task.task_id,
            task_digest=task.digest(),
            status="completed",
            summary="done",
            changed_files=("core/adapter.py",),
            tests_run=("PYTHONPATH=. pytest -q",),
        )
        validate_codex_task_result(task, result)

        mismatched = CodexTaskResult(
            task_id="other",
            task_digest=task.digest(),
            status="completed",
            summary="done",
            changed_files=("core/adapter.py",),
            tests_run=("PYTHONPATH=. pytest -q",),
        )
        with self.assertRaises(ValueError):
            validate_codex_task_result(task, mismatched)

    def test_result_scope_protects_changes(self):
        task = build_task()
        protected = CodexTaskResult(
            task_id=task.task_id,
            task_digest=task.digest(),
            status="completed",
            summary="changed protected file",
            changed_files=("data/characters.yaml",),
            tests_run=("PYTHONPATH=. pytest -q",),
        )
        with self.assertRaises(ValueError):
            validate_codex_task_result(task, protected)

        outside = CodexTaskResult(
            task_id=task.task_id,
            task_digest=task.digest(),
            status="completed",
            summary="changed outside scope",
            changed_files=("scripts/hack.py",),
            tests_run=("PYTHONPATH=. pytest -q",),
        )
        with self.assertRaises(ValueError):
            validate_codex_task_result(task, outside)

    def test_analysis_result_cannot_change_files(self):
        task = build_task(mode="analysis", allowed_paths=("core/",))
        result = CodexTaskResult(
            task_id=task.task_id,
            task_digest=task.digest(),
            status="completed",
            summary="analysis complete",
            changed_files=("core/adapter.py",),
            tests_run=("PYTHONPATH=. pytest -q",),
        )
        with self.assertRaises(ValueError):
            validate_codex_task_result(task, result)

    def test_result_rejects_unknown_status(self):
        with self.assertRaises(ValueError):
            CodexTaskResult(
                task_id="codex-bad",
                task_digest="digest",
                status="unknown",
                summary="bad",
                changed_files=(),
                tests_run=(),
            )

    def test_result_schema_is_closed(self):
        schema = codex_task_result_contract()
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["required"], sorted(schema["properties"]))

    def test_deserializer_rejects_extra_fields(self):
        task = build_task()
        data = task.to_dict()
        data["surprise"] = "not allowed"
        with self.assertRaises(ValueError):
            deserialize_codex_task(json.dumps(data))


if __name__ == "__main__":
    unittest.main()
