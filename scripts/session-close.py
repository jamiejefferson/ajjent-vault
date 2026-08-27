#!/usr/bin/env python3
"""
SessionEnd hook: keep project indexes current without anyone being asked.

Wired into Claude Code by scripts/install.sh. Set AJJENT_VAULT to the vault root
if the vault is not the parent of this script's directory.

Design notes, which are deliberate rather than incidental:

  * It writes only when there is EVIDENCE of work: new commits in the repo since
    the note's own last_touched. No commits means no write at all. Stamping a
    fresh date onto an unchanged note is precisely how a stale vault comes to look
    maintained, which is the failure this whole design exists to prevent.

  * It backfills from the note's own last_touched rather than from session start,
    so any session that ended without the hook firing is picked up by the next one.

  * It dedupes on short commit hash, so re-runs cannot double-log.

  * It never fails a session. Any error exits 0 and stays quiet.
"""
import json
import os
import re
import subprocess
import sys
import datetime
import glob

VAULT = os.environ.get(
    "AJJENT_VAULT",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
PROJECTS = os.path.join(VAULT, "Projects")
LOG_HEADING = "## Session log"
REPO_KEYS = ("repo", "repository", "path", "source", "code", "repo_path")
MAX_COMMITS = 20


def run(args):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def read_frontmatter(path):
    fm, inside = {}, False
    with open(path, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            s = line.rstrip("\n")
            if i == 0 and s.strip() == "---":
                inside = True
                continue
            if inside and s.strip() == "---":
                break
            if inside:
                m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", s)
                if m:
                    fm[m.group(1).lower()] = m.group(2).strip().strip("\"'")
    return fm


def find_index_for_repo(repo_root):
    """Explicit frontmatter pointer wins; folder-name match is the fallback."""
    repo_real = os.path.realpath(repo_root)
    name = norm(os.path.basename(repo_real))
    fallback = None
    for idx in sorted(glob.glob(os.path.join(PROJECTS, "*", "_index.md"))):
        try:
            fm = read_frontmatter(idx)
        except OSError:
            continue
        for k in REPO_KEYS:
            v = fm.get(k)
            if v and ("/" in v or "~" in v):
                try:
                    if os.path.realpath(os.path.expanduser(v.strip("`<>[] "))) == repo_real:
                        return idx
                except OSError:
                    continue
        if fallback is None and norm(os.path.basename(os.path.dirname(idx))) == name:
            fallback = idx
    return fallback


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if not os.path.isdir(cwd) or not os.path.isdir(PROJECTS):
        return

    repo_root = run(["git", "-C", cwd, "rev-parse", "--show-toplevel"])
    if not repo_root or not os.path.isdir(repo_root):
        return  # not a code project, so there is nothing verifiable to log

    idx = find_index_for_repo(repo_root)
    if not idx:
        return

    fm = read_frontmatter(idx)
    m = re.search(r"(\d{4}-\d{2}-\d{2})", fm.get("last_touched", "") or "")
    since = m.group(1) if m else "30 days ago"

    raw = run(["git", "-C", repo_root, "log", f"--since={since}",
               f"--max-count={MAX_COMMITS}", "--no-merges",
               "--date=short", "--format=%h\t%ad\t%s"])
    if not raw:
        return  # no evidence of work, so no stamp

    with open(idx, encoding="utf-8") as fh:
        body = fh.read()

    entries = []
    for line in raw.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3 and parts[0] not in body:  # dedupe on short hash
            entries.append(f"- `{parts[0]}` {parts[1]} {parts[2]}")
    if not entries:
        return

    today = datetime.date.today().isoformat()
    branch = run(["git", "-C", repo_root, "rev-parse", "--abbrev-ref", "HEAD"]) or "?"
    block = f"### {today} ({branch})\n" + "\n".join(entries)

    if LOG_HEADING in body:
        body = body.replace(LOG_HEADING, f"{LOG_HEADING}\n\n{block}", 1)
    else:
        body = body.rstrip() + f"\n\n{LOG_HEADING}\n\n{block}\n"

    if re.search(r"^last_touched:.*$", body, flags=re.M):
        body = re.sub(r"^last_touched:.*$", f"last_touched: {today}",
                      body, count=1, flags=re.M)

    tmp = idx + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(body)
    os.replace(tmp, idx)

    project = os.path.basename(os.path.dirname(idx))
    plural = "s" if len(entries) != 1 else ""
    print(json.dumps({
        "systemMessage": f"Vault updated: {project} "
                         f"({len(entries)} commit{plural} logged, last_touched → {today})"
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # a bookkeeping hook must never fail a session
    sys.exit(0)
