# How the agent works this vault

`CLAUDE.md` holds the rules that must never lapse. `CONVENTIONS.md` holds the
schema. This file explains the operating model: who writes what, when, and which
parts you must not touch by hand.

It applies to any agent, not only Claude Code. If you are reading this because
something routed you here, read all of it before writing to the vault.

---

## 1. Three writers, three jobs

The vault has three things writing to it, and they must not do each other's work.

| Writer | Owns | Runs |
|---|---|---|
| **The hook** (`scripts/session-close.py`) | `last_touched`, the `## Session log` section | Automatically, when a session ends |
| **You**, during work | `## State`, `## Decisions`, `## Traps`, `## Open threads`, `## Next actions` | While doing the work, as part of finishing it |
| **`/vault-review`** | Corrections, challenges, reclassification | Weekly |

The split follows what each writer can actually know. The hook can see commits,
so it records commits. It cannot tell whether a change mattered, so it never
writes prose. You can tell what mattered, so you write the reasoning — and you
never write the mechanical log, because the hook already has it and will not
notice your version.

### What this means in practice

**Do not hand-write in `## Session log`.** The hook owns that section. It dedupes
on short commit hash, so anything you add by hand is invisible to it and will sit
alongside a duplicate the moment the hook next runs.

**Do not hand-stamp `last_touched`.** This is the important one. The hook only
moves that date when there are new commits, which is what makes the date
trustworthy. If you set it yourself, you break the single guarantee the field
carries: that a recent date means recent, verifiable work. A note that looks
maintained and isn't is worse than one that is visibly six months old, because
the visibly old one still tells the truth about itself.

The one exception is `/vault-setup` creating a note for the first time, where it
sets `last_touched` to the repository's last commit date. Not today — writing a
note about a project is not work on the project.

---

## 2. The session lifecycle

### When you start work in a repository

Read the project's `_index.md` before making architectural decisions. If the
repo's own `CLAUDE.md` names the vault note, that pointer is there precisely so
you find the context without being told.

Read the `## Decisions` and `## Traps` sections properly rather than skimming.
They exist because someone paid for that knowledge once already.

### While you work

When something genuinely changes, write it down as part of finishing the work,
not as a separate chore afterwards:

- A decision made, with the reasoning and the cost. Append it, dated.
- A trap discovered. Add it, stated so someone else could act on it.
- The situation shifting. Rewrite `## State` so it describes where things are now.

Do not write an entry for every session. Most sessions change nothing worth
recording, and the session log already captures that they happened. Volume is
what makes a vault unreliable, so the bar for adding prose is that a future
reader would act differently for having read it.

### When the session ends

Do nothing. The hook handles it.

If commits were made, the matching note gets them appended and its date moved
forward. If none were made, nothing is written at all, which is correct.

---

## 3. Reading discipline

**A note is a claim, not a fact.** It was true when written, on a date the note
tells you. Anything since then is unverified.

Before telling the user something is current, check it:

- Does the `repo:` path still exist, and is the branch still what the note says?
- Do the commits since `last_touched` contradict the `## State` paragraph?
- Does a recorded decision match what the code now does?

Where you cannot check, say the note is unverified rather than presenting it as
current. Confident staleness is the specific failure this vault is built to avoid,
and it is a failure you cause, not the vault.

**Prefer the repo for anything derivable.** If the question is what changed, when,
or in what order, read git. The vault answers a different question: why, and what
it cost. When the two disagree, the repo is right about facts and the note is
right about reasoning, and the disagreement itself is worth reporting.

---

## 4. Writing discipline

**Decisions are append-only.** Never edit or delete one. To reverse a decision,
add a new dated entry naming the one it supersedes and say what changed. The
sequence of what was believed, and when, is usually more valuable than the current
answer alone.

**Never invent.** An empty `## Traps` section is honest. A plausible-sounding trap
you inferred rather than observed will be read back as fact by every future
session, and nothing in the system will ever catch it. If you need a fact you do
not have, flag the gap.

**Dates are ISO and absolute.** Never "last week" or "recently".

**Never write a secret.** Record where a credential lives. Never its value.

**Ask before restructuring.** The frontmatter schema is what makes the vault
machine-readable. Changing a field name silently breaks every script in
`scripts/`. Ask before renaming fields, moving multiple files, or deleting notes.

---

## 5. Projects with no repository

A large share of most vaults is work that produces no code: client projects,
pitches, research, workshops. For those:

- The hook never fires, because there are no commits to find.
- `reconcile.py` lists them under **UNVERIFIABLE** rather than hiding them.
- Nothing automatic can tell whether they are current.

This is not a gap to engineer around. It is a fact about the work, and the
honest response is to make it visible: `/vault-review` raises every `active`
project with no update in 30 days and asks the user to confirm or reclassify.

For these projects, `last_touched` is yours to maintain, because there is no hook
to conflict with. Update it when you actually change the note's content.

---

## 6. When the hook misbehaves

**It didn't fire.** Check the hook is registered (`/hooks`), and that the session's
working directory was inside a git repository. It does nothing outside one, by
design.

**It logged to the wrong project.** It matches the `repo:` frontmatter path first
and falls back to comparing folder name against repository name. A vault folder
called `Client Portal` and a repo called `client-portal-web` will not match on
name. Fix it by adding the explicit `repo:` pointer, which is what that field is
for.

**It logged nothing despite commits.** Its window starts at the note's own
`last_touched`. If that date is in the future, or the commits are older than it,
it finds nothing. Correct the date and it will backfill on the next run.

**It logged a duplicate.** It dedupes on short commit hash against the whole note
body. A duplicate means the hash was rewritten, usually by a rebase or amend.
Remove the older entry by hand; that is the one case where editing the session log
is right.

Because it must never break a session, the hook fails silently. If you suspect it,
run it directly and watch:

```bash
echo '{"cwd":"'"$PWD"'"}' | AJJENT_VAULT=<vault> python3 <vault>/scripts/session-close.py
```

Output means it wrote. Silence means it decided not to, which is usually correct.
