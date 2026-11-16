# Ajjent Vault

A second brain your coding agent actually maintains.

Clone it, point Claude at it, and answer a few questions. You get a plain-Markdown
knowledge base that stays current on its own, because the agent writes to it as a
side effect of doing the work rather than because someone remembered to.

No Obsidian. No database. No app to open. Just folders and Markdown files that
`grep`, your editor, and any agent can all read.

```bash
git clone https://github.com/<you>/ajjent-vault my-vault
cd my-vault
claude
> /vault-setup
```

---

## Why this exists

Most "second brain" setups fail the same way. You capture diligently for three
weeks, the notes drift out of date, and then nobody trusts them — least of all the
agent, which reads a stale note and acts on it with total confidence.

Ajjent Vault is built around four rules that come from that failure.

### 1. Don't store what you can derive

Your repository already logs every detail perfectly. Git records what changed,
when, in what order, and the commit messages say why. It is self-verifying: the
code either matches the description or it doesn't.

Copying that into notes creates a second version of the truth that can silently
disagree with the first. So the vault stores only what has no other home:

- The approach you tried for two days and abandoned, and why you abandoned it.
- The client constraint that was said on a call and appears in no file.
- The trap that costs an hour every time someone forgets it.
- Where the account, the dashboard, or the deploy button actually is.

Everything else is a pointer to the repo.

### 2. More notes make recall worse, not better

A sparse vault fails by not answering. A dense one fails by answering *wrongly*,
because a superseded decision sits alongside the current one with nothing marking
which is which. The second failure is harder to see and far more expensive.

Decisions are therefore append-only and dated. Reversing one adds an entry that
supersedes the old; it never edits history.

### 3. Every claim carries a way to check it

Code stays honest because it runs. Notes don't run, so if nobody reads them,
nothing catches an error. The substitute is cheap: every project note carries a
repo path and a `last_touched` date, so the agent can verify a claim against
ground truth instead of believing it.

`scripts/reconcile.py` does exactly that comparison and reports where the notes
and the repos disagree.

### 4. Capture is easy; retrieval is the bottleneck

A perfectly maintained vault that nothing points at is inert. Agents read what
they are routed to, so the routing is part of the design:

- `CLAUDE.md` at the vault root sets a startup sequence.
- Each project note names its repo.
- `/vault-setup` writes a pointer back into each repo's own `CLAUDE.md`, so
  opening the code leads to the context, not just the other way round.

---

## What's in the box

```
CLAUDE.md               Boot config. Loaded automatically when Claude runs here.
AGENTS.md               The operating model: who writes what, and what not to touch.
CONVENTIONS.md          Frontmatter schema and note structure.
Projects/               One folder per project, each with an _index.md.
Reference/              Durable material that isn't project-scoped.
People/                 Who's who, and what they care about.
Decisions/              Cross-project decisions with dates and reasoning.
templates/              The shapes new notes are stamped from.
scripts/session-close.py  SessionEnd hook: logs real commits, stamps the date.
scripts/reconcile.py      Staleness check: notes versus repos.
scripts/install.sh        Registers the hook in your Claude settings.
```

---

## The automatic part

The thing that keeps this alive is `scripts/session-close.py`, wired as a
Claude Code `SessionEnd` hook by `/vault-setup`.

When a session in a project repo ends, it:

1. Finds the vault note whose `repo:` pointer matches that repository.
2. Reads the note's own `last_touched` date.
3. Asks git what has been committed since then.
4. Appends those commits to `log.md` beside the note and moves the note's date forward.

Two properties matter more than the mechanism.

**It only writes when there is evidence.** No new commits means no write at all.
Stamping a fresh date onto an unchanged note is how a stale vault comes to look
maintained, and that is the failure this whole design exists to prevent.

**It backfills.** Because it works from the note's own date rather than from when
the session started, any session that ended without the hook firing gets picked up
by the next one.

---

## The weekly part

`/vault-review` is a slash command, and it is best run on a schedule. It:

- Runs `reconcile.py` and reports notes whose repos have moved on without them.
- Lists every project marked `active` with no update in 30 days, and asks you to
  confirm or reclassify each one.
- Flags decisions that later work appears to contradict.

That second item is the one people skip, and it is the one that keeps `status`
meaningful. A status field that is never wrong is never useful.

---

## Using it without Claude Code

Nothing here depends on Claude Code except the hook and the two slash commands.
The vault is Markdown with YAML frontmatter in ordinary folders. Read it in any
editor, search it with `grep` or `rg`, and point any other agent at `CONVENTIONS.md`.
If you want the graph view, open the folder in Obsidian — it will work, because
`[[wikilinks]]` are just text.

## Licence

MIT.
