import copy
import unittest
from pathlib import Path

from core.canon_guard import validate_piece
from core.library_guard import (
    validate_library_catalog,
    validate_library_element,
    validate_library_elements,
)
from core.loader import load_repository


ROOT = Path(__file__).resolve().parents[1]


class LibraryGuardTests(unittest.TestCase):
    KNOWLEDGE = {
        "objects": {
            "botijo": {
                "name": "Botijo",
                "role": "everyday_prop",
                "invariants": ["simplified_iconic_form"],
            },
        },
        "fauna": {
            "gaviota": {
                "name": "Gaviota",
                "role": "recurring_support",
                "invariants": ["readable_as_seagull"],
            },
        },
        "heritage": {
            "alhambra": {
                "name": "Alhambra",
                "role": "heritage_icon",
                "invariants": ["recognizable_silhouette"],
            },
        },
    }

    def test_known_object_reference_is_valid(self):
        issues = validate_library_element(
            {"library": "objects", "id": "botijo", "intention": "scene_support"},
            self.KNOWLEDGE,
        )
        self.assertEqual(issues, ())

    def test_known_fauna_reference_is_valid(self):
        issues = validate_library_element(
            {"library": "fauna", "id": "gaviota", "intention": "background_support"},
            self.KNOWLEDGE,
        )
        self.assertEqual(issues, ())

    def test_known_heritage_reference_is_valid(self):
        issues = validate_library_element(
            {"library": "heritage", "id": "alhambra", "intention": "heritage_reference"},
            self.KNOWLEDGE,
        )
        self.assertEqual(issues, ())

    def test_unknown_entry_is_rejected(self):
        issues = validate_library_element(
            {"library": "objects", "id": "unknown_object", "intention": "scene_support"},
            self.KNOWLEDGE,
        )
        self.assertIn("LIBRARY_ENTRY_NOT_FOUND", {issue.code for issue in issues})

    def test_invalid_library_is_rejected(self):
        issues = validate_library_element(
            {"library": "characters", "id": "killo", "intention": "character_identity"},
            self.KNOWLEDGE,
        )
        self.assertIn("LIBRARY_INVALID", {issue.code for issue in issues})

    def test_library_reference_requires_intention(self):
        issues = validate_library_element(
            {"library": "objects", "id": "botijo"},
            self.KNOWLEDGE,
        )
        self.assertIn("LIBRARY_INTENTION_MISSING", {issue.code for issue in issues})

    def test_library_reference_requires_id(self):
        issues = validate_library_element(
            {"library": "objects", "intention": "scene_support"},
            self.KNOWLEDGE,
        )
        self.assertIn("LIBRARY_ID_MISSING", {issue.code for issue in issues})

    def test_non_namespaced_elements_are_not_invented_into_library_references(self):
        issues = validate_library_elements(
            [{"id": "botijo", "intention": "scene_support"}],
            self.KNOWLEDGE,
        )
        self.assertEqual(issues, ())

    def test_guard_does_not_mutate_inputs(self):
        element = {"library": "objects", "id": "botijo", "intention": "scene_support"}
        knowledge = copy.deepcopy(self.KNOWLEDGE)
        element_before = copy.deepcopy(element)
        knowledge_before = copy.deepcopy(knowledge)

        validate_library_element(element, knowledge)

        self.assertEqual(element, element_before)
        self.assertEqual(knowledge, knowledge_before)

    def test_catalog_rejects_missing_name(self):
        knowledge = copy.deepcopy(self.KNOWLEDGE)
        del knowledge["objects"]["botijo"]["name"]
        issues = validate_library_catalog(knowledge)
        self.assertIn("LIBRARY_NAME_MISSING", {issue.code for issue in issues})

    def test_catalog_rejects_missing_role(self):
        knowledge = copy.deepcopy(self.KNOWLEDGE)
        del knowledge["fauna"]["gaviota"]["role"]
        issues = validate_library_catalog(knowledge)
        self.assertIn("LIBRARY_ROLE_MISSING", {issue.code for issue in issues})

    def test_catalog_rejects_missing_invariants(self):
        knowledge = copy.deepcopy(self.KNOWLEDGE)
        knowledge["heritage"]["alhambra"]["invariants"] = []
        issues = validate_library_catalog(knowledge)
        self.assertIn("LIBRARY_INVARIANTS_MISSING", {issue.code for issue in issues})

    def test_catalog_rejects_invalid_invariant(self):
        knowledge = copy.deepcopy(self.KNOWLEDGE)
        knowledge["objects"]["botijo"]["invariants"] = ["", 3]
        issues = validate_library_catalog(knowledge)
        self.assertIn("LIBRARY_INVARIANT_INVALID", {issue.code for issue in issues})

    def test_real_repository_catalog_is_structurally_valid(self):
        knowledge = load_repository(ROOT)
        self.assertEqual(validate_library_catalog(knowledge), ())


if __name__ == "__main__":
    unittest.main()
