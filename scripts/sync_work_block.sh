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

git fetch origin

local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "$upstream_ref")"

if [[ "$local_sha" == "$remote_sha" ]]; then
  printf 'SYNC: GREEN — local HEAD matches %s (%s)\n' "$upstream_ref" "$(git rev-parse --short HEAD)"
  exit 0
fi

if git merge-base --is-ancestor "$local_sha" "$remote_sha"; then
  if [[ "$mode" == "check" ]]; then
    printf 'SYNC: BEHIND — %s is ahead of local HEAD (%s -> %s). Pull before continuing.\n'       "$upstream_ref" "$(git rev-parse --short "$local_sha")" "$(git rev-parse --short "$remote_sha")" >&2
    exit 3
  fi

  if [[ -n "$(git status --porcelain)" ]]; then
    printf 'SYNC: BEHIND + DIRTY — local changes prevent a safe fast-forward.\n' >&2
    printf '       Commit/stash local work, then run this script again.\n' >&2
    exit 4
  fi

  git merge --ff-only "$upstream_ref"
  printf 'SYNC: GREEN — fast-forwarded local branch to %s (%s)\n'     "$upstream_ref" "$(git rev-parse --short HEAD)"
  exit 0
fi

if git merge-base --is-ancestor "$remote_sha" "$local_sha"; then
  printf 'SYNC: AHEAD — local HEAD is ahead of %s (%s -> %s). Push before continuing.\n'     "$upstream_ref" "$(git rev-parse --short "$remote_sha")" "$(git rev-parse --short "$local_sha")" >&2
  exit 5
fi

printf 'SYNC: DIVERGED — local and %s have different histories. Reconcile explicitly; do not force-push.\n'   "$upstream_ref" >&2
printf '       local:  %s\n' "$(git rev-parse --short "$local_sha")" >&2
printf '       remote: %s\n' "$(git rev-parse --short "$remote_sha")" >&2
exit 6
