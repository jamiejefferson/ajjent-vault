# Vault conventions

Canonical IDEalize documentation ruleset ajjent-vault@9f7cfe9 (2026-08-12).

- One project, one folder under Projects/, anchored by its `_index.md`. A project folder without an index is invisible to tooling; the index is the contract.
- Folders: Decisions, People, Projects, Reference, templates. Decisions/ holds cross-project decisions (`YYYY-MM-DD-topic.md`); Reference/ holds durable material not scoped to one project; People/ holds who's who.
- `_index.md` frontmatter carries `project`, `status`, `type`, `created`, `last_touched` (plus optional `repo`, `live`, `tags`). The `repo:` pointer (absolute path to the working checkout) is what lets tools verify a claim instead of believing it.
- `status` is one of active | draft | parked | blocked | done | archived, and it must be allowed to be wrong — a vault where everything says active carries no information.
- Decisions are append-only and dated (`### YYYY-MM-DD — Title`). Reverse a decision by appending a new entry that names the one it supersedes; never edit history.
- Dates are absolute ISO (YYYY-MM-DD), never "yesterday" or "last week".
- The session log at the foot of a project note records commit evidence; IDEalize appends to it automatically when a session ends with commits. Do not write `last_touched` or `## Session log` by hand.
- Store what cannot be derived. Anything reconstructible from git, and any secret, stays out; record where a credential lives, never its value.
