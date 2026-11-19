# RavenDB Node.js client: minimal start and traps

Minimal start and traps for the Node.js client. Every other call: `../client-docs.md`.

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

- Without `findCollectionNameForObjectLiteral` set before `initialize()`, every stored object literal lands in the `@empty` collection. Class instances take the collection from the class name.
- The session tracks every document it receives in full (`load`, an include, a query without `selectFields`): `saveChanges()` sends their changes, plus stores and deletes, in one batch. Loading an id again makes no request.

## Secured server (certificate)

The certificate goes in the third constructor argument, not a convention:

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

- `type: "pem"` takes one PEM holding **both** the certificate and its private key (RavenDB's `.pem` download); `type: "pfx"` takes the raw bytes as a `Buffer`.
- Other options: `../client-docs.md` (Secured server: client certificate).

## Traps

- **Numeric and date sorts need the ordering type as a second argument.** `orderBy`/`orderByDescending` sort a named field as a string, so `.orderByDescending("amount")` puts `99952` above `243889170`, silently. Pass `"Double"`, `"Long"` or `"AlphaNumeric"`: `.orderByDescending("amount", "Double")`.
- **That argument is case-sensitive; any other value is dropped silently.** `"double"`, `"DOUBLE"` or `"banana"` sort lexically; only `"Long"`, `"Double"`, `"AlphaNumeric"` and `"String"` count. Check that the top row holds the largest number.
- Not tracked: projections (`selectFields`), streams, aggregations, facets. Changing one and calling `saveChanges()` writes nothing, silently (`session.advanced.hasChanges()` stays false), and `getDocumentId`/`getMetadataFor` cannot see it. To change documents without loading them in full, patch (`operations.md`).
- The client sets the entity's `id` on `store()` and on query results (`results[0].id`, like `session.advanced.getDocumentId(entity)`); the document body does not hold it. Projections carry no `id`: project `id()`.
- Class entities round-trip dates as `Date`; in query comparisons pass `Date` objects, not strings, unless you stored ISO strings.
- 30 requests per session (`store.conventions.maxNumberOfRequestsPerSession`), then it throws: open a new session rather than raising the limit. Current count: `session.advanced.numberOfRequests`.

## Bulk insert

The calls: `../client-docs.md` (Bulk insert). What that page does not warn about:

- `await bulk.finish()` is mandatory: it flushes the remaining batch, and nothing persists without it.
- Ids ending in `|` are rejected in bulk insert.

## Staleness

Per query: `session.query({ collection: "Clients" }).waitForNonStaleResults(5000)` (timeout in ms). Every index at
once: the helper in `testing.md`.

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
| `whereIn`, `whereBetween`, `whereStartsWith`, `whereExists`, `containsAny` | `../rql-docs.md` (Filtering) |
| `orElse`, `not`, subclauses, `usingDefaultOperator` (before any condition) | Logical operators |
| The query builder as a whole | Document query API |
| A static index | Querying a static index |
| `statistics(...)`: total results, `isStale` | Query statistics: total results, staleness |
| `count()`, `first()`, `single()` | Counting results |
| `selectFields` | `../rql-docs.md` (Projections) |
| `distinct()` | Distinct |
| `skip`, `take` | `../rql-docs.md` (Paging) |
| `lazily()`, `countLazily()` | Lazy queries |
| `session.advanced.stream`, `streamInto` | Streaming results |
| `search(...)` and its options; sorting | `../rql-docs.md` (Full-text search; Sorting) |
