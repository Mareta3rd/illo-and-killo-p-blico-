import inspect
import json
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from core.attention import (
    AttentionCategory,
    AttentionEvent,
    AttentionSeverity,
    AttentionStatus,
)
from core.attention_store import JsonAttentionStore


def event(event_id, run_id="run-001", *, status=AttentionStatus.PENDING, claim_key="gag/001/composition/illo_primary", category=AttentionCategory.CORE_HUMAN_REVIEW):
    return AttentionEvent(
        event_id=event_id,
        run_id=run_id,
        severity=AttentionSeverity.ATTENTION,
        category=category,
        status=status,
        reason="requires human review",
        claim_key=claim_key,
        created_at="2026-08-28T01:47:00Z",
        deduplication_key="dedupe-001",
    )


class AttentionStoreTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.store = JsonAttentionStore(Path(self.directory.name) / "attention.json")

    def tearDown(self):
        self.directory.cleanup()

    def test_save_get_and_persistence(self):
        original = event("event-001")
        self.store.save(original)
        reloaded = JsonAttentionStore(self.store.path)
        self.assertEqual(reloaded.get(original.event_id), original)
        payload = self.store.path.read_text(encoding="utf-8")
        self.assertEqual(payload, reloaded.path.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(payload)["schema_version"], 1)

    def test_list_pending_and_filters(self):
        first = event("event-001", run_id="run-001")
        second = event("event-002", run_id="run-002", claim_key="fauna/mosquito_tigre/readable_as_mosquito", category=AttentionCategory.EVIDENCE_UNKNOWN)
        self.store.save(first)
        self.store.save(second)
        self.store.acknowledge(first.event_id)
        self.assertEqual(self.store.list_pending(), (self.store.get(first.event_id), self.store.get(second.event_id)))
        self.assertEqual(self.store.list_pending(run_id="run-002"), (second,))
        self.assertEqual(self.store.list_pending(category=AttentionCategory.EVIDENCE_UNKNOWN), (second,))
        self.assertEqual(self.store.list_pending(claim_key=second.claim_key, event_id=second.event_id), (second,))

    def test_acknowledge_resolve_dismiss_return_new_events(self):
        original = event("event-001")
        self.store.save(original)
        acknowledged = self.store.acknowledge(original.event_id)
        self.assertEqual(acknowledged.status, AttentionStatus.ACKNOWLEDGED)
        self.assertEqual(original.status, AttentionStatus.PENDING)
        resolved = self.store.resolve(original.event_id, "reviewed")
        self.assertEqual(resolved.status, AttentionStatus.RESOLVED)
        self.store.save(event("event-002"))
        dismissed = self.store.dismiss("event-002", "not applicable")
        self.assertEqual(dismissed.status, AttentionStatus.DISMISSED)
        self.assertEqual(self.store.list_pending(), ())

    def test_invalid_transitions_and_missing_events(self):
        self.assertIsNone(self.store.get("missing"))
        with self.assertRaises(KeyError):
            self.store.acknowledge("missing")
        self.store.save(event("event-001"))
        with self.assertRaises(ValueError):
            self.store.resolve("event-001", "")
        self.store.resolve("event-001", "done")
        with self.assertRaises(ValueError):
            self.store.acknowledge("event-001")

    def test_duplicates_are_preserved_and_run_ids_remain_distinct(self):
        first = event("event-001", run_id="run-001")
        second = event("event-002", run_id="run-002")
        self.store.save(first)
        self.store.save(second)
        self.assertEqual(self.store.list_pending(), (first, second))
        self.assertEqual({item.deduplication_key for item in self.store.list_pending()}, {"dedupe-001"})
        self.assertEqual({item.run_id for item in self.store.list_pending()}, {"run-001", "run-002"})

    def test_corrupt_and_unknown_schema_are_rejected(self):
        self.store.path.write_text("not json", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.list_pending()
        self.store.path.write_text(json.dumps({"schema_version": 2, "events": []}), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.list_pending()
        self.store.path.write_text(json.dumps({"schema_version": 1, "events": [{"event_id": "bad"}]}), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.list_pending()

    def test_event_immutable_and_no_external_channels_or_execution(self):
        original = event("event-001")
        self.store.save(original)
        with self.assertRaises(FrozenInstanceError):
            original.status = AttentionStatus.RESOLVED
        source = inspect.getsource(__import__("core.attention_store", fromlist=["attention_store"]))
        for forbidden in ("gemini", "groq", "qwen", "openai", "gmail", "email", "notify", "run_application", "run_pipeline"):
            self.assertNotIn(forbidden, source.lower())


if __name__ == "__main__":
    unittest.main()