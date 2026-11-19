# RavenDB .NET client: minimal start and traps

Minimal start and traps for the .NET client. Every other call: `../client-docs.md`.

## Minimal start

```csharp
using Raven.Client.Documents;

var store = new DocumentStore
{
    Urls = new[] { "http://127.0.0.1:8080" },
    Database = "ConsultingDeals"
};
store.Initialize();

using (var session = store.OpenSession())
{
    var client = new Client { Name = "Acme" };
    session.Store(client);                 // id auto: "clients/1-A"
    session.SaveChanges();                 // one batch request; nothing hits the server before this

    var loaded = session.Load<Client>("clients/1-A");   // null for a missing id

    var active = session.Query<Client>()
        .Where(x => x.Status == "active")
        .ToList();

    // RQL text, e.g. copied from Studio or written from ../rql-cheatsheet.md:
    var rows = session.Advanced.RawQuery<Client>("from Clients where Status = $s")
        .AddParameter("s", "active")
        .ToList();
}
// on shutdown:
store.Dispose();

public class Client                        // collection "Clients"; Id is filled in on Store()
{
    public string? Id { get; set; }
    public string? Name { get; set; }
    public string? Status { get; set; }
}
```

- The session tracks every document it receives in full (`Load`, an include, a query without a projection): `SaveChanges()` sends their changes, plus stores and deletes, in one batch, so a mutated entity needs no second `Store`. Loading an id again makes no request.

## Secured server (certificate)

```csharp
using System.Security.Cryptography.X509Certificates;   // X509CertificateLoader lives here
using Raven.Client.Documents;

var store = new DocumentStore
{
    Urls = new[] { "https://a.myapp.ravendb.cloud" },
    Database = "ConsultingDeals",
    Certificate = X509CertificateLoader.LoadPkcs12FromFile(
        Environment.GetEnvironmentVariable("RAVENDB_CERT_PATH"),
        Environment.GetEnvironmentVariable("RAVENDB_CERT_PASSWORD"))
};
store.Initialize();
```

- `Certificate` is an `X509Certificate2`, set before `Initialize()`. `X509CertificateLoader` is .NET 9+; older targets use `new X509Certificate2(path, password)`.
- The loader is **pkcs12-only**: convert a `.pem` download first (`openssl pkcs12 -export -in client.pem -out client.pfx`).
- **Trust the server's certificate too.** A self-signed or private-CA server fails `Initialize()` with `Failed to retrieve database topology from all known nodes` → `The remote certificate was rejected by the provided RemoteCertificateValidationCallback` (never on Cloud, which chains to a public root). Trust the CA out of band (`SSL_CERT_FILE=/path/ca.crt`) or handle the static event `Raven.Client.Http.RequestExecutor.RemoteCertificateValidationCallback`.
- Other options: `../client-docs.md` (Secured server: client certificate).

## Traps

- The bare string overload of `Query<T>` takes an **index** name: `session.Query<Deal>("Deals")` throws `IndexDoesNotExistException: Could not find index Deals`. Name a collection with `session.Query<Deal>(collectionName: "Deals")`.
- **Query a small entity class, not `dynamic` or `object`.** Lambdas over `Query<dynamic>()` fail with `CS1963: An expression tree may not contain a dynamic operation`; string-named operators return a plain `IOrderedQueryable<dynamic>` without `Statistics` or other Raven extensions.
- `string.Contains` does not translate: `.Where(x => x.Name.Contains("acme"))` throws `NotSupportedException: Could not understand expression`. Use `.Search(x => x.Name, "acme")` on an analyzed field, or `StartsWith`/`EndsWith`.
- Search several fields by chaining `Search`, with the combining option on later calls: `.Search(x => x.Name, q).Search(x => x.Email, q, options: SearchOptions.Or)`. The enum is `Raven.Client.Documents.SearchOptions` (`Or`/`And`/`Not`/`Guess`, default `Guess`), not under `.Queries`. `OrElse()` exists only on `Advanced.DocumentQuery`, not on `IRavenQueryable<T>`.
- LINQ `.OrderBy(x => x.Amount)` sorts numerically, but the string-named `.OrderByDescending("Amount")` on `Advanced.DocumentQuery` sorts as a string (`99952` above `243889170`), silently. Pass `OrderingType.Double` (or `Long`, `AlphaNumeric`) from `Raven.Client.Documents.Session`: `.OrderByDescending("Amount", OrderingType.Double)`.
- `.Statistics(out QueryStatistics stats)` exists only on `IRavenQueryable<T>`: a query turned into a plain `IQueryable<T>`/`IOrderedQueryable<T>` loses it, with only `CS1061: does not contain a definition for 'Statistics'`. Keep the query in a `var` and `T` a real class.
- A projecting `RawQuery<T>` needs `T` to be a class with the projected properties or `Dictionary<string, object>`: each row carries an `@metadata` object, so `Dictionary<string, string>` fails to deserialize. Async sessions: `AsyncRawQuery<T>`.
- Stored field names are the C# property names (PascalCase by default), so RQL and `DocumentQuery` strings must match them exactly.
- Not tracked: projections (`Select`, `ProjectInto`), streams, aggregations, facets. Changing one and calling `SaveChanges()` writes nothing, silently, and `GetDocumentId`/`GetMetadataFor` cannot see it. To change documents without loading them in full, patch (`operations.md`).
- The client sets a `public string Id` on `Store()`; the document body does not hold it. For a queried entity, even one with no `Id` property, use `session.Advanced.GetDocumentId(entity)`; for a projection (untracked), project `id()`.
- 30 requests per session (`store.Conventions.MaxNumberOfRequestsPerSession`), then it throws: open a new session rather than raising the limit. Current count: `session.Advanced.NumberOfRequests`.

## Bulk insert

The calls: `../client-docs.md` (Bulk insert). What that page does not warn about:

- Open it with `using (var bulk = store.BulkInsert())`: disposing flushes the remaining batch, and nothing persists without it.
- An `Id` initialized to `""` throws `BulkInsertInvalidOperationException: Document id must have a non empty value`, because bulk insert treats any non-null id as explicit. Leave it `null` (`string?`).
- Ids ending in `|` are rejected in bulk insert.

## Staleness

Per query: `session.Query<Client>().Customize(x => x.WaitForNonStaleResults(TimeSpan.FromSeconds(5)))`.
Every index at once: `WaitForIndexing(store)` from the test driver (`testing.md`), or
`../client-docs.md` (Index statistics, polling for non-stale).

## Docs

| You need | `../client-docs.md` topic |
|---|---|
| Other `DocumentStore` settings and `Conventions` | Creating the document store; Conventions |
| Explicit ids, the server-assigned tail (`/` suffix), cluster-wide identities (pipe suffix) | Document ids |
| `OpenAsyncSession` and session options | Opening a session |
| Load several ids, `Include` on load | Loading documents, `include` on load |
| `Include` on a query | Related documents: `include`, `load` |
| Delete a document | Deleting documents |
| `GetMetadataFor` and metadata keys | Metadata |
| A higher request limit | Requests per session limit |
| `DateTime` and time zones | Storing dates |
| `Advanced.DocumentQuery`: `WhereEquals`, `AndAlso`, `OpenSubclause`, field names known only at runtime | Document query API |
| `OrElse`, `Not`, subclauses | Logical operators |
| `Query<T, TIndexCreator>()` and other static-index forms | Querying a static index |
| `Statistics`: `TotalResults`, `IsStale` | Query statistics: total results, staleness |
| `Count`, `CountAsync` | Counting results |
| `Select`, `ProjectInto<T>()` | `../rql-docs.md` (Projections) |
| `Distinct` | Distinct |
| `Skip`, `Take` | `../rql-docs.md` (Paging) |
| `Lazily` | Lazy queries |
| `session.Advanced.Stream` | Streaming results |
| `Search` and `SearchOptions`; sorting | `../rql-docs.md` (Full-text search; Sorting) |
