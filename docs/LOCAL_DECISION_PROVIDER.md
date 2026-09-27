# Local decision provider prototype

## First candidate

The first local decision-capability target is Qwen3.8-27B in GGUF form, served by
llama.cpp through its OpenAI-compatible server interface.

The choice is pragmatic rather than a quality judgment: the model is available as an
open-weight 27B multimodal model, with a published GGUF path for local inference. llama.cpp
supports JSON Schema constrained output on its server endpoints, which matches the bounded
DecisionResult contract. This is a prototype, not an adoption decision.

## Contract

LocalStructuredDecisionProvider:

- receives the existing DecisionRequest;
- asks the local runtime for only value and optional confidence;
- uses the request allowed choices as the JSON Schema enum;
- validates the returned DecisionResult through the existing Core boundary;
- never executes an action;
- never returns Core decisions, canon mutations, routing instructions or evidence claims.

The provider is runtime-agnostic. The caller supplies an OpenAI-compatible client, so the
same adapter can target llama.cpp or another local server without making Core depend on the
runtime.

## First execution target

After the focused and complete test gates are green, run:

    PYTHONPATH=. python scripts/run_local_decision_benchmark.py

The default target assumes a local server at http://127.0.0.1:8080/v1 with the
Qwen3.8-27B-GGUF:Q4_K_M model. The benchmark excludes the harness-control fixture unless
--include-control is supplied.

The output is evidence only: expected-vs-observed values, repeatability, latency,
confidence, provider/model metadata and failures. It is not a provider ranking.

## Hardware note

Public third-party estimates put Q4_K_M around 18 GB total VRAM depending on context and
runtime. Treat that only as planning information; actual feasibility depends on the machine.
The project should not buy hardware or API access merely to run this experiment.