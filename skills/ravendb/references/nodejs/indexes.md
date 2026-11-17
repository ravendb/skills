# RavenDB indexes from Node.js: traps

This file holds the traps. Defining, deploying, map-reduce, related documents, analyzers, vector fields and the staleness API are in the docs via `../client-docs.md`: read the `.nodejs.md` copy for the server's version. A feature this file does not show still exists: check the docs page for your server version before saying it does not.

## Traps

- **Query a static index by its `/` name.** The index name is the class name with `_` turned into `/`: class `Deals_ByClientName` deploys as `Deals/ByClientName`. Use `session.query({ indexName: "Deals/ByClientName" })` or pass the class, `session.query({ index: Deals_ByClientName })`; the `_` spelling names an index that does not exist.
- **The map function is stringified and shipped to the server**, so it must be self-contained: no closure captures.
- **Reading a computed field takes two things: store it, and project it.** A field the map computes does not exist on the source document, so `this.store("total", "Yes")` plus an explicit `.selectFields([...])` is what makes the server answer from the index; without the store the projection is `null` on every row, silently. Filtering and sorting on the computed field work either way, which is why this reads as a client bug rather than a missing store. Map-reduce indexes are exempt: reduce results always come from the index, stored or not.
- **A stored numeric field comes back from the index as a string** (`"650"`, not `650`): the store keeps the indexed term, not the JSON type. It prints identically, so the bug surfaces later as `"650" + 10 === "65010"`; wrap it in `Number(...)` before any arithmetic or comparison. Map-reduce results keep their numeric type.
- **`=` and `search()` disagree on analyzed fields.** Only fields emitted by the map are queryable. `search()` on a field needs `this.index(field, "Search")` on it, and equality on a Search field matches analyzed terms, not the exact string. RQL side: `../rql-cheatsheet.md`, `../rql-fulltext.md`.
- **Vector fields need the Corax search engine**; Lucene does not support them. The SDK sets `searchEngineType = "Corax"` itself when the index has a vector field.
- **A query right after `saveChanges()` can return pre-write results.** Indexes update asynchronously and the response is marked stale, not delayed. Tests and seed scripts that write and then query must wait: `.waitForNonStaleResults()` on the query, or the polling helper in `testing.md`. Never wait on hot production paths: it trades latency for consistency, so design UIs to tolerate slightly stale results instead.

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
