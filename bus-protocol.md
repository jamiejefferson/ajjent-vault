# Agents/ — Inter-Agent Bus Protocol

How CLIs (Hermes, Claude Code, Cursor, bash scripts) coordinate through this vault.

## Layout

```
Agents/
  bus/        <topic>.jsonl     — append-only conversation, newest line = latest
  status/     <agent>.md        — one file per agent, rewritten atomically
  inbox/      <name>/           — drop files here to hand work to a name
  archive/                      — consumed/acknowledged items move here
```

## Bus line format (one JSON object per line)

```json
{
  "ts": "2026-08-19T16:20:00+01:00",
  "from": "outreach-watch",
  "to": "all | jj | bode-lead",
  "type": "status | request | response | alert | result",
  "topic": "casa-madrigal",
  "summary": "One readable line, no more than ~120 chars",
  "payload": { }
}
```

Rules:
- **Append only.** Never edit past lines. Readers tail from their last-seen offset or timestamp.
- **`from`** is the agent's short, stable slug (`outreach-watch`, `bode-builder`, `casa-madrigal-poller`, `mother-daughter-replies`). Spaces not allowed.
- **`summary` must be human.** A reader skimming the .jsonl should understand what happened without parsing payload. Payload is for structured detail; summary is for people.
- **Topics are files.** Casa Madrigal events go in `bus/casa-madrigal.jsonl`, Bode work in `bus/bode.jsonl`, Mother/daughter in `bus/mother-daughter.jsonl`. Create new topic files freely.

## Status files (status/<agent>.md)

Frontmatter:
```yaml
---
agent: outreach-watch
state: ok | stale | blocked | done
updated: 2026-08-19T16:20:00+01:00
---
```

Body: 5–15 lines max — what the agent is doing, last result, next milestone. Status files are **rewritten** (not appended). Write to `<agent>.md.tmp` then `mv` so readers never see partial writes.

## Inbox

`inbox/<name>/` holds unsolicited or delegated work. Producers drop any file; consumers move it to `archive/` once picked up (or reply with a `response` on the bus). `inbox/jj/` is JJ's general to-drop area.

## Reading and writing

Write: `python ~/.hermes/scripts/bus-publish.py casa-madrigal status "Cleared backlog"` (details via `--payload '{}'`).
Read: `python ~/.hermes/scripts/bus-tail.py casa-madrigal` (plain), or `--json` for full lines.

Any CLI can use the same protocol with native file ops — these scripts are conveniences, not a gate. The protocol is the contract.

## Anti-patterns

- **Do not** write `from: jj` unless JJ personally wrote it. Agents sign for agents; humans sign for humans.
- **Do not** delete old lines except via the archive move. History is the point.
- **Do not** treat bus POLEN as a queue — it's a log. If you need ack semantics, write a `response` line back referencing the request's ts.
