import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_local_collaboration import (
    DEFAULT_IDEA,
    build_work_envelope,
    run_experiment,
)


class FakeCompletions:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return type(
            "Response",
            (),
            {
                "choices": [
                    type(
                        "Choice",
                        (),
                        {
                            "message": type(
                                "Message",
                                (),
                                {
                                    "content": json.dumps(
                                        {
                                            "status": "ready_for_review",
                                            "summary": "He desarrollado una dirección concreta y diferenciada.",
                                            "progress": [
                                                "He usado el contexto semántico del gag y los invariantes actuales.",
                                            ],
                                            "needs_input": None,
                                            "blockers": [],
                                            "output": {
                                                "answer": "La propuesta principal convierte el jamón en el detonante de una escalada física concreta.",
                                                "rationale": "La novedad está en la causalidad de la escalada y no en sustituir un objeto del gag anterior.",
                                                "proposals": [
                                                    "Propuesta principal: el jamón se vuelve el elemento que desencadena la cadena cómica.",
                                                    "Alternativa 1: desplazar el conflicto al comportamiento de ambos personajes.",
                                                ],
                                                "questions": [],
                                            },
                                            "attention_required": True,
                                        }
                                    )
                                },
                            )
                        },
                    )
                ]
            },
        )()


class FakeChat:
    def __init__(self):
        self.completions = FakeCompletions()


class FakeClient:
    def __init__(self):
        self.chat = FakeChat()


class LocalCollaborationRunnerTests(unittest.TestCase):
    def test_work_envelope_contains_current_semantic_context_and_boundaries(self):
        envelope = build_work_envelope(run_id="local-collab-test-001", idea=DEFAULT_IDEA)
        self.assertEqual(envelope.project, "SinergYa / Arsa & Pisha")
        self.assertEqual(envelope.context["route"], "gag")
        entries = envelope.context["semantic_context"]
        self.assertTrue(entries)
        self.assertTrue(any("character=arsa" in item for item in entries))
        self.assertTrue(any("character=pisha" in item for item in entries))
        self.assertIn(
            "historical_material=reference_only; excluded_from_active_canon",
            entries,
        )
        self.assertEqual(envelope.autonomy, "advisory")
        self.assertEqual(envelope.available_tools, ())

    def test_real_runner_records_exact_collaboration_execution(self):
        client = FakeClient()
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "collaboration.json"
            record = run_experiment(
                run_id="local-collab-test-002",
                idea=DEFAULT_IDEA,
                model="qwen3.8-27b",
                base_url="http://127.0.0.1:8080/v1",
                api_key="local",
                artifact_path=artifact_path,
                client=client,
            )
            self.assertEqual(record.provider_id, "local-qwen-collaboration")
            self.assertEqual(record.model_id, "qwen3.8-27b")
            self.assertEqual(record.envelope.envelope_id, "local-collab-test-002")
            self.assertEqual(record.update.status, "ready_for_review")
            self.assertTrue(record.update.attention_required)
            self.assertEqual(record.update.output["questions"], [])
            persisted = artifact_path.read_text(encoding="utf-8")
            self.assertEqual(json.loads(persisted), json.loads(record.to_json()))
            self.assertEqual(len(client.chat.completions.calls), 1)
            request = client.chat.completions.calls[0]
            self.assertEqual(request["model"], "qwen3.8-27b")
            self.assertEqual(request["temperature"], 0.0)
            self.assertEqual(request["response_format"]["type"], "json_schema")
            self.assertIn("WorkEnvelope", request["messages"][0]["content"])
            self.assertIn("historical_material=reference_only; excluded_from_active_canon", request["messages"][0]["content"])


if __name__ == "__main__":
    unittest.main()
