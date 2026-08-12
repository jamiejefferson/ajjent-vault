---
name: vault-setup
description: Set up or extend an Ajjent Vault. Interviews the user about their projects, creates project indexes from the template, writes pointers back into each repo's CLAUDE.md, and installs the SessionEnd hook. Use on first run after cloning, and again whenever projects are added.
---

# Vault setup

Configure this vault for its owner. Re-runnable: on later runs, skip what already
exists and only fill gaps.

Work through the phases in order. Do not batch every question at the start — ask
per phase, so answers to early questions shape later ones.

## Phase 1 — Find the projects, don't ask for them

Before asking anything, look. Guessing badly wastes the user's attention; arriving
with a list to confirm respects it.

1. Search the likely roots for git repositories: `~/code`, `~/src`, `~/projects`,
   `~/dev`, `~/Documents`, `~/work`, and the home directory at shallow depth.
   Skip `node_modules`, `Library`, `.Trash`, `venv`, `dist`, `build`.
2. For each, get the last commit date and the current branch.
3. Sort by recency. Anything untouched for over a year is probably not live work.

Then show what you found and ask which are current projects worth tracking. Offer
the recently-active ones as the default selection. Let the user name projects that
have no repository — client work, pitches and research are exactly the kind of
thing this vault is best at, and they will not appear in any search.

## Phase 2 — Build the project indexes

For each confirmed project, create `Projects/<Name>/_index.md` from
`templates/project-index.md`. Fill in what you can determine yourself:

- `project`, `created` (first commit date if there is a repo, else today)
- `repo` (absolute path), `live` (from README, deploy config, or by asking)
- `last_touched` — the last commit date, NOT today. Today would be a lie: you
  have not done any work on it, you have only written it down.
- `status` — ask. Do not assume `active` because the folder exists.

For the body, read the repo's README and recent commit messages, and write the
**State** paragraph from what you actually find. Leave **Decisions** and **Traps**
empty rather than inventing entries; a fabricated decision is worse than no
decision, because it will be read back as fact.

Ask the user directly for traps, in these words or similar: *"What's the thing
about this project that would cost someone an hour if nobody told them?"* That
question surfaces the genuinely non-derivable knowledge, which is the entire
reason this vault exists.

## Phase 3 — Wire the routing both ways

The vault pointing at repos is only half of it. An agent opening the code will
read that repo's `CLAUDE.md`, not this vault, so the pointer has to exist in both
directions or the context is never found.

For each project with a repo, add to that repo's `CLAUDE.md` (creating it if
absent, appending if present — never overwrite):

```markdown
## Project context

Decisions, traps and current state: `<vault>/Projects/<Name>/_index.md`
Read it before making architectural changes. Update it when the situation shifts.
```

Confirm before writing into repos you did not create. It is their file.

## Phase 4 — Install the hook

Run `./scripts/install.sh`. If it reports missing `jq`, say so and give the
install command rather than working around it.

If writing to the settings file is blocked by permissions, do not retry or seek
another route. Run `./scripts/install.sh --print`, show the user the JSON block,
and tell them where to paste it. Then tell them to open `/hooks` once, or restart,
so the change is picked up.

Explain in one sentence what they have just installed: when a session ends in one
of these repos, the matching project note gets its new commits appended and its
date moved forward, and nothing happens at all if there were no commits.

## Phase 5 — Prove it works

Run `python3 scripts/reconcile.py` and show the output. This is the moment the
user learns whether the setup describes reality, so do not skip it or summarise
it away.

Then offer the weekly review, which is what keeps the thing honest over time:

```
# macOS
0 8 * * 1  cd <vault> && claude -p "/vault-review" >> Reference/reviews/$(date +\%Y-\%m-\%d).md
```

Say plainly that this is optional and what it costs, which is one model call a week.

## Phase 6 — Report

Tell the user what now exists: how many project indexes, how many have repo
pointers and are therefore verifiable, how many do not, and whether the hook is
live or still needs pasting. Name anything you could not complete and why.

Do not claim the vault is "set up and working" if the hook is not actually
registered. Say which parts are live and which are pending.
