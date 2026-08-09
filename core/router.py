from dataclasses import dataclass
from typing import Literal


Route = Literal[
    "character",
    "gag",
    "parody",
    "merchandising",
    "3d",
    "general",
]


@dataclass(frozen=True)
class RouteDecision:
    route: Route
    confidence: float
    requires_human_review: bool
    reason: str


_KEYWORDS: dict[Route, tuple[str, ...]] = {
    "character": (
        "personaje",
        "personajes",
        "character",
        "illo",
        "killo",
    ),
    "gag": (
        "gag",
        "chiste",
        "escena",
        "situación",
    ),
    "parody": (
        "parodia",
        "parody",
        "peaky blinders",
        "película",
        "serie",
    ),
    "merchandising": (
        "merchandising",
        "camiseta",
        "taza",
        "azulejo",
        "imán",
        "poster",
        "producto",
    ),
    "3d": (
        "3d",
        "modelo",
        "modelado",
        "glb",
        "gltf",
    ),
}


# Algunas rutas expresan una intención explícita.
# Tienen prioridad sobre coincidencias secundarias como "illo" o "killo".
_EXPLICIT_ROUTE_PRIORITY: tuple[Route, ...] = (
    "gag",
    "parody",
    "merchandising",
    "3d",
)


def route_idea(idea: str) -> RouteDecision:
    """
    Route an idea to the most appropriate workflow.

    The router identifies intent; it does not generate content
    and does not modify canon.

    Explicit workflow intent has priority over secondary
    character references. Ambiguous cases require human review.
    """
    normalized = idea.strip().lower()

    if not normalized:
        return RouteDecision(
            route="general",
            confidence=0.0,
            requires_human_review=True,
            reason="No se ha proporcionado una idea.",
        )

    # 1. First resolve explicit workflow intent.
    for route in _EXPLICIT_ROUTE_PRIORITY:
        if any(keyword in normalized for keyword in _KEYWORDS[route]):
            return RouteDecision(
                route=route,
                confidence=0.90,
                requires_human_review=False,
                reason=f"Intención explícita identificada: {route}.",
            )

    # 2. Fall back to ordinary keyword matching.
    matches: list[tuple[Route, int]] = []

    for route, keywords in _KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in normalized)
        if score:
            matches.append((route, score))

    if not matches:
        return RouteDecision(
            route="general",
            confidence=0.25,
            requires_human_review=True,
            reason="No se ha identificado una ruta suficientemente clara.",
        )

    matches.sort(key=lambda item: item[1], reverse=True)

    best_route, best_score = matches[0]

    tied = len(matches) > 1 and matches[1][1] == best_score

    if tied:
        return RouteDecision(
            route="general",
            confidence=0.25,
            requires_human_review=True,
            reason="Existen varias rutas igualmente plausibles.",
        )

    confidence = min(0.85, 0.55 + (best_score - 1) * 0.15)

    return RouteDecision(
        route=best_route,
        confidence=confidence,
        requires_human_review=False,
        reason=f"Ruta identificada por coincidencia temática: {best_route}.",
    )
