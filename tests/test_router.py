import unittest

from core.router import route_idea


class RouterTests(unittest.TestCase):

    def test_gag_route(self):
        decision = route_idea(
            "Crear un gag nuevo de Illo y Killo"
        )
        self.assertEqual(decision.route, "gag")
        self.assertFalse(decision.requires_human_review)

    def test_parody_route(self):
        decision = route_idea(
            "Illo y Killo en una parodia de Peaky Blinders"
        )
        self.assertEqual(decision.route, "parody")

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
