# RavenDB agent skills

Skills that teach coding agents to work with [RavenDB](https://ravendb.net) — install a server, model documents, write client code in Node.js / .NET / Python, write RQL and indexes, use vector search and AI agents.

## Install

```bash
npx skills add ravendb/skills                 # every agent that reads SKILL.md
npx skills add ravendb/skills --skill ravendb  # one skill by name
```

Without the CLI, copy the skill directory into the agent's skills path:

```bash
git clone --depth 1 https://github.com/ravendb/skills
cp -r skills/skills/ravendb ~/.claude/skills/      # or .claude/skills/ for one project
```

Per-agent paths: `~/.claude/skills/` (Claude Code), `~/.cursor/skills/` or `.agents/skills/` (Cursor), `.github/skills/` (Copilot). The CLI knows all of them.

## Skills

| Skill | What it covers |
|---|---|
| [`ravendb`](skills/ravendb) | Server install, document modeling, client libraries (Node.js / .NET / Python), RQL, indexes, vector search, AI agents |

## How they are written

Each skill is a router, not a manual. `SKILL.md` holds only the front-matter description plus tables that route a task to the ONE reference file it needs; everything else stays out of context until something asks for it. An agent working in C# never loads the JavaScript files.

Content is verified against the RavenDB client repos and running servers, never written from recall — the rule the skills impose on their readers. Server baseline is **6.2+**; version- and license-gated features carry an inline `(7.0+)` / `(license)` mark in the file that documents them.

## Contributing

Fix the file that owns the fact: a client API change goes in `skills/ravendb/references/<language>/`, an RQL change in the matching `rql-*.md`. A new topic file also needs a row in the router table in `SKILL.md`, or no agent will ever find it.
