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

The synchronization script refreshes `origin` and **directly probes the authoritative remote branch HEAD**. It classifies the state as:

- `SYNC: GREEN` — local HEAD matches the authoritative remote HEAD;
- `SYNC: BEHIND` — remote has commits that are not local;
- `SYNC: AHEAD` — local has commits not yet pushed;
- `SYNC: DIVERGED` — local and remote histories require explicit reconciliation;
- `SYNC: BEHIND + DIRTY` — a safe fast-forward is blocked by uncommitted local work;
- `SYNC: REMOTE_MOVED_DURING_SYNC` — the shared branch moved during synchronization, so the gate stops and must be rerun.

A clean local branch that is behind is fast-forwarded automatically. Uncommitted work is never overwritten automatically. Ahead, diverged and moving-target states stop the flow rather than being force-reconciled.

The direct remote probe exists specifically for shared work: a GitHub-backed write may advance the remote branch without the user's local Codespace having incorporated that commit yet. The remote branch itself, not the conversation transcript or a stale tracking ref, is the authoritative checkpoint.

### Remote-write handshake

When an execution agent writes through the GitHub path:

1. Refresh and verify the target branch HEAD before writing.
2. Base the write on that exact remote checkpoint.
3. After the write, verify the resulting remote branch HEAD and record the exact resulting commit SHA.
4. Treat that SHA as a **remote-write receipt**.
5. Do not continue with local tests or edits until the user's Codespace has synchronized to that receipt with `bash scripts/sync_work_block.sh`.
6. The next test/closure command must run against that synchronized checkpoint.

A remote-write receipt is stronger than saying “the change was committed”: it identifies exactly which shared state the other work environment must consume.

When the GitHub write path is used for several coherent changes, consolidate them into one commit where practical so there is one receipt to synchronize.

### During closure

`scripts/close_work_block.sh` performs an authoritative synchronization preflight before the complete test suite and a read-only authoritative remote check after all verification.

If the remote branch advances while tests are running, closure fails. The suite must then be rerun after synchronization against the newer checkpoint.

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
- exact next implementation target;
- any remote-write receipt needed for another work environment to synchronize.

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
