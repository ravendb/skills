# Official sample code: what to read for what

A sample shows a feature **wired into an application**: layout, startup, background tasks. Take syntax from this skill and the docs, not from a sample, and the version from `version-gate.md`: a sample's pinned client version says nothing about what is current. All are public `github.com/ravendb/…` repos; `ravendb/docs` → `samples/` holds the maintained gallery page for each.

## Full applications, by the feature you care about

| Repo | Stack | Showcases |
|---|---|---|
| `samples-library` | .NET + Aspire, Svelte | The clearest starting point. `include` for related documents in one request, document **refresh** as a timeout mechanism, Azure Queue **ETL** driven off `@refresh`, **vector search** over similar books |
| `samples-hr` | .NET + Aspire, React | **AI agents** with tool calling and conversation management, **vector search** via `vector.search(embedding.text(...))`, **time series** for rate limiting, attachments for signature images, counters for token accounting, expiration for session cleanup |
| `samples-fit` | .NET + Aspire, React | The densest: a parent **AI agent with four sub-agents** plus streaming, **GenAI tasks** producing structured output deduped via `@ai-hashes`, **time series with rollups** (raw/hourly/daily/monthly, query picks the tier), **subscriptions** fanning events to followers, RabbitMQ **Queue ETL**, **OLAP ETL** to Parquet, **Changes API** for a push-driven ticker |
| `samples-verity` | .NET + Aspire, Svelte | Document lifecycle: **GenAI tasks** over documents larger than the model's context window, **AI agents**, **remote attachments** in Azure/S3, **revisions** as an audit trail, **archival** and **expiration**, hub/sink replication, subscriptions driving a live CLI |
| `samples-brain-slop` | .NET + Aspire, Next.js | Small **AI agent** app: free-form text interpreted into actions, GenAI for chat titles |
| `samples-properties` | ASP.NET Core, React, Telegram bot | The only app with **spatial indexing**, a **GenAI ETL** turning an uploaded photo into a maintenance description, **AI agents** reached through a Telegram bot, **subscriptions** for push notifications, time series for utility usage |
| `samples-crypto-app` | .NET + Node.js Azure Functions, TS frontend | **Time series** end to end, the *same* ingestion in the .NET and Node.js clients: the best side-by-side of the two APIs. Database exports in the repo |

There is **no Python sample application**: take structure from `samples-library` and API usage from the Python client's tests.

## Node.js / TypeScript

| Repo | What it gives you |
|---|---|
| `samples-nextjs`, `samples-sveltekit` | The smallest Node client in a framework: one store module (`src/db/store.ts` / `src/lib/store.ts`) plus CRUD and query routes. Both point at `live-test.ravendb.net` by default |
| `template-cloudflare-worker` | `npm init cloudflare my-project https://github.com/ravendb/template-cloudflare-worker`. Read it before writing Worker/edge code: the runtime has no Node `https` agent, so client-certificate auth uses a Cloudflare mTLS binding, not `authOptions` |

## Client repos: executable API examples

| Where | Why |
|---|---|
| `ravendb-nodejs-client` → `README.md` | Effectively the Node client manual, a worked example per area |
| `ravendb-nodejs-client` → `test/` | Grouped by area (`Documents/`, `ServerWide/`, `Issues/`); the tests are executable proof of a signature |
| `ravendb-python-client` → `ravendb/tests/` | The **only** Python examples of the AI surface: `ai_agent_tests/`, `gen_ai_tests/`, `embeddings_generation_tests/`. Also `session_tests/`, `operations_tests/` |
| `ravendb/ravendb` → `test/` | The server's own test suite: the last word on behavior when a sample and the docs disagree |

## Learning material and playgrounds

| Resource | Use it for |
|---|---|
| demo.ravendb.net (source: `ravendb/demo`) | Runnable per-feature demos against your own database, each with a code walkthrough. Several languages, Northwind data |
| live-test.ravendb.net | A free shared server: no install, create a database and go. **Public and periodically wiped**: never put real or private data there |
| `ravendb/bootcamp` | Four self-directed .NET units on Northwind. Old API: the concepts hold, the API details do not |
| `ravendb/book` | Source of *Inside RavenDB*: **why** the engine behaves as it does (storage, clustering, indexing internals). Old API, like the bootcamp |
| `ravendb/awesome-ravendb` | Community integrations: DI, health checks, Serilog sinks, ASP.NET Identity |
| `samples-hugin` | RavenDB on **ARM / a Raspberry Pi**, serving full-text search over Stack Exchange dumps offline: embedded or constrained deployments, a large full-text dataset. Node client |
| `samples-jvm`, `samples-php-laravel` | Only for Java or PHP |
