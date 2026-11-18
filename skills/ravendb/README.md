# `ravendb` — agent skill

RavenDB knowledge for coding agents: install a server, model documents, write client code (Node.js, .NET, Python), write RQL and indexes, use vector search and AI agents.

## Install

```bash
npx skills add ravendb/skills --skill ravendb
```

Or copy this directory into the agent's skills path — `~/.claude/skills/` or `.claude/skills/` (Claude Code), `~/.cursor/skills/` or `.agents/skills/` (Cursor).

## Shape

`SKILL.md` is a router, not a manual: the agent reads it, picks the ONE topic file its task needs, and opens only that. Nothing but the front-matter description is in context until a RavenDB task shows up.

The skill owns the workflow and safety rules, the traps (code that runs and returns the wrong rows), a verbatim minimal start per client language, and the routing. API reference lives in the docs: `rql-docs.md` and `client-docs.md` map each topic to its page on docs.ravendb.net, read as Markdown in the agent's client language.

```
SKILL.md                    router: language table, topic table, docs scheme, version/license gate
references/
  install.md                find a server first, docker, database, version + licensing
  install-native.md         download, extract, service, per-OS commands
  license.md                free key request form, activation call, verification
  windows.md                PowerShell probes, rvn windows-service, WSL2, firewall
  structure.md              store singleton, startup order, session per unit of work
  modeling.md               collections, ids, embed vs reference, metadata
  http-api.md               docs / queries / bulk_docs over raw HTTP
  ai-agents.md              agent configs + conversation endpoints
  testing.md                route choice, staleness flakes, what to test, CI
  diagnostics.md            wrong results, broken index, slow server, exceptions, logs
  samples.md                official sample apps and what each one showcases
  rql-cheatsheet.md         clause order and the SQL habits that return wrong rows
  rql-fulltext.md           full-text traps
  rql-timeseries.md         time series traps
  rql-docs.md               RQL docs pages by topic and server version
  client-docs.md            client API docs pages by topic and server version
  nodejs/ dotnet/ python/   client.md (minimal start, traps) · indexes.md · operations.md ·
                            testing.md · ai-agents.md
```

Version- and license-gated features carry an inline `(7.2.2+)` / `(license)` mark in the file that documents them, and the router requires three checks before using one: server version (`GET /build/version`), the client version pinned in the project, and `GET /license/status`.

## Maintaining it

Content is verified against the real client repos and a tri-language sample app, never written from recall: the same rule the skill imposes on its readers. Keep API reference out of the skill: when the docs cover a call, route to the page instead of restating it, because a restated API drifts from the docs and an agent reads a gap in the skill as proof the feature does not exist. Add a trap when code runs and silently does the wrong thing. A docs route goes in `rql-docs.md` or `client-docs.md`, and must answer 200 without a redirect on every version its row is for. Adding a topic file means adding a row to the router table in `SKILL.md`, otherwise the agent never finds it.
