#!/usr/bin/env bash
set -euo pipefail

mode="auto"
if [[ "${1:-}" == "--check-only" ]]; then
  mode="check"
elif [[ "${1:-}" != "" ]]; then
  printf 'Usage: %s [--check-only]\n' "$0" >&2
  exit 2
fi

upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
if [[ -z "$upstream_ref" ]]; then
  printf '%s\n' 'SYNC: NO_UPSTREAM — configure an upstream branch before continuing.' >&2
  exit 2
fi

upstream_remote="${upstream_ref%%/*}"
upstream_branch="${upstream_ref#*/}"
if [[ -z "$upstream_branch" || "$upstream_remote" == "$upstream_ref" ]]; then
  printf 'SYNC: INVALID_UPSTREAM — expected a remote tracking branch, got %s.\n' "$upstream_ref" >&2
  exit 2
fi

# Refresh local remote-tracking refs first, then query the actual remote ref directly.
# The direct probe avoids treating a stale/lagging tracking ref as authoritative when
# another execution path has just written the shared branch.
git fetch origin

probe_remote_sha() {
  local ref="refs/heads/$upstream_branch"
  local attempt
  local sha
  for attempt in 1 2 3; do
    sha="$(git ls-remote "$upstream_remote" "$ref" | awk 'NR == 1 {print $1}')"
    if [[ "$sha" =~ ^[0-9a-f]{40}$ ]]; then
      printf '%s' "$sha"
      return 0
    fi
    sleep 1
  done
  printf '%s\n' "SYNC: REMOTE_HEAD_UNAVAILABLE — could not read $ref directly from $upstream_remote." >&2
  return 7
}

local_sha="$(git rev-parse HEAD)"
remote_sha="$(probe_remote_sha)"

printf 'SYNC: PROBE — local %s | remote %s | %s/%s\n' \
  "$(git rev-parse --short "$local_sha")" "$(git rev-parse --short "$remote_sha")" "$upstream_remote" "$upstream_branch"

if [[ "$local_sha" == "$remote_sha" ]]; then
  printf 'SYNC: GREEN — local HEAD matches remote %s (%s)\n' "$upstream_ref" "$(git rev-parse --short HEAD)"
  exit 0
fi

if git merge-base --is-ancestor "$local_sha" "$remote_sha"; then
  if [[ "$mode" == "check" ]]; then
    printf 'SYNC: BEHIND — remote %s is ahead of local HEAD (%s -> %s). Pull before continuing.\n' \
      "$upstream_ref" "$(git rev-parse --short "$local_sha")" "$(git rev-parse --short "$remote_sha")" >&2
    exit 3
  fi

  if [[ -n "$(git status --porcelain)" ]]; then
    printf '%s\n' 'SYNC: BEHIND + DIRTY — local changes prevent a safe fast-forward.' >&2
    printf '%s\n' '       Commit/stash local work, then run this script again.' >&2
    exit 4
  fi

  git merge --ff-only "$upstream_ref"

  # A second authoritative probe closes the small race where the remote moves while
  # the local fast-forward is happening. Do not silently chase a moving target.
  final_remote_sha="$(probe_remote_sha)"
  final_local_sha="$(git rev-parse HEAD)"
  if [[ "$final_local_sha" != "$final_remote_sha" ]]; then
    printf 'SYNC: REMOTE_MOVED_DURING_SYNC — local %s | remote %s. Rerun sync before continuing.\n' \
      "$(git rev-parse --short "$final_local_sha")" "$(git rev-parse --short "$final_remote_sha")" >&2
    exit 8
  fi

  printf 'SYNC: GREEN — fast-forwarded local branch to remote %s (%s)\n' \
    "$upstream_ref" "$(git rev-parse --short HEAD)"
  exit 0
fi

if git merge-base --is-ancestor "$remote_sha" "$local_sha"; then
  printf 'SYNC: AHEAD — local HEAD is ahead of remote %s (%s -> %s). Push before continuing.\n' \
    "$upstream_ref" "$(git rev-parse --short "$remote_sha")" "$(git rev-parse --short "$local_sha")" >&2
  exit 5
fi

printf 'SYNC: DIVERGED — local and remote %s have different histories. Reconcile explicitly; do not force-push.\n' \
  "$upstream_ref" >&2
printf '       local:  %s\n' "$(git rev-parse --short "$local_sha")" >&2
printf '       remote: %s\n' "$(git rev-parse --short "$remote_sha")" >&2
exit 6
