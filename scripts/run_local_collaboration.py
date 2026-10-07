"""Run one real local Qwen collaborative work pass.

This entrypoint is an experiment composition root. It builds a bounded
WorkEnvelope from the repository's authoritative semantic context, invokes an
OpenAI-compatible local runtime, and writes the exact CollaborationExecutionRecord.
It does not call Core decision logic, mutate canon, or execute tools.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from openai import OpenAI

from core.collaboration_execution import CollaborationExecutionRecord, execute_collaboration
from core.local_collaboration_provider import LocalStructuredCollaborationProvider
from core.loader import load_repository
from core.semantic_context import build_semantic_context
from core.work_envelope import WorkEnvelope

DEFAULT_MODEL = os.environ.get("LOCAL_QWEN_MODEL", "qwen3.8-27b")
DEFAULT_BASE_URL = os.environ.get("LOCAL_QWEN_BASE_URL", "http://127.0.0.1:8080/v1")

DEFAULT_IDEA = (
    "Crear un gag nuevo de Arsa y Pisha alrededor de un jamón: debe tener un gag "
    "principal inmediato, una escalada absurda nacida de una lógica reconocible y "
    "mantener la complicidad y ternura entre ambos."
)

DEFAULT_OUTPUT = (
    "Una colaboración concreta y utilizable: diagnóstico breve del problema creativo, "
    "una propuesta principal desarrollada, dos alternativas diferenciadas y preguntas "
    "solo cuando sean realmente bloqueantes."
)


def build_work_envelope(*, run_id: str, idea: str) -> WorkEnvelope:
    knowledge = load_repository(REPO_ROOT)
    semantic_context = build_semantic_context(
        idea=idea,
        route="gag",
        data=knowledge.data,
        markdown=knowledge.markdown,
    )
    return WorkEnvelope(
        envelope_id=run_id,
        objective=(
            "Desarrollar una dirección creativa nueva para un gag de Arsa y Pisha "
            "que use el contexto semántico actual como límite e información, no como "
            "plantilla, y que resulte concreta y evaluable por una persona."
        ),
        project="SinergYa / Arsa & Pisha",
        state="available",
        context={
            "route": "gag",
            "semantic_context": list(semantic_context.entries),
            "canon_boundary": "Arsa & Pisha are current canon; Illo & Killo and earlier Xoxo material are historical only.",
            "evidence_boundary": "Provider output is experimental collaboration evidence, not canon and not a Core decision.",
        },
        constraints=(
            "Preservar la identidad y los invariantes actuales de Arsa y Pisha.",
            "Un solo gag principal por ilustración; la lectura inicial debe ser inmediata.",
            "La escalada absurda debe nacer de una lógica reconocible, no de ruido aleatorio.",
            "La novedad no puede ser solo sustituir un objeto manteniendo el mismo mecanismo causal del gag 001.",
            "No convertir el resultado en una receta fija ni imitar mecánicamente el contexto semántico.",
            "No ejecutar herramientas, acciones, cambios de archivos ni cambios de canon.",
        ),
        available_tools=(),
        prior_work=(
            "El contexto semántico actual y el protocolo colaborativo están cerrados y verificados en verde.",
            "El primer experimento de generación Qwen llegó correctamente hasta Core pero terminó en human_review por una salida estructurada inválida: elementos como cadenas en lugar de objetos con intención explícita.",
            "El objetivo de esta prueba es colaboración creativa concreta y no una decisión booleana, de elección o puntuación.",
        ),
        known_failures=(
            "Salida vaga o genérica que no usa el contexto suministrado.",
            "Repetición del mecanismo causal del gag 001 disfrazada como novedad.",
            "Salida estructurada incompleta o ambigua.",
            "Intentos de atribuir al colaborador autoridad sobre canon, decisiones Core o ejecución.",
        ),
        expected_output=DEFAULT_OUTPUT,
        autonomy="advisory",
        interrupt_policy="needs_input_only",
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one bounded local Qwen collaboration experiment."
    )
    parser.add_argument("--run-id", required=True, help="Unique experiment/run identifier.")
    parser.add_argument("--idea", default=DEFAULT_IDEA, help="Concrete creative objective.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model ID exposed by the local server.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="OpenAI-compatible base URL.")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("LOCAL_QWEN_API_KEY", "local"),
        help="Local runtime API key value. Defaults to a non-secret local placeholder.",
    )
    parser.add_argument(
        "--artifact-path",
        required=True,
        type=Path,
        help="Path where the CollaborationExecutionRecord JSON will be written.",
    )
    return parser


def _write_record(path: Path, record: CollaborationExecutionRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record.to_json() + "\n", encoding="utf-8")


def run_experiment(
    *,
    run_id: str,
    idea: str,
    model: str,
    base_url: str,
    api_key: str,
    artifact_path: str | Path,
    client: Any | None = None,
) -> CollaborationExecutionRecord:
    envelope = build_work_envelope(run_id=run_id, idea=idea)
    if client is None:
        client = OpenAI(api_key=api_key, base_url=base_url, max_retries=0)
    provider = LocalStructuredCollaborationProvider(
        client,
        model=model,
        provider_id="local-qwen-collaboration",
        temperature=0.0,
    )
    record = execute_collaboration(provider, envelope)
    _write_record(Path(artifact_path), record)
    return record


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        record = run_experiment(
            run_id=args.run_id,
            idea=args.idea,
            model=args.model,
            base_url=args.base_url,
            api_key=args.api_key,
            artifact_path=args.artifact_path,
        )
    except Exception as exc:
        raise SystemExit(f"local collaboration experiment failed: {exc}") from exc

    print(
        json.dumps(
            {
                "run_id": record.envelope.envelope_id,
                "provider_id": record.provider_id,
                "model_id": record.model_id,
                "status": record.update.status,
                "summary": record.update.summary,
                "needs_input": record.update.needs_input,
                "blockers": list(record.update.blockers),
                "attention_required": record.update.attention_required,
                "artifact_path": str(args.artifact_path),
                "envelope_digest": record.envelope_digest,
                "update_digest": record.update_digest,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print("\n=== COLLABORATION OUTPUT ===")
    print(json.dumps(record.update.output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_IDEA",
    "DEFAULT_MODEL",
    "DEFAULT_OUTPUT",
    "build_argument_parser",
    "build_work_envelope",
    "main",
    "run_experiment",
]
