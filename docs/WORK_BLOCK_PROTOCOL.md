# WORK BLOCK PROTOCOL

This repository is worked in closed, auditable blocks. The goal is to finish a coherent problem, verify it, save it, document it, and leave one clear next direction rather than carrying unresolved state between sessions.

## Shared-branch synchronization

The active work branch can be changed from both the user's Codespace and the GitHub-backed execution path. Synchronization is therefore a first-class work-block invariant.

### Before starting or resuming a block

Run:

```bash
git status --short
bash scripts/sync_work_block.sh
```

The synchronization script fetches `origin`, detects the branch upstream, and classifies the state as:

- `SYNC: GREEN` — local HEAD matches upstream;
- `SYNC: BEHIND` — remote has commits that are not local;
- `SYNC: AHEAD` — local has commits not yet pushed;
- `SYNC: DIVERGED` — local and remote histories require explicit reconciliation;
- `SYNC: BEHIND + DIRTY` — a safe fast-forward is blocked by uncommitted local work.

A clean local branch that is behind is fast-forwarded automatically. Uncommitted work is never overwritten automatically. Ahead and diverged states stop the flow rather than being force-reconciled.

### Before remote writes

When an execution agent writes through the GitHub path, it must refresh the target branch first and base the write on the current remote checkpoint. The agent must not update files from a stale branch snapshot.

After remote writes, the Codespace synchronizes before continuing.

### During closure

`scripts/close_work_block.sh` performs a synchronization preflight before the complete test suite and a final synchronization check after all verification.

The final check is intentionally read-only. If the upstream advanced while tests were running, closure fails so the suite can be rerun against the newer checkpoint.

This protects against the failure mode where tests are green for an older commit while the shared remote branch has already moved.

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

For a new session, use the active branch rather than assuming `feature/semantic-model`:

```bash
git status --short
bash scripts/sync_work_block.sh
PYTHONPATH=. pytest -q
```

Then read `docs/AI_HANDOFF.md` and continue only from its documented checkpoint and direction.

## Closure invariant

A work block is closed only when all of these are true:

`solved + synchronized + verified + inspected + committed + pushed + handed-off + next-direction-marked`

The conversation is transient context. `docs/AI_HANDOFF.md` is the durable project state.
