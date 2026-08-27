# Groq + Qwen 3.6 27B Provider Phase

## Objective
Add a second practical real evidence provider using Groq-hosted Qwen 3.6 27B, while reusing the existing provider-neutral evidence architecture and keeping Core unchanged.

Target:

Groq transport
→ Qwen 3.6 27B
→ provider adapter/parser
→ ExternalEvidenceRecord
→ ProviderEvidenceObservation
→ EvidenceSnapshot
→ existing Core pipeline/evaluator
→ Core decision

## Verified current external contract
Groq documentation currently lists Qwen 3.6 27B as:
- model ID: qwen/qwen3.6-27b
- multimodal: text + images
- vision
- reasoning
- JSON Object Mode
- 131K context window
- max 16,384 output tokens
- image input supported

Groq also documents an OpenAI-compatible API and Responses API, including image input. The project can therefore use the already-installed OpenAI Python SDK with:
- base_url=https://api.groq.com/openai/v1
- GROQ_API_KEY from environment/Codespaces secret

Do not assume free-tier capacity is unlimited. Verify the current account limits in Groq Console when the real account is available.

## Cost / availability policy
Groq has a Free tier with published rate limits. Exact limits are account/model dependent and must be checked in the current Groq Console. Never design the system around unlimited free usage.

The first candidate model is explicitly:
qwen/qwen3.6-27b

The model is currently marked Preview by Groq. Treat that status as operational metadata, not as a Core semantic property.

## Non-negotiable boundaries
- Groq/Qwen is evidence only, never Core authority.
- Provider output must normalize to ExternalEvidenceRecord only.
- CONFIRMED / CONTRADICTED / UNKNOWN remain observations until Core evaluates them.
- provider, run_id, model and transport metadata must not become claims.
- Do not rewrite Gag 001 four-segment canonical claims into the three-segment contractual taxonomy.
- Do not add Groq/Qwen branches to pipeline.py or evidence_evaluator.py.
- Do not change Gemini behavior.
- Do not weaken parser validation to accommodate provider output.
- Credentials must stay outside source, tests, commits and chat.

## Reuse
Reuse the existing provider-neutral composition:
- collect_provider_observation(...)
- snapshot_from_provider_observation(...)
- run_provider_evidence_pipeline(...)

Do not create Groq-specific observation or snapshot types.

## Phase A — provider-specific contract with fake transport
Before network access:
1. inspect the existing Gemini and OpenAI provider contracts;
2. use the existing openai SDK rather than adding groq SDK unless a concrete incompatibility is demonstrated;
3. implement a Groq-specific transport around the OpenAI-compatible endpoint;
4. use an injected/fake Responses client in tests;
5. use Qwen model ID qwen/qwen3.6-27b;
6. construct multimodal Responses input with input_text + input_image;
7. use data URL Base64 image input;
8. use structured JSON Schema if the model/API combination demonstrably supports it; otherwise stop and report the limitation rather than silently falling back to an unconstrained parser contract.

## Phase B — conformance
Required tests:
- model and base URL are configurable;
- requested keys pass through unchanged;
- input image is encoded correctly;
- MIME type is preserved;
- structured schema is exact;
- output text is passed to parser;
- confirmed requires supporting sources;
- contradicted requires contradicting sources;
- unknown has no sources;
- duplicate/unrequested/missing claims fail;
- invalid verdict fails;
- provider failures become boundary errors;
- Core decision vocabulary is rejected as provider output;
- adapter does not evaluate canon or candidate quality.

## Phase C — provider-neutral integration
After Phase A/B pass, connect through the existing composition only:
Groq/Qwen adapter
→ ProviderEvidenceObservation
→ EvidenceSnapshot
→ run_provider_evidence_pipeline

Test both:
- fauna/mosquito_tigre/readable_as_mosquito
- gag/001/composition/illo_primary

The first may receive contractual evaluation; the second must remain a canonical claim without invented contractual evaluation.

## Phase D — real access
After tests are green:
1. create Groq account/project;
2. create a Groq API key;
3. store it as Codespaces secret GROQ_API_KEY;
4. verify presence only by boolean/length, never print the key;
5. run one text-only connectivity call;
6. run one real structured/image evidence call;
7. preserve the exact provider observation;
8. do not auto-retry to obtain a preferred verdict.

## Phase E — real Core end-to-end
Run one real contractual invariant through:
Groq/Qwen real
→ adapter
→ observation
→ snapshot
→ contractual evaluation
→ Core decision

The provider must not return accept, continue, or human_review.

## Model-selection discipline
Do not introduce fallback models automatically. If qwen/qwen3.6-27b is unavailable for the account or capability combination, report the exact limitation and stop for human model-selection review.

## OpenAI relationship
OpenAI API remains a prepared provider but may be blocked by quota. Its adapter should not be reused as a semantic provider identity. The Groq transport may legitimately use the OpenAI Python SDK because Groq exposes an OpenAI-compatible endpoint; the adapter and provider identity remain Groq/Qwen-specific.

## Exit criteria
Groq/Qwen is operational when:
- conformance tests are green;
- provider-neutral integration is green;
- real connectivity is verified;
- one real perceptual invariant yields a valid evidence record;
- that record crosses the snapshot boundary;
- one real Core decision is produced by Core;
- complete suite remains green;
- no Groq/Qwen-specific Core path exists.
