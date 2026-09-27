# Codex project instructions

## Start here
- Read `docs/AI_HANDOFF.md` before making changes.
- Treat Arsa & Pisha as current canon. Historical Illo & Killo and earlier material are reference only.
- Preserve the Core authority boundary: providers and Codex execute or observe; Core owns canon, evidence, evaluation and final decisions.

## Repository discipline
- Work only inside the task scope you were given.
- Never put secrets, tokens or credentials into the repository.
- Do not commit or push unless the task explicitly authorizes that action.
- Prefer small coherent changes and keep the working tree inspectable.
- Use `bash scripts/close_work_block.sh` for the repository's complete verification gate when the task asks for closure.
- The closure script sets the repository Python path correctly; do not replace it with an unrelated test invocation.

## Shared-branch synchronization
- The active work branch may be written from both the user's Codespace and the GitHub-backed execution path. Treat its remote branch as shared state.
- Before writing through GitHub to the active branch, refresh the branch head and base any file/tree update on that current remote state. Never write against a stale branch head.
- After remote changes are made, the Codespace must synchronize with `bash scripts/sync_work_block.sh` before continuing local work or running the closure gate.
- Never force-push to reconcile a shared branch.
- A clean local branch that is behind its upstream may be fast-forwarded automatically by `scripts/sync_work_block.sh`; dirty, ahead or diverged states require explicit human reconciliation.
- If the upstream branch advances after tests start, the closure gate must detect that change and require a rerun on the newer checkpoint.

## Creative system
- Read `docs/CANON_100.md`, `docs/HUMOR.md` and `docs/ATTITUDE_AND_MAGNETISM.md` when a task touches creative behavior.
- `ATTITUDE_AND_MAGNETISM` is a direction, not a scoring rule: preserve freedom, variety and human art direction.
- Canon is a boundary, not a template. Avoid noun substitution disguised as novelty.

## Codex role
- You are an execution agent, not a Core decision-maker.
- Respect the `CodexTask` scope, protected paths and acceptance criteria supplied by the host.
- Never silently promote your output to canon.
- Report what you actually changed, what you tested and any blocker you encountered.
