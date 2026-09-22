#!/usr/bin/env bash
set -euo pipefail

echo "== Codex CLI environment check =="
echo "Shell: ${SHELL:-unknown}"

if command -v codex >/dev/null 2>&1; then
  echo "codex: $(command -v codex)"
  codex --version
else
  echo "codex: NOT FOUND"
  echo
  echo "Install the current Codex CLI with:"
  echo "  curl -fsSL https://chatgpt.com/codex/install.sh | sh"
  echo
  echo "Then open a new shell (or refresh PATH) and run:"
  echo "  codex --version"
  exit 2
fi

echo
echo "Next: run \"codex\" from the repository root and complete the available login flow."
echo "Do not place credentials in the repository or in AGENTS.md."