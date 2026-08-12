---
name: vault-review
description: The weekly vault pass. Reconciles project notes against their repos, challenges stale active statuses, checks for superseded decisions, and reports what needs a human answer. Run it on a schedule or on demand.
---

# Vault review

A vault nobody reads is a vault nobody corrects. This is the pass that catches
what would otherwise rot silently. Run it weekly.

Fix mechanically what is unambiguous. Bring the user only what needs judgement,
and bring it as a specific question rather than a list of concerns.

## 1. Reconcile against the repos

Run `python3 scripts/reconcile.py`.

For each **STALE** project, read the commits the note has missed and update its
**State** paragraph so it describes where the project actually is. This is a
content fix, not a date fix. Moving the date without changing the body produces a
note that looks maintained and isn't, which is the exact failure mode this vault
is designed against.

## 2. Challenge the statuses

For every `active` project with no update in 30 days, ask the user directly
whether it is still active. Show the age and the last thing that happened.

Ask about all of them in one question with multiple selections rather than one at
a time. Never reclassify on the user's behalf: an unanswered question is more
useful than a wrong answer written into the file, because the wrong answer stops
anyone asking again.

This step is the one people skip, and it is the one that keeps `status` meaningful.
A field that is never wrong carries no information.

## 3. Look for contradicted decisions

For each project with recent commits, compare the **Decisions** entries against
what the code now does. Where a commit appears to reverse a recorded decision,
raise it: *"`2026-03-04` says db:push over migrations, but there's a `migrations/`
directory as of last week. Superseded?"*

If confirmed, append a new dated decision naming the one it supersedes. Never edit
the original — being wrong on a given date, and knowing why you believed it, is
the part worth keeping.

## 4. Check the pointers still resolve

- Every `repo:` path exists and is still a git repository.
- Every `live:` URL still responds.
- Every `[[wikilink]]` resolves to a note that exists.

Repair broken paths where the target has obviously moved. Ask when the answer is
not obvious — a confidently repointed link to the wrong repo is worse than a
broken one, because it looks fine.

## 5. Report

Write a short report. Lead with what needs the user, not with what you fixed.

```markdown
# Vault review — YYYY-MM-DD

## Needs you
- acme-rebrand: 83 days since any update, still marked active. Still live?
- billing-service: commits suggest the db:push decision was reversed. Confirm?

## Fixed
- Updated State on internal-tools (23 days of commits were missing)
- Repointed client-portal repo path to client-portal-web

## Unverifiable
24 of 40 projects have no repo pointer, so nothing here could be checked
automatically. Oldest: pitch-northbank (121 days).
```

Keep the "Needs you" section short enough to act on in one sitting. A review that
raises twenty items gets skipped entirely, and then nothing gets corrected at all.
