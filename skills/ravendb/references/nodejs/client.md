# RavenDB Node.js client: minimal start and traps

This file holds the minimal start, verbatim, and the traps. Every other call is in the docs, routed through
`../client-docs.md`: read the page as the `.nodejs.md` copy for the server's version. A call this file does not show
still exists: check the docs page for your server version before saying it does not.

## Minimal start

```js
const { DocumentStore } = require("ravendb");

const store = new DocumentStore("http://127.0.0.1:8080", "ConsultingDeals");
store.conventions.findCollectionNameForObjectLiteral = e => e["collection"];
store.initialize();

const session = store.openSession();

await session.store({ collection: "Clients", name: "Acme" });   // id auto: "clients/1-A"; the prefix is lower-cased
await session.saveChanges();   // one batch request; nothing hits the server before this

const client = await session.load("clients/1-A");   // null for a missing id

const results = await session.query({ collection: "Clients" })
    .whereEquals("status", "active")
    .all();

// RQL text, e.g. copied from Studio or written from ../rql-cheatsheet.md:
const rows = await session.advanced.rawQuery("from Clients where status = $s")
    .addParameter("s", "active")
    .all();

session.dispose();
// on shutdown:
store.dispose();
```

- One `DocumentStore` per app. `initialize()` is mandatory before any use; conventions are frozen at that point.
- `findCollectionNameForObjectLiteral` MUST be set before `initialize()` when storing plain object literals; otherwise all literals land in the `@empty` collection. Class instances don't need it (collection derives from class name).
- A session is a unit of work with an identity map. It holds every document it received in full (`load`, an include, a query without `selectFields`), keyed by id, with a copy of the JSON as it arrived. `saveChanges()` diffs the tracked documents against those copies and sends the differences, plus anything stored or deleted, in one batch; nothing else reaches the server. Loading the same id twice in one session hits the cache (no second request).
- `query({ collection })` is a dynamic query (auto index); `query({ indexName: "Clients/ByName" })` targets a static index (`indexes.md`).

## Secured server (certificate)

A secured server needs an X.509 client certificate on the store, as a third constructor argument (not a convention):

```js
const fs = require("fs");

const store = new DocumentStore("https://a.myapp.ravendb.cloud", "ConsultingDeals", {
    certificate: fs.readFileSync("./client.pfx"),   // pfx: Buffer; pem: the file's text
    type: "pfx",                                    // "pem" | "pfx"
    password: process.env.RAVENDB_CERT_PASSWORD,    // omit if unprotected
    ca: fs.readFileSync("./ca.crt")                 // only for a self-signed CA
});
store.initialize();
```

- `type: "pem"` expects one PEM holding **both** the certificate and its private key (that is what RavenDB's `.pem` download is); `type: "pfx"` expects the raw bytes as a `Buffer`.
- The certificate must be on the store before `initialize()`, and the URL must be `https://`.
- Never commit the certificate or its password: read both from the environment.
- Other options: `../client-docs.md` (Secured server: client certificate).

## Traps

- **Sorting on a number or a date needs the ordering type as a second argument.** `orderBy`/`orderByDescending` name the field as a string, and a string field name sorts as a **string** unless you say otherwise: `.orderByDescending("amount")` puts `99952` above `243889170`. Pass `"Double"`, `"Long"` or `"AlphaNumeric"` whenever the field is not text: `.orderByDescending("amount", "Double")`. This returns wrong rows with no error.
- **That second argument is a case-sensitive exact match and an unrecognised value is discarded in silence.** `"double"`, `"DOUBLE"` and `"banana"` all behave exactly like passing nothing, so the sort falls back to lexical and you get the same wrong rows you were trying to avoid. Only `"Long"`, `"Double"`, `"AlphaNumeric"` and `"String"` count. Read a number back off the top row and check it is the largest one, because the call site looks correct either way.
- Field names in queries are the literal JSON property names: the client does no case conversion by default, so use exactly what you stored.
- Not in the identity map, so not tracked: projections (`selectFields`), streams, aggregations, facets. Mutating one and calling `saveChanges()` writes nothing and raises nothing (`session.advanced.hasChanges()` stays false); `getDocumentId` and `getMetadataFor` cannot see it either. To change documents without loading them in full, patch (`operations.md`).
- The `id` property on the entity is populated by the client after `store()`; it is not stored inside the document body. It is also populated on entities returned by a query, so `results[0].id` is the document id; `session.advanced.getDocumentId(entity)` does the same. Projections are not tracked and carry no `id`, so project `id()` in the query instead.
- Include paths are resolved on what the query returns. On a projected query the include is silently dropped unless the field it walks is in the projection: `select DealName, AccountId include AccountId` includes the accounts, `select DealName include AccountId` includes nothing and every later load is a request.
- Dates round-trip as `Date` for class entities; when comparing in queries pass `Date` objects, not strings, unless you stored ISO strings.
- 30 requests per session (`store.conventions.maxNumberOfRequestsPerSession`); exceeding throws. Open a new session instead of raising it. `session.advanced.numberOfRequests` shows the current count.

## Bulk insert

The calls: `../client-docs.md` (Bulk insert). What that page does not warn about:

- `await bulk.finish()` is mandatory: it flushes the remaining batch, and nothing persists without it.
- `bulk.store({ collection: "Deals", ...row })` needs `findCollectionNameForObjectLiteral` (Minimal start) or the rows land in `@empty`.
- Ids ending in `|` are rejected in bulk insert.

## Staleness

Queries run on indexes that update asynchronously; a query right after `saveChanges()` may return stale results. Per
query: `session.query({ collection: "Clients" }).waitForNonStaleResults(5000)` (timeout in ms), never on hot production
paths. Waiting for every index at once: the helper in `testing.md`. Test-suite discipline: `../testing.md`; the driver and per-test
database call forms: `testing.md`.

## Docs

| You need | `../client-docs.md` topic |
|---|---|
| Store options beyond the URL and database | Creating the document store; Conventions |
| Explicit ids, the server-assigned tail (`/` suffix), cluster-wide identities (pipe suffix) | Document ids |
| Load several ids, `include` on load | Loading documents, `include` on load |
| `include` on a query | Related documents: `include`, `load` |
| Delete a document | Deleting documents |
| `getMetadataFor`, `@expires` and other metadata | Metadata |
| A higher request limit | Requests per session limit |
| `whereIn`, `whereBetween`, `whereStartsWith`, `whereExists`, `containsAny` | Filtering |
| `orElse`, `not`, subclauses, `usingDefaultOperator` (before any condition) | Logical operators |
| The query builder as a whole | Document query API |
| A static index | Querying a static index |
| `statistics(...)`: total results, `isStale` | Query statistics: total results, staleness |
| `count()`, `first()`, `single()` | Counting results |
| `selectFields` | Projections |
| `distinct()` | Distinct |
| `skip`, `take` | Paging |
| `lazily()`, `countLazily()` | Lazy queries |
| `session.advanced.stream`, `streamInto` | Streaming results |
| `search(...)` and its options; sorting | `../rql-docs.md` (Full-text search; Sorting) |
