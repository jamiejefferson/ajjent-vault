#!/usr/bin/env bash
# Register the SessionEnd hook so project indexes stay current on their own.
#
#   ./scripts/install.sh            # install into ~/.claude/settings.json
#   ./scripts/install.sh --print    # print the JSON block and change nothing
#
# Idempotent: running it twice does not duplicate the hook.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# The vault is this repo by default, but the scripts work against any vault.
# Set AJJENT_VAULT to point them at one that lives elsewhere.
VAULT="${AJJENT_VAULT:-$REPO}"
HOOK="$REPO/scripts/session-close.py"
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
CMD="AJJENT_VAULT='$VAULT' python3 '$HOOK'"

command -v jq >/dev/null 2>&1 || { echo "jq is required. brew install jq"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 is required."; exit 1; }
chmod +x "$HOOK"

BLOCK=$(jq -n --arg cmd "$CMD" '{
  hooks: {
    SessionEnd: [
      { hooks: [ { type: "command", command: $cmd, timeout: 30 } ] }
    ]
  }
}')

if [[ "${1:-}" == "--print" ]]; then
  echo "Add this to $SETTINGS (merging with any existing hooks):"
  echo "$BLOCK"
  exit 0
fi

mkdir -p "$(dirname "$SETTINGS")"
[[ -f "$SETTINGS" ]] || echo '{}' > "$SETTINGS"

if ! jq empty "$SETTINGS" 2>/dev/null; then
  echo "$SETTINGS is not valid JSON. Fix it first — a malformed settings file"
  echo "silently disables every setting in it, not just this hook."
  exit 1
fi

if jq -e --arg h "$HOOK" '.hooks.SessionEnd[]?.hooks[]?
      | select(.command? and (.command | contains($h)))' "$SETTINGS" >/dev/null 2>&1; then
  echo "Already installed. Nothing to do."
  exit 0
fi

cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y%m%d%H%M%S)"
tmp=$(mktemp)
jq --arg cmd "$CMD" '
  .hooks //= {} |
  .hooks.SessionEnd //= [] |
  .hooks.SessionEnd += [ { hooks: [ { type: "command", command: $cmd, timeout: 30 } ] } ]
' "$SETTINGS" > "$tmp"

jq empty "$tmp" || { echo "Refusing to write invalid JSON."; rm -f "$tmp"; exit 1; }
mv "$tmp" "$SETTINGS"

echo "Installed the SessionEnd hook into $SETTINGS"
echo "Backup written alongside it."
echo
echo "It fires when a session ends inside a repo that a project note points at."
echo "Open /hooks once, or restart Claude Code, for it to be picked up."
