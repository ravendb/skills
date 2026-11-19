# RavenDB indexes from .NET: traps

Index traps for the .NET client. Defining, deploying and querying indexes: `../client-docs.md`.

## Traps

- **Query a static index by its `/` name**: class `Deals_ByClientName` deploys as `Deals/ByClientName`, and the `_` spelling names no index. Use `session.Query<Deal, Deals_ByClientName>()` or `session.Query<Deal>("Deals/ByClientName")`.
- **The map expression is translated and shipped to the server**, so it must be self-contained: no closure captures, no local method calls.
- **A computed field (`Total = Sum(...)`) reads back only with `Store(x => x.Total, FieldStorage.Yes)` and an explicit `.Select(x => new Result {...})` or `.ProjectInto<Result>()`.** A bare `Query<TResult, TIndex>()` loads the source document and binds `TResult` by name, so `Total` is `0`/`null` on every row while filtering and sorting on it work. Map-reduce indexes are exempt.
- **A stored value is a string on the wire** (`"2479.0"`): a typed `decimal`/`int` property converts it, an `object`, `dynamic` or `string` target keeps the string. Give computed fields their real numeric type.
- **`Search()` needs the field indexed as `FieldIndexing.Search`**, and only fields the map emits are queryable. What `=` and `Search()` then match: `../rql-cheatsheet.md`.
- **Vector fields need the Corax search engine** (Lucene lacks them): set `SearchEngineType = SearchEngineType.Corax` in the index constructor, per index.
- **Multi-map indexes drop vector fields silently** `(client 7.2.0)`: `AbstractMultiMapIndexCreationTask<T>` does not copy `VectorIndexesStrings` into the `IndexDefinition`. Override `CreateIndexDefinition()` and copy each entry into `def.Fields[key].Vector`.

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
