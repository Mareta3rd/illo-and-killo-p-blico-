import unittest

from core.router import route_idea


class RouterTests(unittest.TestCase):

    def test_gag_route(self):
        decision = route_idea(
            "Crear un gag nuevo de Xoxo y Pisha"
        )
        self.assertEqual(decision.route, "gag")
        self.assertFalse(decision.requires_human_review)

    def test_parody_route(self):
        decision = route_idea(
            "Xoxo y Pisha en una parodia de Peaky Blinders"
        )
        self.assertEqual(decision.route, "parody")

    def test_character_keywords_route_to_character(self):
        self.assertEqual(route_idea("Diseñar a Xoxo").route, "character")
        self.assertEqual(route_idea("Revisar a Pisha").route, "character")

    def test_merchandising_route(self):
        decision = route_idea(
            "Preparar un diseño para una taza"
        )
        self.assertEqual(decision.route, "merchandising")

    def test_ambiguous_idea_requires_human_review(self):
        decision = route_idea("")
        self.assertTrue(decision.requires_human_review)


if __name__ == "__main__":
    unittest.main()
