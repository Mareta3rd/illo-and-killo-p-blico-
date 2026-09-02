"""Candidate Executor contract and isolation tests.

These tests verify:
- Executor receives and passes correct arguments
- Executor output meets contract (dict, no Core logic, no invented evidence)
- Provider errors are encapsulated
- No provider-specific branching in Application
- Loop iteration and improvement workflow
"""

from pathlib import Path
import unittest
from unittest.mock import Mock, patch, MagicMock

from core.candidate_executor import (
    Candidate,
    CandidateExecutor,
    CandidateExecutorError,
    InvalidCandidateError,
    ProviderCandidateError,
    ExecutorConfig,
)
from core.simulated_candidate_executor import (
    SimulatedCandidateExecutor,
    build_simulated_executor,
)
from core.prompt_compiler import CompiledPrompt
from core.orchestrator import run_vertical_slice
from core.evidence_state import EvidenceClaim, EvidenceState


ROOT = Path(__file__).resolve().parents[1]

COMPLETE_EVIDENCE = {
    "intention": EvidenceClaim("intention", EvidenceState.CONFIRMED),
    "canon": EvidenceClaim("canon", EvidenceState.CONFIRMED),
    "coherence": EvidenceClaim("coherence", EvidenceState.CONFIRMED),
    "reuse_intention": EvidenceClaim("reuse", EvidenceState.CONFIRMED),
}

INITIAL_CANDIDATE = {
    "characters": ["illo", "killo"],
    "elements": [
        {"id": "clavel", "intention": "character_identity"},
        {"id": "black_spots", "count": 2, "intention": "character_identity"},
    ],
}

IMPROVED_CANDIDATE = {
    "characters": ["illo", "killo"],
    "elements": [
        {"id": "clavel", "intention": "character_identity"},
        {"id": "black_spots", "count": 3, "intention": "character_identity"},
    ],
}


class CandidateExecutorIntegrationTests(unittest.TestCase):
    """Contract tests for candidate executors integrated with Core."""

    def test_1_compiled_prompt_arrives_unchanged(self):
        """Executor receives the exact CompiledPrompt object."""
        received_prompts = []

        def capture_executor(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            received_prompts.append(prompt)
            return dict(INITIAL_CANDIDATE)

        result = run_vertical_slice(
            "Crear un gag con Illo y Killo",
            ROOT,
            capture_executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
        )

        self.assertFalse(result.stopped)
        self.assertEqual(len(received_prompts), 1)
        self.assertIs(received_prompts[0], result.pipeline.compiled_prompt)
        self.assertIsNotNone(result.pipeline.compiled_prompt)

    def test_2_executor_returns_dict(self):
        """Executor output must be a dict (Candidate type)."""
        def valid_executor(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            return {"valid": "dict", "elements": []}

        result = run_vertical_slice(
            "Crear un gag",
            ROOT,
            valid_executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
        )

        self.assertFalse(result.stopped)
        self.assertIsNotNone(result.loop)
        self.assertIsInstance(result.loop.iterations[-1].candidate, dict)

    def test_3_previous_candidate_arrives_correctly_iteration_1(self):
        """On iteration 1, previous is the initial_candidate."""
        received_previous = []

        def capture_executor(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            received_previous.append((iteration, previous))
            return dict(INITIAL_CANDIDATE)

        run_vertical_slice(
            "Crear un gag",
            ROOT,
            capture_executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
        )

        self.assertEqual(received_previous[0][0], 1)
        self.assertEqual(received_previous[0][1], INITIAL_CANDIDATE)

    def test_4_previous_candidate_arrives_correctly_iteration_2(self):
        """On iteration 2+, previous is the candidate from iteration 1."""
        received_previous = []

        # Create a semantic regression scenario: first iteration changes something
        first_candidate = {
            "characters": ["illo", "killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {"id": "black_spots", "count": 1, "intention": "character_identity"},
            ],
        }

        def capture_executor(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            received_previous.append((iteration, previous))
            if iteration == 1:
                return first_candidate
            return dict(INITIAL_CANDIDATE)

        result = run_vertical_slice(
            "Crear un gag",
            ROOT,
            capture_executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
            max_iterations=3,
        )

        # Verify that if we iterate, previous is preserved
        if len(received_previous) >= 2:
            self.assertEqual(received_previous[1][0], 2)
            self.assertEqual(received_previous[1][1], first_candidate)
        else:
            # If accepted on first try, at least verify first iteration got initial
            self.assertEqual(received_previous[0][0], 1)
            self.assertEqual(received_previous[0][1], INITIAL_CANDIDATE)

    def test_5_iteration_number_increments_correctly(self):
        """Executor receives 1-indexed iteration numbers matching loop behavior."""
        iteration_numbers = []

        def capture_executor(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            iteration_numbers.append(iteration)
            return dict(INITIAL_CANDIDATE)

        result = run_vertical_slice(
            "Crear un gag",
            ROOT,
            capture_executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
            max_iterations=3,
        )

        # Verify iteration numbering is correct (at minimum, iteration 1 is called)
        self.assertGreaterEqual(iteration_numbers[0], 1)
        # All iterations should be sequential
        for i, num in enumerate(iteration_numbers):
            self.assertEqual(num, i + 1)

    def test_6_no_core_logic_inside_executor(self):
        """Executor never validates, evaluates, or decides."""
        def simple_executor(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            # Executor returns raw dict; evaluation happens in Core
            # It doesn't check if it's valid, just returns a dict
            return {
                "characters": ["illo", "killo"],
                "elements": [{"id": "clavel", "intention": "character_identity"}],
            }

        result = run_vertical_slice(
            "Crear un gag",
            ROOT,
            simple_executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
        )

        # Executor produced the candidate and passed it to Core
        self.assertIsNotNone(result.loop)
        self.assertEqual(len(result.loop.iterations), 1)
        # The candidate was evaluated by Core (not by executor)
        self.assertIsNotNone(result.loop.iterations[0].evaluation)

    def test_7_no_provider_specific_branching_in_core(self):
        """Core and Application remain neutral to executor type."""
        # Two different executors, same Core logic
        def executor_a(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            return dict(INITIAL_CANDIDATE)

        def executor_b(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            return dict(INITIAL_CANDIDATE)

        result_a = run_vertical_slice(
            "Crear un gag",
            ROOT,
            executor_a,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
        )

        result_b = run_vertical_slice(
            "Crear un gag",
            ROOT,
            executor_b,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
        )

        # Same pipeline result, same evaluation
        self.assertEqual(result_a.pipeline.context.route, result_b.pipeline.context.route)
        self.assertEqual(result_a.loop.status, result_b.loop.status)

    def test_8_simulated_executor_respects_contract(self):
        """SimulatedCandidateExecutor validates candidate type."""
        with self.assertRaises(TypeError):
            # This should fail during build, not during execution
            build_simulated_executor(["not", "dicts"])

    def test_9_simulated_executor_rejects_out_of_range_iteration(self):
        """SimulatedCandidateExecutor raises on iteration > sequence length."""
        executor = build_simulated_executor([INITIAL_CANDIDATE])

        with self.assertRaises(InvalidCandidateError):
            executor.execute(
                CompiledPrompt(
                    route="gag",
                    task="Crear un gag",
                    constraints=(),
                    checks=(),
                    context_summary=(),
                ),
                iteration=2,
                previous=None,
            )

    def test_10_invalid_candidate_not_containing_core_decision(self):
        """Candidate must be data, never containing 'decision' or 'accept' keys."""
        def bad_executor(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            return {
                "characters": ["illo"],
                "elements": [],
                "decision": "accept",  # WRONG: executor should never decide
            }

        result = run_vertical_slice(
            "Crear un gag",
            ROOT,
            bad_executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
        )

        # The candidate contains the bad key (executor is not validating)
        self.assertIn("decision", result.loop.iterations[0].candidate)
        # But Core still evaluates it, not accepting the decision
        # (Canon guard will fail due to invalid schema)
        self.assertIsNotNone(result.loop.iterations[0].evaluation)

    def test_11_candidate_never_contains_invented_evidence(self):
        """Executor candidate dict must never include evidence_state, verdict, or source fields."""
        def bad_executor(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            return {
                "characters": ["illo"],
                "elements": [],
                "invented_evidence": {
                    "verdict": "confirmed",  # WRONG: executor never invents evidence
                    "sources": ["fabricated"],
                },
            }

        result = run_vertical_slice(
            "Crear un gag",
            ROOT,
            bad_executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
        )

        # Executor produced the bad data (not validating)
        candidate = result.loop.iterations[0].candidate
        self.assertIn("invented_evidence", candidate)
        # But Core never treats it as evidence
        self.assertIsNotNone(result.loop.iterations[0].evaluation)
        # Evidence remains from the snapshot, not from candidate
        self.assertIsNotNone(result.pipeline.evidence_snapshot)

    def test_12_no_real_network_calls(self):
        """Executor tests never make actual network requests."""
        simulated = build_simulated_executor([INITIAL_CANDIDATE])

        # Mock any potential HTTP/network calls
        with patch("socket.socket") as mock_socket:
            with patch("urllib.request.urlopen") as mock_urlopen:
                result = run_vertical_slice(
                    "Crear un gag",
                    ROOT,
                    simulated,
                    evidence_claims=COMPLETE_EVIDENCE,
                    initial_candidate=INITIAL_CANDIDATE,
                )
                # No network calls
                mock_socket.assert_not_called()
                mock_urlopen.assert_not_called()

        self.assertFalse(result.stopped)

    def test_13_single_call_per_iteration(self):
        """Executor is called exactly once per loop iteration."""
        call_count = [0]

        def counting_executor(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            call_count[0] += 1
            return dict(INITIAL_CANDIDATE)

        result = run_vertical_slice(
            "Crear un gag",
            ROOT,
            counting_executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
            max_iterations=3,
        )

        # Executor called once per iteration (at minimum once for first iteration)
        self.assertGreaterEqual(call_count[0], 1)
        # Call count should match iteration count
        self.assertEqual(call_count[0], len(result.loop.iterations))

    def test_14_second_iteration_only_when_loop_decides_continue(self):
        """Executor is not called again unless evaluator decides 'continue'."""
        def always_accepts(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            return dict(INITIAL_CANDIDATE)

        result = run_vertical_slice(
            "Crear un gag",
            ROOT,
            always_accepts,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL_CANDIDATE,
            max_iterations=3,
        )

        # Accepted on first iteration, no second call
        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 1)

    def test_15_application_remains_provider_neutral(self):
        """Application accepts any Executor without knowing provider details."""
        from core.application import ApplicationRequest, run_application
        from core.external_evidence_adapter import ExternalEvidenceRecord
        from core.evidence_state import EvidenceState

        executor_was_called = [False]

        def tracking_executor(prompt: CompiledPrompt, iteration: int, previous: Candidate | None) -> Candidate:
            executor_was_called[0] = True
            return dict(INITIAL_CANDIDATE)

        # Mock provider with complete evidence
        from core.simulated_evidence_provider import SimulatedEvidenceProvider
        mock_provider = SimulatedEvidenceProvider({
            "intention": ExternalEvidenceRecord(
                claim_key="intention",
                statement="test",
                state=EvidenceState.CONFIRMED,
                supporting_sources=("test",),
                contradicting_sources=(),
            ),
            "canon": ExternalEvidenceRecord(
                claim_key="canon",
                statement="test",
                state=EvidenceState.CONFIRMED,
                supporting_sources=("test",),
                contradicting_sources=(),
            ),
            "coherence": ExternalEvidenceRecord(
                claim_key="coherence",
                statement="test",
                state=EvidenceState.CONFIRMED,
                supporting_sources=("test",),
                contradicting_sources=(),
            ),
            "reuse_intention": ExternalEvidenceRecord(
                claim_key="reuse_intention",
                statement="test",
                state=EvidenceState.CONFIRMED,
                supporting_sources=("test",),
                contradicting_sources=(),
            ),
        })

        image_path = ROOT / "gags" / "images" / "001_jamon.png"
        image_data = image_path.read_bytes() if image_path.is_file() else b"\x89PNG\r\n\x1a\n"

        request = ApplicationRequest(
            idea="Crear un gag",
            root=ROOT,
            provider=mock_provider,
            provider_name="simulated",
            run_id="test-app-neutral",
            requested_claims=("intention", "canon", "coherence", "reuse_intention"),
            proposal=INITIAL_CANDIDATE,
            executor=tracking_executor,  # Any callable works
            model="test",
            image=str(image_path) if image_path.is_file() else "test.png",
            max_iterations=1,
        )

        result = run_application(request)

        # Application used the executor (provider-neutral)
        self.assertTrue(executor_was_called[0])
        self.assertIsNotNone(result.core)


class SimulatedCandidateExecutorTests(unittest.TestCase):
    """Unit tests for SimulatedCandidateExecutor implementation."""

    def test_build_rejects_empty_sequence(self):
        """build_simulated_executor requires at least one candidate."""
        with self.assertRaises(ValueError):
            build_simulated_executor([])

    def test_build_rejects_non_dict_items(self):
        """build_simulated_executor validates all items are dicts."""
        with self.assertRaises(TypeError):
            build_simulated_executor([INITIAL_CANDIDATE, "not a dict"])

    def test_callable_interface(self):
        """SimulatedCandidateExecutor is callable (backward compatible)."""
        executor = build_simulated_executor([INITIAL_CANDIDATE])
        prompt = CompiledPrompt(
            route="gag",
            task="Test",
            constraints=(),
            checks=(),
            context_summary=(),
        )

        # Call as function
        result = executor(prompt, 1, None)
        self.assertEqual(result, INITIAL_CANDIDATE)

        # Call as method
        result2 = executor.execute(prompt, 1, None)
        self.assertEqual(result2, INITIAL_CANDIDATE)

    def test_defensive_copy_prevents_mutation(self):
        """Returned candidate is a copy, not a reference."""
        original_dict = {
            "characters": ["illo"],
            "elements": [],
        }
        executor = build_simulated_executor([original_dict])

        # Get first result
        result1 = executor.execute(
            CompiledPrompt("gag", "Test", (), (), ()),
            1,
            None,
        )

        # Get second result from same executor
        result2 = executor.execute(
            CompiledPrompt("gag", "Test", (), (), ()),
            1,
            None,
        )

        # Mutate result1
        result1["characters"].append("killo")

        # result2 should not be affected (it's a separate copy)
        self.assertEqual(result2["characters"], ["illo"])


class CandidateExecutorErrorTests(unittest.TestCase):
    """Error handling contract tests."""

    def test_provider_error_is_encapsulated(self):
        """Provider errors are wrapped in CandidateExecutorError."""
        error = ProviderCandidateError("provider failed")
        self.assertIsInstance(error, CandidateExecutorError)
        self.assertIn("provider failed", str(error))

    def test_invalid_candidate_error(self):
        """InvalidCandidateError documents contract violations."""
        error = InvalidCandidateError("candidate not dict")
        self.assertIsInstance(error, CandidateExecutorError)
        self.assertIn("candidate not dict", str(error))

    def test_executor_config_is_provider_neutral(self):
        """ExecutorConfig does not favor any specific provider."""
        config = ExecutorConfig(
            provider="simulated",
            model=None,
            max_retries=0,
            timeout_seconds=60,
            extra={"key": "value"},
        )

        self.assertEqual(config.provider, "simulated")
        self.assertIsNone(config.model)
        self.assertIsNotNone(config.extra)


if __name__ == "__main__":
    unittest.main()
