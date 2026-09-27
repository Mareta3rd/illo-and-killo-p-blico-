import json

import pytest

from core.capability_registry import CapabilityRegistry, CapabilityRecord, load_capability_registry


def test_repository_capability_registry_loads_and_queries():
    registry = load_capability_registry()

    assert isinstance(registry, CapabilityRegistry)
    assert registry.version == 1
    assert {record.id for record in registry.records} == {
        "execution.codex_cli",
        "decision.rules",
        "decision.jev",
        "orchestration.openai_agents_api",
        "computer_use.anthropic_cowork",
    }
    assert registry.get("decision.rules").status == "adopted"
    assert registry.get("decision.jev").status == "deferred_external_access"
    assert [record.id for record in registry.for_capability("decision")] == ["decision.rules", "decision.jev"]


def test_registry_serialization_is_deterministic_and_matches_source(tmp_path):
    from pathlib import Path

    source = Path(__file__).resolve().parents[1] / "data" / "capabilities.json"
    fixture = json.loads(source.read_text(encoding="utf-8"))
    path = tmp_path / "capabilities.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    registry = load_capability_registry(path)

    assert json.loads(registry.to_json()) == registry.to_dict()
    assert registry.to_json() == registry.to_json()
    assert registry.to_dict() == fixture


def test_registry_rejects_unknown_fields_and_duplicate_ids(tmp_path):
    from pathlib import Path

    source = Path(__file__).resolve().parents[1] / "data" / "capabilities.json"
    fixture = json.loads(source.read_text(encoding="utf-8"))

    fixture["capabilities"][0]["unexpected"] = "nope"
    unknown_path = tmp_path / "unknown.json"
    unknown_path.write_text(json.dumps(fixture), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly the record fields"):
        load_capability_registry(unknown_path)

    fixture = json.loads(source.read_text(encoding="utf-8"))
    fixture["capabilities"].append(dict(fixture["capabilities"][0]))
    duplicate_path = tmp_path / "duplicate.json"
    duplicate_path.write_text(json.dumps(fixture), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate capability id"):
        load_capability_registry(duplicate_path)


def test_registry_rejects_duplicate_values_in_string_lists(tmp_path):
    from pathlib import Path

    source = Path(__file__).resolve().parents[1] / "data" / "capabilities.json"
    fixture = json.loads(source.read_text(encoding="utf-8"))
    fixture["capabilities"][0]["strengths"].append(fixture["capabilities"][0]["strengths"][0])
    path = tmp_path / "duplicates.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    with pytest.raises(ValueError, match="strengths must not contain duplicates"):
        load_capability_registry(path)


def test_record_and_registry_type_boundaries():
    with pytest.raises(TypeError, match="tuple of strings"):
        CapabilityRecord(
            id="x",
            capability="decision",
            provider="test",
            product_or_runtime="test",
            status="evaluate",
            integration="local",
            cost_model="none",
            latency_character="fast",
            strengths=["one"],
            limitations=(),
            dependencies=(),
            security_boundary="none",
            replaceable_by=(),
            last_reviewed="2026-09-27",
            evidence=(),
        )

    with pytest.raises(TypeError, match="CapabilityRecord"):
        CapabilityRegistry(1, "2026-09-27", "stable", (object(),))
