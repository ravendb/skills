# RavenDB .NET client: minimal start and traps

This file holds the minimal start, verbatim, and the traps. Every other call is in the docs, routed through
`../client-docs.md`: read the page as the C# copy (`<path>.md`) for the server's version. A call this file does not
show still exists: check the docs page for your server version before saying it does not.

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

- One `DocumentStore` per app (it is thread-safe and expensive). `Initialize()` is mandatory; conventions are frozen at that point, so set `store.Conventions` before it.
- Collection name derives from the class name, pluralized (`Client` → `Clients`).
- A session is a unit of work with an identity map. It holds every document it received in full (`Load`, an include, a query without a projection), keyed by id, with a copy of the JSON as it arrived. `SaveChanges()` diffs the tracked documents against those copies and sends the differences, plus anything stored or deleted, in one batch; nothing else reaches the server. Mutate a loaded entity and `SaveChanges()` persists it, no second `Store` call needed. Loading the same id twice hits the session cache.
- A session is not thread-safe. Dispose it (`using`); an undisposed session leaks tracked entities, not connections, but treat it as a bug.
- Async mirror: `store.OpenAsyncSession()`, `StoreAsync`, `SaveChangesAsync()`, `LoadAsync<T>`, and `ToListAsync()` from `Raven.Client.Documents` on queries. Prefer async in app code.
- `session.Query<T>()` is a dynamic query (server creates/reuses an auto index); `session.Query<T, TIndexCreator>()` targets a static index (`indexes.md`).

## ASP.NET Core

In an ASP.NET Core app the store is a singleton and the session is scoped to the request:

```csharp
var store = new DocumentStore { Urls = new[] { cfg["Raven:Url"] }, Database = cfg["Raven:Database"] };
store.Initialize();
builder.Services.AddSingleton<IDocumentStore>(store);
builder.Services.AddScoped<IAsyncDocumentSession>(sp => sp.GetRequiredService<IDocumentStore>().OpenAsyncSession());
```

The scoped session is one unit of work per request, disposed with the request. Inject `IDocumentStore` instead when a handler needs several sessions or a bulk insert. Index deployment and database creation belong in the startup path before `app.Run()` (`../structure.md`).

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

- `Certificate` is an `X509Certificate2` and must be set before `Initialize()`, and the URL must be `https://`. `X509CertificateLoader` is .NET 9+; older targets use `new X509Certificate2(path, password)`.
- The loader is **pkcs12-only**: convert a `.pem` download first (`openssl pkcs12 -export -in client.pem -out client.pfx`). The file must be readable by the process user.
- **The client certificate is only half of it: the *server's* certificate must also be trusted.** Against RavenDB Cloud this is invisible because those chain to a public root, but a self-signed or private-CA server fails at `Initialize()` with `Failed to retrieve database topology from all known nodes` → `The remote certificate was rejected by the provided RemoteCertificateValidationCallback`. Trust the CA out of band (`SSL_CERT_FILE=/path/ca.crt` needs no code), or register `Raven.Client.Http.RequestExecutor.RemoteCertificateValidationCallback`, a public static event.
- Never commit the `.pfx` or its password.
- Other options: `../client-docs.md` (Secured server: client certificate).

## Traps

- The bare string overload of `Query<T>` is an **index** name, not a collection name: `session.Query<Deal>("Deals")` throws `IndexDoesNotExistException: Could not find index Deals`. To name a collection, pass the argument by name: `session.Query<Deal>(collectionName: "Deals")`.
- **Declare a small class for the entity; do not query `dynamic` or `object`.** `Query<dynamic>()` breaks LINQ two ways: a lambda over it fails to compile with `CS1963: An expression tree may not contain a dynamic operation`, and the string-named operators return a plain `IOrderedQueryable<dynamic>`, which has lost `Statistics` and every other Raven extension. A three-property class costs less than working around either.
- `string.Contains` does not translate: `.Where(x => x.Name.Contains("acme"))` throws `NotSupportedException: Could not understand expression`. Use `.Search(x => x.Name, "acme")` for an analyzed field, or `StartsWith`/`EndsWith`.
- Searching **several fields at once** chains `Search` calls and passes the combining option on the later ones: `.Search(x => x.Name, q).Search(x => x.Email, q, options: SearchOptions.Or)`. The enum is `Raven.Client.Documents.SearchOptions` (`Or`/`And`/`Not`/`Guess`, default `Guess`), not under `.Queries`. `OrElse()` exists only on `Advanced.DocumentQuery`, not on `IRavenQueryable<T>`, so it will not compile here.
- Sorting: LINQ `.OrderBy(x => x.Amount)` carries the property type and sorts numerically. The **string-named** form on `Advanced.DocumentQuery` does not: `.OrderByDescending("Amount")` sorts as a string and puts `99952` above `243889170`. Pass the ordering type, from `Raven.Client.Documents.Session`: `.OrderByDescending("Amount", OrderingType.Double)`, and `Long` / `AlphaNumeric` likewise. This returns wrong rows with no error.
- `.Statistics(out QueryStatistics stats)` is defined on `IRavenQueryable<T>`, so keep the query in a `var` and keep `T` a real class. Anything that drops it back to a plain `IQueryable<T>` / `IOrderedQueryable<T>` loses the method, and the compiler only says `CS1061: does not contain a definition for 'Statistics'`.
- When raw RQL projects, `T` in `RawQuery<T>` is a class with the projected properties or `Dictionary<string, object>`; each row also carries an `@metadata` object, so `Dictionary<string, string>` fails to deserialize. On an async session the call is `AsyncRawQuery<T>`.
- Field names in the database are the C# property names (PascalCase by default): RQL and `DocumentQuery` strings must match exactly.
- Not in the identity map, so not tracked: projections (`Select`, `ProjectInto`), streams, aggregations, facets. Mutating one and calling `SaveChanges()` writes nothing and raises nothing; `GetDocumentId` and `GetMetadataFor` cannot see it either. To change documents without loading them in full, patch (`operations.md`).
- A `public string Id` property on the entity is populated by the client after `Store()`; it is not stored inside the document body. To read the id of a document you **queried** rather than stored, use `session.Advanced.GetDocumentId(entity)`. It works on any tracked entity, including one whose class has no `Id` property. Projections are not tracked, so project `id()` in the query instead.
- Include paths are resolved on what the query returns. On a projected query the include is silently dropped unless the field it walks is in the projection: `select DealName, AccountId include AccountId` includes the accounts, `select DealName include AccountId` includes nothing and every later load is a request.
- 30 requests per session (`store.Conventions.MaxNumberOfRequestsPerSession`); exceeding throws. Open a new session instead of raising it. `session.Advanced.NumberOfRequests` shows the current count.

## Bulk insert

The calls: `../client-docs.md` (Bulk insert). What that page does not warn about:

- Open it with `using (var bulk = store.BulkInsert())`: disposing flushes the remaining batch, and nothing persists without it.
- An entity whose `Id` is initialized to `""` throws `BulkInsertInvalidOperationException: Document id must have a non empty value`: bulk insert treats a non-null id as explicit. Leave the property `null` (`string?`) and let the client assign it.
- Ids ending in `|` are rejected in bulk insert.

## Staleness

Queries run on indexes that update asynchronously; a query right after `SaveChanges()` may return stale results. Per
query: `session.Query<Client>().Customize(x => x.WaitForNonStaleResults(TimeSpan.FromSeconds(5)))`, never on hot
production paths. Waiting for every index at once: `testing.md` (test driver), or `../client-docs.md` (Index statistics, polling for non-stale). Test-suite discipline: `../testing.md`; the driver and
per-test database call forms: `testing.md`.

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
| `Select`, `ProjectInto<T>()` | Projections |
| `Distinct` | Distinct |
| `Skip`, `Take` | Paging |
| `Lazily` | Lazy queries |
| `session.Advanced.Stream` | Streaming results |
| `Search` and `SearchOptions`; sorting | `../rql-docs.md` (Full-text search; Sorting) |
