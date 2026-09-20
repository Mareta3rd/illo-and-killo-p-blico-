# Visual Critique Layer

## Purpose

The next major capability is multimodal visual critique: a reviewer that can
look at a generated image and describe concrete observations without becoming
a second canon system.

## What the reviewer should examine

- **character_fidelity** — whether Arsa and Pisha remain visually recognizable;
- **gag_readability** — whether the primary gag reads immediately and the second
  reading adds value rather than noise;
- **composition_hierarchy** — whether scale, placement, salience and negative
  space direct the eye correctly;
- **motion_and_pose** — whether body mechanics, gesture and action communicate;
- **style_coherence** — whether line, shape, rendering and character treatment
  belong to the same visual universe;
- **cultural_integration** — whether Andalusian references are integrated rather
  than pasted on as tourist decoration;
- **production_fit** — whether the image makes sense for the intended support,
  such as white textile or a mug composition.

## No aesthetic score

The reviewer should report observations, evidence and confidence, not a numeric
taste score. A finding can be useful without being a hard failure.

States are deliberately limited to:

`observed` · `uncertain` · `not_applicable`

Confidence is separate:

`high` · `medium` · `low`

An uncertain observation must not silently become a canon violation. It is
feedback for another pass or a human review decision.

## Architecture

`image -> multimodal reviewer -> VisualCritiqueReport -> creative feedback / Core evaluation`

The multimodal reviewer proposes observations. Core remains responsible for
canonical decisions. Creative feedback may use high-confidence observations to
request another generation, while ambiguous aesthetic judgements remain soft.

## Current implementation

`core/visual_critique.py` defines the provider-neutral contract and closed schema.
`core/gemini_visual_reviewer.py` now provides the first concrete multimodal
reviewer adapter: it sends the supplied image to Gemini with a structured visual
review schema, requires one finding for every requested dimension, and returns
only a `VisualCritiqueReport`.

The adapter is observational and does not score taste or make Core decisions.
The next controlled experiment is a real review of an Arsa & Pisha image,
starting with a deliberately bounded test artifact before any integration into
the creative-feedback loop.
