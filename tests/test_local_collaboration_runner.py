import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_local_collaboration import (
    DEFAULT_IDEA,
    build_argument_parser,
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
        self.assertEqual(envelope.context["requested_idea"], DEFAULT_IDEA)
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
        self.assertTrue(
            any(
                "mantener centrales los personajes, objetos y resultados" in item
                for item in envelope.constraints
            )
        )
        self.assertTrue(
            any(
                "Sustituir el elemento concreto solicitado" in item
                for item in envelope.known_failures
            )
        )

    def test_local_runner_defaults_to_qwen3_4b(self):
        required = ["--run-id", "test", "--artifact-path", "record.json"]
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(build_argument_parser().parse_args(required).model, "qwen3-4b")
        with patch.dict("os.environ", {"LOCAL_QWEN_MODEL": "runtime-alias"}):
            parser = build_argument_parser()
            self.assertEqual(parser.parse_args(required).model, "runtime-alias")
            self.assertEqual(parser.parse_args([*required, "--model", "other-alias"]).model, "other-alias")

    def test_real_runner_records_exact_collaboration_execution(self):
        client = FakeClient()
        idea = "Crear un gag de Arsa y Pisha con un jamón y una escalera plegable."
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "collaboration.json"
            record = run_experiment(
                run_id="local-collab-test-002",
                idea=idea,
                model="qwen3-4b",
                base_url="http://127.0.0.1:8080/v1",
                api_key="local",
                artifact_path=artifact_path,
                client=client,
            )
            self.assertEqual(record.provider_id, "local-qwen-collaboration")
            self.assertEqual(record.model_id, "qwen3-4b")
            self.assertEqual(record.envelope.envelope_id, "local-collab-test-002")
            self.assertEqual(record.update.status, "ready_for_review")
            self.assertTrue(record.update.attention_required)
            self.assertEqual(record.update.output["questions"], [])
            persisted = artifact_path.read_text(encoding="utf-8")
            self.assertEqual(json.loads(persisted), json.loads(record.to_json()))
            self.assertEqual(len(client.chat.completions.calls), 1)
            request = client.chat.completions.calls[0]
            self.assertEqual(request["model"], "qwen3-4b")
            self.assertEqual(request["temperature"], 0.0)
            self.assertEqual(request["response_format"]["type"], "json_schema")
            self.assertIn("WorkEnvelope", request["messages"][0]["content"])
            self.assertIn(idea, request["messages"][0]["content"])
            self.assertEqual(json.loads(persisted)["envelope"]["context"]["requested_idea"], idea)
            self.assertIn("historical_material=reference_only; excluded_from_active_canon", request["messages"][0]["content"])


if __name__ == "__main__":
    unittest.main()
