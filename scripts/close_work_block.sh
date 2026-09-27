#!/usr/bin/env bash
set -euo pipefail

# Guardrail for closing a work block. This script verifies the repository state;
# it intentionally does not commit or push automatically, and it never edits
# the handoff. Those steps require explicit judgment about what is being saved.

printf '%s\n' '== WORK BLOCK CLOSE CHECK =='
printf '%s\n' '0) Synchronizing with the active branch upstream...'
bash scripts/sync_work_block.sh

printf '\n%s\n' '1) Running complete test suite...'
PYTHONPATH=. pytest -q

printf '\n%s\n' '2) Checking whitespace errors...'
git diff --check

printf '\n%s\n' '3) Working tree...'
git status --short

printf '\n%s\n' '4) Diff summary...'
git diff --stat

printf '\n%s\n' '5) Final synchronization check...'
bash scripts/sync_work_block.sh --check-only

printf '\n%s\n' '6) Current checkpoint...'
git rev-parse --short HEAD

cat <<'EOF'

== NEXT HUMAN STEPS ==
- Confirm no accidental/generated files or secrets are present.
- Commit the completed block with a descriptive message.
- Push the active branch.
- Update docs/AI_HANDOFF.md with the new checkpoint, verified tests,
  decisions, unresolved gaps, and one explicit next target.
- Stop at the stable checkpoint.

SYNC RULES:
- A clean local branch that is behind the upstream is fast-forwarded automatically.
- Local uncommitted changes never get overwritten automatically.
- A local branch that is ahead must be pushed before the block can close.
- Diverged histories stop the gate and require explicit reconciliation.
- If the upstream advances while tests are running, the final check fails so
  the suite can be rerun against the newer checkpoint.
EOF
