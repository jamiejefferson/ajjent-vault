# CLAUDE.md — Ajjent Vault boot config

Auto-loaded when Claude Code runs from this vault root. Kept short so it survives
context compaction. Two companions hold the detail:

- `AGENTS.md` — the operating model. Who writes what, and which sections are
  maintained automatically and must not be written by hand. Read it before your
  first write to this vault.
- `CONVENTIONS.md` — the frontmatter schema and note structure.

This vault holds reasoning, decisions and project state. It is deliberately NOT a
copy of anything a repository, a ticket tracker, or a company's own system already
records.

## Startup sequence

1. Read `AGENTS.md`, then `CONVENTIONS.md`.
2. Scan `Projects/*/_index.md` frontmatter for anything marked `status: active`.
3. If the user names a project, read its `Projects/<name>/_index.md` before acting.

Re-read both after any context compaction.

## Do not write these by hand

`last_touched` and the `## Session log` section are maintained by the SessionEnd
hook, which only writes when there are new commits. Stamping either yourself
destroys the one guarantee they carry — that a recent date means recent,
verifiable work. `AGENTS.md` section 1 explains the division of labour in full.

## Rules that can't lapse

- **Store what cannot be derived.** If git, the code, or an external system already
  records it, write a pointer instead of a copy. Two copies of a fact will
  eventually disagree, and nothing will tell you which one is wrong.

- **Verify before asserting.** A note is a claim, not a fact. Before telling the
  user something is current, check it against the repo, the file, or the live
  service. If you cannot check it, say so rather than presenting the note as truth.

- **Decisions are append-only.** Never edit or delete a past decision. To reverse
  one, add a new dated entry that supersedes it and say why. The reasoning behind
  a reversal is usually worth more than the reversal.

- **Date everything, in ISO format, absolute.** Never write "last week" or
  "recently" — the note will outlive the context that made it legible.

- **When a project's situation changes, persist it without being asked.** Update
  the project `_index.md` as part of finishing the work, not as a separate chore
  the user has to request.

- **Ask before deleting or moving more than one file, and before changing the
  frontmatter schema.** The schema is what makes the vault machine-readable; a
  silent change breaks every script that reads it.

- **Don't fabricate.** If a note needs a number, a date, or a name you don't have,
  flag the gap. A confident invention in a vault outlives the conversation that
  produced it and gets read back as fact.

## Commands

- `/vault-setup` — first-run configuration, and re-runnable to add projects.
- `/vault-review` — the weekly pass: reconcile, challenge stale statuses, report.

## What this vault is not for

- Copies of records that live in a company's own system. Reference them by name.
- Generated output, build artefacts, or anything reproducible from source.
- Secrets. Record where a credential lives, never the credential itself.
