# Codex CLI Transport

## Purpose

CodexCliTransport is the first concrete implementation of the provider-neutral
CodexTransport boundary. It invokes the installed Codex CLI in non-interactive
mode and translates its JSONL execution stream into CodexTaskResult.

The transport is deliberately outside Core.

## Execution mode

For analysis tasks it invokes codex exec with --json --ephemeral --sandbox read-only
and passes the compiled task prompt as the final positional argument.

For implementation, repair and improvement tasks it uses --sandbox workspace-write.

Important CLI compatibility note: the installed Codex CLI 0.155.1 rejects
--ask-for-approval and -a when they are placed after the exec subcommand. The
transport therefore does not emit either approval flag. The provider's exec mode
is non-interactive; the execution bridge remains responsible for the project's
explicit human-approval gate, while --sandbox remains the transport's runtime
autonomy boundary. This avoids coupling the adapter to an option that the
installed exec parser does not accept. Upstream Codex CLI issue reports document
the same post-exec rejection behavior.

The task prompt contains the issuer, objective, context, allowed/protected paths,
constraints, acceptance criteria and verification commands. The transport also
refuses to run when the repository branch or base commit does not match the task,
or when the working tree is already dirty.

OpenAI's current Codex documentation specifies codex exec for non-interactive
automation and documents JSONL output with --json, plus read-only and
workspace-write sandbox modes for controlled automation.

## Result extraction

The transport parses Codex JSONL events, captures the last agent message as the
task summary, records declared verification commands observed in command events,
derives changed paths from Git relative to the pre-execution commit, and computes
a deterministic diff digest.

A local JSONL trace may be written with trace_path. Trace files are runtime
artifacts and must not be committed because they may contain execution data.

## Scope boundary

The bridge remains the authoritative gate for explicit human approval and final
task-result validation. The transport cannot grant Core authority.

For the first real smoke test, use an analysis task. This validates the actual
Codex CLI connection without giving the first experiment write permission.
Only after that succeeds should we execute a bounded implementation task.

## Current non-goals

- no API-key creation or secret management in source code;
- no automatic merge or commit;
- no provider-specific logic in Core;
- no use of danger-full-access;
- no autonomous bypass of human approval.

## Live smoke test

The repository includes `scripts/run_codex_smoke_test.py` for the first real execution. It builds a task from the current branch and HEAD, requires an explicit `--approve`, runs in `analysis` mode, and returns a non-zero exit code if the execution fails or files change. The trace defaults to `/tmp/arsa-pisha-codex-smoke.jsonl`.

Run from the repository root after a green closure:

```bash
PYTHONPATH=. python scripts/run_codex_smoke_test.py --approve
```

The first live run is deliberately read-only. After it succeeds, the next task can use `workspace-write` for a bounded implementation mission.

## Codespace setup

The current Codespace failure was `codex_executable_not_found`. The official Codex CLI documentation currently provides a standalone macOS/Linux installer:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

After installation, start a fresh shell or refresh the command lookup and verify:

```bash
codex --version
```

Then run `codex` from the repository root and complete the authentication method offered by the CLI. Do not put tokens or credentials in the repository, `AGENTS.md`, or task payloads. The non-interactive transport can reuse Codex's stored CLI authentication; current OpenAI documentation also supports explicit `CODEX_API_KEY` or `CODEX_ACCESS_TOKEN` flows for automation, but no credential is committed by this project.

For a quick environment check before the live smoke test:

```bash
bash scripts/check_codex_environment.sh
```
