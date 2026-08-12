#!/usr/bin/env python3
"""
Reconcile project indexes against the repositories they describe. Read-only.

    python3 scripts/reconcile.py [--days N]

Reports four groups:

  STALE          The repo has commits newer than the note's last_touched.
  IN SYNC        The note is level with or ahead of the repo.
  UNVERIFIABLE   No repo pointer, so nothing can be checked automatically.
                 Normal for client and design work; shown with age so an
                 abandoned "active" project is still visible.
  NO DATE        A repo pointer but no last_touched to compare against.

Set AJJENT_VAULT to the vault root if it is not this script's parent directory.
"""
import argparse
import datetime
import glob
import os
import re
import subprocess

VAULT = os.environ.get(
    "AJJENT_VAULT",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
PROJECTS = os.path.join(VAULT, "Projects")
REPO_KEYS = ("repo", "repository", "path", "source", "code", "repo_path")


def read_frontmatter(path):
    fm, inside = {}, False
    try:
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
    except OSError:
        pass
    return fm


def parse_date(v):
    if not v:
        return None
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", v)
    if not m:
        return None
    try:
        return datetime.date(*(int(g) for g in m.groups()))
    except ValueError:
        return None


def last_commit(repo):
    try:
        r = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%cd", "--date=short"],
                           capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip():
            return parse_date(r.stdout.strip())
    except Exception:
        pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30,
                    help="flag unverifiable active projects older than this (default 30)")
    args = ap.parse_args()
    today = datetime.date.today()

    rows = []
    for idx in sorted(glob.glob(os.path.join(PROJECTS, "*", "_index.md"))):
        fm = read_frontmatter(idx)
        folder = os.path.basename(os.path.dirname(idx))
        touched = parse_date(fm.get("last_touched") or fm.get("updated"))
        repo = None
        for k in REPO_KEYS:
            v = fm.get(k)
            if v and ("/" in v or "~" in v):
                cand = os.path.expanduser(v.strip("`<>[] "))
                if os.path.isdir(os.path.join(cand, ".git")):
                    repo = cand
                    break
        commit = last_commit(repo) if repo else None
        rows.append(dict(folder=folder, status=fm.get("status", "?"),
                         touched=touched, repo=repo, commit=commit,
                         drift=(commit - touched).days if (commit and touched) else None))

    stale = sorted([r for r in rows if r["drift"] and r["drift"] > 0],
                   key=lambda r: -r["drift"])
    insync = [r for r in rows if r["drift"] is not None and r["drift"] <= 0]
    nodate = [r for r in rows if r["repo"] and not r["touched"]]
    unver = [r for r in rows if not r["repo"]]

    print(f"Project indexes examined: {len(rows)}\n")

    print(f"=== STALE — repo moved, note did not ({len(stale)}) ===")
    for r in stale:
        print(f"  {r['folder']:<28} {r['status']:<9} note {r['touched']}  "
              f"repo {r['commit']}  +{r['drift']}d")
    if not stale:
        print("  (none)")

    print(f"\n=== IN SYNC ({len(insync)}) ===")
    for r in insync:
        print(f"  {r['folder']:<28} {r['status']:<9} note {r['touched']}")

    if nodate:
        print(f"\n=== NO last_touched ({len(nodate)}) ===")
        for r in nodate:
            print(f"  {r['folder']:<28} {r['status']:<9} repo {r['commit']}")

    print(f"\n=== UNVERIFIABLE — no repo pointer ({len(unver)}) ===")
    for r in sorted(unver, key=lambda r: r["touched"] or datetime.date.min):
        age = (today - r["touched"]).days if r["touched"] else None
        flag = "  <-- confirm still active" if (
            r["status"] == "active" and age is not None and age > args.days) else ""
        print(f"  {r['folder']:<28} {r['status']:<9} "
              f"last_touched {r['touched']}" + (f"  ({age}d)" if age is not None else "")
              + flag)


if __name__ == "__main__":
    main()
