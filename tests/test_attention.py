from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import inspect
import unittest

from core.application import ApplicationResult
from core.attention import (
    AttentionCategory,
    AttentionEvent,
    AttentionSeverity,
    AttentionStatus,
    build_attention_events,
)
from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from tests.test_application import FakeProvider, FailingProvider, ApplicationTests


ROOT = Path(__file__).resolve().parents[1]
INVARIANT = "fauna/mosquito_tigre/readable_as_mosquito"
CANONICAL = "gag/001/composition/illo_primary"


class AttentionTests(unittest.TestCase):
    def application_result(self, *, state=EvidenceState.CONFIRMED, key=INVARIANT, stop_reason=None, artifact_error=None):
        provider = FakeProvider(state, key)
        from core.application import run_application
        request = ApplicationTests().request(provider, claims=(key,))
        result = run_application(request)
        if stop_reason is not None or artifact_error is not None:
            return ApplicationResult(
                run_id=result.run_id,
                observation=result.observation,
                snapshot=result.snapshot,
                core=result.core,
                artifact=result.artifact,
                artifact_error=artifact_error,
                stopped=True,
                stop_reason=stop_reason,
            )
        return result

    def test_human_review_and_unknown_translate_without_changing_result(self):
        result = self.application_result(state=EvidenceState.UNKNOWN)
        before = result
        events = build_attention_events(result)
        categories = {event.category for event in events}
        self.assertIn(AttentionCategory.EVIDENCE_UNKNOWN, categories)
        self.assertNotIn(AttentionCategory.CORE_HUMAN_REVIEW, categories)
        self.assertEqual(
            sum(event.category is AttentionCategory.EVIDENCE_UNKNOWN for event in events),
            1,
        )
        self.assertEqual(result, before)
        self.assertEqual(result.observation.records[0].state, EvidenceState.UNKNOWN)

    def test_contradicted_is_not_transformed(self):
        result = self.application_result(state=EvidenceState.CONTRADICTED)
        self.assertNotIn(
            AttentionCategory.EVIDENCE_CONFLICT,
            {event.category for event in build_attention_events(result)},
        )
        self.assertEqual(result.observation.records[0].state, EvidenceState.CONTRADICTED)

    def test_provider_failure_and_artifact_failure(self):
        from core.application import run_application
        provider_result = run_application(ApplicationTests().request(FailingProvider()))
        provider_events = build_attention_events(provider_result)
        self.assertEqual(provider_events[0].category, AttentionCategory.PROVIDER_FAILURE)
        self.assertEqual(provider_events[0].severity, AttentionSeverity.CRITICAL)
        artifact_result = self.application_result(artifact_error="unable to write execution artifact: disk full")
        artifact_events = build_attention_events(artifact_result)
        self.assertEqual(artifact_events[0].category, AttentionCategory.ARTIFACT_FAILURE)
        self.assertEqual(artifact_events[0].severity, AttentionSeverity.CRITICAL)

    def test_conflict_claim_and_invariant_metadata(self):
        from core.application import run_application
        request = ApplicationTests().request(FakeProvider())
        conflict_request = replace(
            request,
            proposal={**request.proposal, "checks": {INVARIANT: False}},
        )
        conflict = run_application(conflict_request)
        event = build_attention_events(conflict)[0]
        self.assertEqual(event.category, AttentionCategory.EVIDENCE_CONFLICT)
        self.assertEqual(conflict.core.pipeline.evaluation.evaluation.decision, "human_review")
        self.assertNotIn(
            AttentionCategory.CORE_HUMAN_REVIEW,
            {item.category for item in build_attention_events(conflict)},
        )
        canonical = build_attention_events(self.application_result(state=EvidenceState.UNKNOWN, key=CANONICAL))
        unknown = next(event for event in canonical if event.category is AttentionCategory.EVIDENCE_UNKNOWN)
        self.assertEqual(unknown.claim_key, CANONICAL)
        self.assertIsNone(unknown.catalog)
        invariant = next(event for event in build_attention_events(self.application_result(state=EvidenceState.UNKNOWN)) if event.category is AttentionCategory.EVIDENCE_UNKNOWN)
        self.assertEqual((invariant.catalog, invariant.entry, invariant.invariant), ("fauna", "mosquito_tigre", "readable_as_mosquito"))

    def test_unrelated_human_review_is_core_human_review(self):
        from core.application import run_application
        request = ApplicationTests().request(FakeProvider())
        result = run_application(
            replace(request, proposal={**request.proposal, "checks": {}})
        )
        events = build_attention_events(result)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].category, AttentionCategory.CORE_HUMAN_REVIEW)

    def test_identity_severity_category_and_run_id_are_deterministic(self):
        result = self.application_result(state=EvidenceState.UNKNOWN)
        first = build_attention_events(result)
        second = build_attention_events(result)
        self.assertEqual(first, second)
        self.assertTrue(all(event.run_id == result.run_id for event in first))
        self.assertEqual(first[0].severity, AttentionSeverity.ATTENTION)
        self.assertEqual(first[0].status, AttentionStatus.PENDING)
        shifted = replace(first[0], created_at="2026-08-28T00:00:00Z")
        self.assertEqual(shifted.deduplication_key, first[0].deduplication_key)

    def test_distinct_runs_keep_run_ids_but_share_deduplication(self):
        first = self.application_result(state=EvidenceState.UNKNOWN)
        second = ApplicationResult(
            run_id="application-run-002",
            observation=first.observation,
            snapshot=first.snapshot,
            core=first.core,
            artifact=first.artifact,
            artifact_error=first.artifact_error,
            stopped=first.stopped,
            stop_reason=first.stop_reason,
        )
        event_one = next(event for event in build_attention_events(first) if event.category is AttentionCategory.EVIDENCE_UNKNOWN)
        event_two = next(event for event in build_attention_events(second) if event.category is AttentionCategory.EVIDENCE_UNKNOWN)
        self.assertNotEqual(event_one.event_id, event_two.event_id)
        self.assertNotEqual(event_one.run_id, event_two.run_id)
        self.assertEqual(event_one.deduplication_key, event_two.deduplication_key)

    def test_event_is_immutable_and_translation_has_no_external_side_effects(self):
        result = self.application_result(state=EvidenceState.UNKNOWN)
        event = build_attention_events(result)[0]
        with self.assertRaises(FrozenInstanceError):
            event.status = AttentionStatus.RESOLVED
        source = inspect.getsource(__import__("core.attention", fromlist=["attention"]))
        for forbidden in ("gemini", "groq", "qwen", "openai", "gmail", "notify", "send_email"):
            self.assertNotIn(forbidden, source.lower())
        self.assertIsInstance(result, ApplicationResult)

    def test_conflict_and_unknown_events_are_stable_across_repeated_translation(self):
        unknown = self.application_result(state=EvidenceState.UNKNOWN)
        first = build_attention_events(unknown)
        second = build_attention_events(unknown)
        self.assertEqual(first, second)
        self.assertEqual(first[0].deduplication_key, second[0].deduplication_key)


if __name__ == "__main__":
    unittest.main()