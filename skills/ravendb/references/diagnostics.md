# Diagnosing a RavenDB problem

Symptom → what to read. Endpoints are `GET` on the server URL unless marked; `{db}` is the database name; the rest are in `client-docs.md` (HTTP endpoints). Fixes that change state (patch, delete, redeploy, kill a query, raise the log level) are writes (`SKILL.md`).

## "The query returns nothing / the wrong rows"

| Question | Check |
|---|---|
| Which index served it, and why that one? | `GET /databases/{db}/queries?query=<rql>&debug=explain`: the candidate indexes, with why each was picked or rejected. **Dynamic queries only**: on `from index 'X'` it throws `InvalidOperationException: Explain can only work on dynamic indexes` |
| What did the index store for these documents? | `GET /databases/{db}/queries?query=<rql>&debug=entries`: the raw index entries, not the documents. **Drop the `where` first**: entries are filtered by the same predicate, so the query that returns nothing returns no entries either. A field missing from the unfiltered entries was never indexed |
| Which terms exist for a field? | `GET /databases/{db}/indexes/terms?name=<index>&field=<field>`: the answer to most "why doesn't `where` match" on an analyzed field |
| Where did the time go? | `include timings()`: `rql-docs.md` (Query timings: `include timings()`) |
| Is the result stale? | `IsStale` and `IndexTimestamp` on every query response; `GET /databases/{db}/indexes/staleness?name=<index>` asks directly |

Most empty results are field-name case or `=` against an analyzed field (`rql-cheatsheet.md`); `debug=entries` tells which. A predicate that matches as a dynamic query and returns nothing on a static index is usually the same trap: the auto-index stores the field exact, the static index analyzes it, so use `search()` there. `indexes/terms` on each index shows which is which.

## "The index is broken / never finishes"

| Check | Endpoint |
|---|---|
| Errors per index (map/reduce exceptions, with document ids) | `GET /databases/{db}/indexes/errors` |
| State, priority, indexed/errored counts, last indexing time | `GET /databases/{db}/indexes/stats` |
| How far behind, and on which collection | `GET /databases/{db}/indexes/progress` |
| Per-batch timings: which stage is slow | `GET /databases/{db}/indexes/performance` (`/performance/live` streams) |
| The definition the server has | `GET /databases/{db}/indexes?name=<index>`, or `/indexes/source` for the compiled source |
| Did my deploy change anything? | `POST /databases/{db}/indexes/has-changed` with the definition; if not, the deploy is not the problem |

`ErrorsCount` and `State` are separate: a map that throws on a few documents leaves the index `Normal`, indexing everything else. It turns `Error` only when the map failure rate passes **15%** over at least 6 attempts, or every attempt so far has failed, so a few poison documents in a large collection show as a rising `ErrorsCount`, never a state change. Check both. An index in `Error` stops indexing entirely: fix the map and redeploy, which rebuilds side-by-side. A poison document repeats the same id in the errors: patch or delete it. Too many auto indexes: `GET /databases/{db}/indexes/suggest-index-merge` proposes merging near-duplicates.

## "It's slow" / "it stopped responding"

| Check | Endpoint |
|---|---|
| Queries running now, with their RQL and duration | `GET /databases/{db}/debug/queries/running`; kill one with `POST /databases/{db}/debug/queries/kill?id=<id>` (the id from that listing) |
| Database counts, index count, size on disk | `GET /databases/{db}/stats` (`/stats/essential` is cheaper, `/stats/detailed` adds identity and compare-exchange counts). Per-collection counts and sizes: `GET /databases/{db}/collections/stats/detailed` |
| Disk I/O over time | `GET /databases/{db}/debug/io-metrics` |
| Storage layout and space per tree | `GET /databases/{db}/debug/storage/report` |
| Oversized documents | `GET /databases/{db}/debug/documents/huge`: documents over `PerformanceHints.Documents.HugeDocumentSizeInMb` (default 5 MB), but only those *read* since the server started, so it is empty on a fresh process. The threshold is the **stored** size, far below the JSON you sent for repetitive text: check one document with `GET /databases/{db}/docs/size?id=<id>` (`ActualSize`) before concluding the endpoint is broken |
| Everything, for a support ticket | `GET /databases/{db}/debug/info-package`: a zip of the whole diagnostic set; attach it rather than pasting fragments |

Cluster health: `GET /cluster/topology` and `GET /admin/cluster/log`. A `Passive` node or a cluster with no leader fails writes while reads keep working.

## Exceptions and what they mean

| Exception | Meaning | Response |
|---|---|---|
| `ConcurrencyException` | change-vector mismatch under optimistic concurrency, or a duplicate id on `store` | reload and retry, or drop optimistic concurrency for that path |
| `ClusterTransactionConcurrencyException` | compare-exchange index moved under a cluster-wide transaction | retry the whole transaction: the expected outcome of a lost race |
| `DocumentDoesNotExistException` | a patch or attachment operation targeted a missing document (`Load` returns `null` instead) | check the id shape: `clients/1-A`, not `clients/1` |
| `IndexDoesNotExistException` | the query names an index that was never deployed | deploy indexes at startup (`structure.md`) |
| `InvalidQueryException` | the server rejects the RQL | the message names the clause; `rql-cheatsheet.md` |
| `DatabaseDoesNotExistException` | the store's `Database` does not exist on that server | create it explicitly; do not assume the server auto-creates it |
| `AllTopologyNodesDownException` | no node reachable: wrong URL or port, server down, or TLS refused | probe the URL as in `install.md`; with a certificate the scheme is `https` |
| `AuthorizationException` / 403 | the certificate is valid but not authorized for that database | check the certificate's database permissions |
| `LicenseLimitException` | the feature or resource is beyond the license | `version-gate.md` |
| `IndexCompilationException` | the index definition does not compile server-side | the message carries the compiler error |
| `NotSupportedInCoraxException` | the index uses a Lucene-only capability | rewrite it, or pin that index to Lucene |
| `RavenTimeoutException` | the server did not answer within the configured timeout | usually a slow query or a stale-wait, not a network fault |
| `BulkInsertAbortedException` | the server ended the bulk-insert stream | the real error is the inner exception |

Per language: .NET throws classes under `Raven.Client.Exceptions`, all deriving from `RavenException`. Python raises them from `ravendb.exceptions.exceptions`, and spells the missing-document one `DocumentDoesNotExistsException`. **Node.js has no exception classes**: every failure is a plain `Error` whose `name` is the string above, so branch on `err.name === "ConcurrencyException"`; `instanceof` cannot work.

## Server-side logs

Logs go to `Logs.Path` (Docker image: `/var/log/ravendb/logs`). Raise verbosity without a restart:

```bash
curl -s -X POST '<server>/admin/logs/configuration' \
  -H 'Content-Type: application/json' -d '{"Logs":{"MinLevel":"Debug"},"Persist":false}'
```

Lower it afterwards: debug logging is expensive. `Persist: true` survives a restart. `GET /admin/logs/configuration` reads the setting, `GET /admin/logs/watch` is a websocket tail, `GET /admin/logs/download` a zip. Settings: `client-docs.md` (Logging configuration). Startup failures (port in use, bad certificate, unaccepted EULA) appear only in stdout or `docker logs <container>`, never in the HTTP API: the server never got far enough to serve it.
