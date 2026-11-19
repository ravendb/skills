# RavenDB indexes from Node.js: traps

Index traps for the Node.js client. Defining, deploying and querying indexes: `../client-docs.md`.

## Traps

- **Query a static index by its `/` name**: class `Deals_ByClientName` deploys as `Deals/ByClientName`, and the `_` spelling names no index. Use `session.query({ indexName: "Deals/ByClientName" })` or `session.query({ index: Deals_ByClientName })`.
- **The map function is stringified and shipped to the server**, so it must be self-contained: no closure captures.
- **A computed field reads back only when stored and projected.** Projecting it with `.selectFields([...])` returns `null` on every row, silently, until the index has `this.store("total", "Yes")`, though filtering and sorting on it work. Map-reduce indexes are exempt.
- **A stored numeric field reads back as a string** (`"650"`), so `"650" + 10 === "65010"`: wrap it in `Number(...)`. Map-reduce results keep their numeric type.
- **`search()` needs the field indexed as `this.index(field, "Search")`**, and only fields the map emits are queryable. What `=` and `search()` then match: `../rql-cheatsheet.md`.
- **Vector fields need the Corax search engine** (Lucene lacks them); the SDK sets `searchEngineType = "Corax"` itself for an index with a vector field.

## Map-reduce in JavaScript syntax

Map and reduce can also be written in JavaScript rather than as C#-syntax strings:

```js
const { AbstractJavaScriptIndexCreationTask } = require("ravendb");

class Deals_CountByStatus extends AbstractJavaScriptIndexCreationTask {
    constructor() {
        super();
        this.map("Deals", d => ({ status: d.status, count: 1, total: d.value }));
        this.reduce(r => r.groupBy(x => x.status).aggregate(g => ({
            status: g.key,
            count: g.values.reduce((c, v) => c + v.count, 0),
            total: g.values.reduce((t, v) => t + v.total, 0)
        })));
    }
}
```

Map output and reduce output must have the same shape. Query rows are `{ status, count, total }` aggregates, not documents.

## Docs

| You need | `../client-docs.md` topic |
|---|---|
| Auto vs static, when a static index is worth it | What indexes are: auto vs static |
| A JavaScript index (`AbstractJavaScriptIndexCreationTask`), deploying it (`store.executeIndex`, `IndexCreation.createIndexes`) | Defining and deploying a static index |
| Field options: `this.index`, `this.store`, `this.analyze` | Map indexes; Storing fields in the index; Analyzers, full-text fields |
| Several collections in one index | Multi-map indexes |
| Map-reduce in C#-syntax strings, `outputReduceToCollection` | Map-reduce indexes |
| `load()` from `this.mapUtils()` | Indexing related documents: `LoadDocument` |
| Querying a static index | Querying a static index |
| Vector fields: `createVector`, `vectorField`, `vectorSearch` with `withField` | Vector search on a static index |
| Waiting for non-stale results per query | Customizing a query: wait for non-stale results, no caching; Stale indexes |
| Polling index statistics | Index statistics, polling for non-stale |

The query side of full-text and vector search: `../rql-docs.md` (Full-text search; Vector search).
