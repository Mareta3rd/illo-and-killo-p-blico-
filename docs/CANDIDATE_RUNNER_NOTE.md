# Candidate runner note

This is the first minimal composition runner for the Groq/Qwen candidate pipeline.

It intentionally stays textual-only and does not add image handling, multimodal planning,
or a new Core decision layer. The current executor contract remains unchanged and must be
extended only through a controlled, explicit future change when multimodal behavior is
required.
