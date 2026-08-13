#!/usr/bin/env bash
# anti-slop Stop hook for Claude Code.
#
# Makes the quality gate mechanical instead of voluntary: when Claude tries to
# end its turn in a project that has a slopcheck baseline, the gate runs; if it
# fails, the stop is blocked (exit 2) and the failure report is fed back to
# Claude so it refactors before finishing.
#
# Behavior:
#   * No baseline in CWD  -> exit 0 silently (the hook never nags projects that
#     haven't opted in; opt in by running `slopcheck.py baseline .`).
#   * Gate passes         -> exit 0 (baseline ratchets forward automatically).
#   * Gate fails          -> exit 2, failure summary on stderr (shown to Claude).
#   * slopcheck unavailable/errors -> exit 0 (never brick the session over tooling).
#
# Install (user-wide) in ~/.claude/settings.json:
#   { "hooks": { "Stop": [ { "hooks": [ { "type": "command",
#     "command": "bash <ABSOLUTE_PATH_TO>/skills/anti-slop/scripts/stop-hook.sh" } ] } ] } }
#
# Loop safety: Claude Code sets stop_hook_active in the hook input when a Stop
# hook already blocked once this turn; we allow the second stop through to avoid
# infinite block loops (the failure report has already been delivered).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SLOPCHECK="$SCRIPT_DIR/slopcheck.py"

INPUT="$(cat 2>/dev/null || true)"
if printf '%s' "$INPUT" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

[ -f ".slopcheck/baseline.json" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0
[ -f "$SLOPCHECK" ] || exit 0

OUT="$(python3 "$SLOPCHECK" check . 2>&1)"
STATUS=$?

if [ "$STATUS" -eq 1 ]; then
  {
    echo "anti-slop gate FAILED — the turn cannot end with a failing quality gate."
    printf '%s\n' "$OUT" | grep -E "FAIL|WARN|erosion|duplication|dead code|max function" | head -15
    echo "Refactor (extract helpers, unify clones, delete dead code), re-run tests,"
    echo "then re-run: python3 $SLOPCHECK check ."
  } >&2
  exit 2
fi

exit 0
