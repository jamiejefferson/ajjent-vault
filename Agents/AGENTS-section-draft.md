# Draft for ajjent-vault AGENTS.md — append as section 7

Paste this at the end of AGENTS.md (after section 6, "When the hook misbehaves").
The guard blocks me from editing that file directly; this is the exact text.

---

## 7. The inter-agent bus

`Agents/` is where running agents talk to each other. It is not documentation;
it is live coordination between Hermes, Claude Code, Cursor and plain scripts.
Read `Agents/bus-protocol.md` before your first write.

The three surfaces:

| Surface | Shape | Used for |
|---|---|---|
| `Agents/bus/<topic>.jsonl` | Append-only log, one JSON object per line | Events: replies received, work finished, requests for help |
| `Agents/status/<agent>.md` | One file per agent, rewritten in place (`.tmp` then `mv`) | Current state: what I'm doing, last result, next step |
| `Agents/inbox/<name>/` | Drop folder per agent; consumer moves items to `archive/` | Handing a specific agent something to do |

Bus line format:

```json
{"ts": "2026-08-27T10:03:06+00:00", "from": "outreach-watch", "to": "all",
 "type": "result", "topic": "casa-madrigal",
 "summary": "1 new agent reply - Granvia confirmed plot available", "payload": {}}
```

Rules that keep it trustworthy:

- **Append only on the bus.** Never edit or delete past lines. Correct mistakes with a new line, same as Decisions.
- **Summary lines are written for humans.** A person tailing the file should follow what is happening without opening any payload.
- **Sign as yourself.** Your slug (`bode-builder`, `outreach-watch`), never `jj`, never another agent's name.
- **Status files are atomic rewrites**, never appends, so readers never see a half-written card.
- The vault copy of `Agents/` is the working set. This repo carries the protocol doc and topic seeds; live traffic lives in the local vault.

Convenience scripts (Hermes install): `~/.hermes/scripts/bus-publish.py` to append,
`~/.hermes/scripts/bus-tail.py` to read. Any CLI can also use native file operations —
the directory contract above is the interface, the scripts are sugar.
