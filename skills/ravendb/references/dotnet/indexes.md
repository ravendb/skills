# RavenDB indexes from .NET: traps

This file holds the traps. Defining, deploying, map-reduce, related documents, analyzers, vector fields and the staleness API are in the docs via `../client-docs.md`: read the plain `.md` copy, which is C#, for the server's version. A feature this file does not show still exists: check the docs page for your server version before saying it does not.

## Traps

- **Query a static index by its `/` name.** The index name is the class name with `_` turned into `/`: class `Deals_ByClientName` deploys as `Deals/ByClientName`. Use `session.Query<Deal, Deals_ByClientName>()`, or by name `session.Query<Deal>("Deals/ByClientName")`; the `_` spelling names an index that does not exist.
- **The map expression is translated and shipped to the server**, so it must be self-contained: no closure captures, no local method calls.
- **Reading a computed field takes two things: store it, and project it.** A field the map computes (`Total = Sum(...)`) does not exist on the source document, and a bare `Query<TResult, TIndex>()` **loads the document** and binds `TResult` by name, so `Total` comes back `0`/`null` for every row. Add `Store(x => x.Total, FieldStorage.Yes)` in the index *and* an explicit `.Select(x => new Result {...})` or `.ProjectInto<Result>()`, which is what makes the server answer from stored index fields. Filtering and sorting on the computed field work either way, which is why this reads as a client bug rather than a missing projection. Map-reduce indexes are exempt: reduce results always come from the index, stored or not.
- **A stored value is a string on the wire** (`"2479.0"`). A typed `decimal`/`int` property converts it silently, so this only bites when the projection target is `object`, `dynamic`, or a `string` property that then fails to parse. Give computed fields their real numeric type.
- **`=` and `Search()` disagree on analyzed fields.** Only fields emitted by the map are queryable. `Search()` on a field needs `FieldIndexing.Search` on it, and equality on a Search field matches analyzed terms, not the exact string. RQL side: `../rql-cheatsheet.md`, `../rql-fulltext.md`.
- **Vector fields need the Corax search engine**; Lucene does not support them. Set `SearchEngineType = SearchEngineType.Corax` in the index constructor; it applies to that index only.
- **Multi-map indexes drop vector fields silently** `(client 7.2.0)`: `AbstractMultiMapIndexCreationTask<T>` does not copy `VectorIndexesStrings` into the `IndexDefinition`, so the index deploys without its vector configuration. Override `CreateIndexDefinition()` and copy each entry into `def.Fields[key].Vector`.
- **A query right after `SaveChanges()` can return pre-write results.** Indexes update asynchronously and the response is marked stale (`stats.IsStale`), not delayed. Tests and seed scripts that write and then query must wait: `WaitForIndexing(store)` from the test driver (`testing.md`), or `.Customize(x => x.WaitForNonStaleResults(...))` on the query. Never wait on hot production paths: it trades latency for consistency, so design UIs to tolerate slightly stale results instead.

## Docs

| You need | `../client-docs.md` topic |
|---|---|
| Auto vs static, when a static index is worth it | What indexes are: auto vs static |
| `AbstractIndexCreationTask<T>`, deploying it (`store.ExecuteIndexAsync`, `IndexCreation.CreateIndexesAsync`) | Defining and deploying a static index |
| Field options: `Index`, `Store`, `Analyze` | Map indexes; Storing fields in the index; Analyzers, full-text fields |
| Several collections in one index: `AbstractMultiMapIndexCreationTask`, `AddMap` | Multi-map indexes |
| Map-reduce, `OutputReduceToCollection` | Map-reduce indexes |
| `LoadDocument<T>` in a map | Indexing related documents: `LoadDocument` |
| Querying a static index | Querying a static index |
| Vector fields: `CreateVector`, `Vector(...)`, `VectorSearch` with `WithField` | Vector search on a static index |
| Waiting for non-stale results per query | Customizing a query: wait for non-stale results, no caching; Stale indexes |
| Polling index statistics without the test driver | Index statistics, polling for non-stale |

The query side of full-text and vector search: `../rql-docs.md` (Full-text search; Vector search).
