# WORK BLOCK PROTOCOL

This repository is worked in closed, auditable blocks. The goal is to finish a coherent problem, verify it, save it, document it, and leave one clear next direction rather than carrying unresolved state between sessions.

## Standard cycle

### 1. Solve
Define the current block objective before implementation. Keep unrelated improvements out of scope.

### 2. Verify
Run focused checks during implementation. For integration or architectural changes, finish with the complete suite:

```bash
PYTHONPATH=. pytest -q
```

A failing test means the block is not closed.

### 3. Inspect
Before saving, check:

```bash
git status --short
git diff --check
git diff --stat
```

Look specifically for accidental files, generated artifacts, secrets, stale references, and unintended canon changes.

### 4. Save
Commit the coherent block with a descriptive message and push the active branch when ready. Do not leave a known-good block only in the local Codespace.

### 5. Record
Update `docs/AI_HANDOFF.md` with:

- current branch and checkpoint;
- verified test result;
- decisions made;
- work completed;
- unresolved issues;
- exact next implementation target.

### 6. Mark direction
The handoff must contain one primary next target and state what remains deliberately out of scope until that target is closed.

### 7. Stop
Once the block is verified, saved and handed off, stop. Do not open a second architectural front merely because the session remains active.

## Session start

Start every new session with:

```bash
git status --short
git pull --rebase origin feature/semantic-model
PYTHONPATH=. pytest -q
```

Then read `docs/AI_HANDOFF.md` and continue only from its documented checkpoint and direction.

## Closure invariant

A work block is closed only when all of these are true:

`solved + verified + inspected + committed + pushed + handed-off + next-direction-marked`

The conversation is transient context. `docs/AI_HANDOFF.md` is the durable project state.
