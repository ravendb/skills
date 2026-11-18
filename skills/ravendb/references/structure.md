# Structuring a RavenDB codebase

How the pieces wire together, in any language. The calls are in your language's `client.md`, `indexes.md` and `operations.md`, and in the docs via `client-docs.md`.

## One store, created once

`DocumentStore` is thread-safe. Construct and `initialize()` it **once per process**, hold it for the app's lifetime, and open every session from it. A store per request or query leaks the request executor and its connection pool.

- C#: register the initialized store as a DI singleton and the session as scoped, so each request gets one unit of work: `builder.Services.AddSingleton<IDocumentStore>(store)` and `builder.Services.AddScoped<IAsyncDocumentSession>(sp => sp.GetRequiredService<IDocumentStore>().OpenAsyncSession())`.
- Node/Python: a module-level instance created at boot, imported where needed.
- Conventions (id conventions, serializers, Node's `findCollectionNameForObjectLiteral`) freeze at initialization: set them before.

## Startup does the provisioning, in order

One idempotent startup path takes a bare server to a ready app:

1. Create and `initialize()` the store.
2. Ensure the database exists (`CreateDatabase`, swallow "already exists").
3. **Deploy every static index**: the client's bulk helper (`IndexCreation.CreateIndexes` / `createIndexes` / `create_indexes`) or each task's own execute call (your language's `indexes.md`; `client-docs.md` (Defining and deploying a static index)). An unchanged definition is a no-op, a changed one rebuilds side-by-side. Deploy here only, never lazily from a query path.
4. Enable the server-side features the app relies on (Refresh, ETL, expiration, AI connection strings and agents).
5. Seed idempotently: check for existing data and skip. Bulk insert assigns a fresh auto-id per call and never upserts, so a second run silently doubles the collection. Use explicit ids when a re-run must be a no-op.
6. Wait once for non-stale indexes (poll `GetStatisticsOperation`: `client-docs.md` (Index statistics, polling for non-stale)) **after** deploy and seed, never before. A wait ahead of the deploy returns immediately (the index does not exist yet) and the first queries hit a stale index.

A static index serves only the queries that name it. Query the collection instead (`query(collection)`, raw `from Collection where …`) and the server quietly builds a *separate* auto-index while the static one sits unused; name an index that was never deployed and the query fails (HTTP 404; `IndexDoesNotExistException` in the clients). Deploy it at startup **and** query it by name, or do not deploy it.

## Indexes are code, in one place

Every static index is a class (`AbstractIndexCreationTask` / `AbstractJavaScriptIndexCreationTask` / C#-syntax task) in one indexes module (`indexes.ts`, `app/indexes.py`, index classes in the assembly), not string literals in handlers. The class name *is* the index name (`_` → `/`).

## Session per unit of work

Open a session per unit of work (typically one request), do the loads, queries and changes, save once, dispose. Never share one across requests or hold one for the process. Keep one logical operation's reads and writes in one session so `include()` and the identity map avoid N+1 and repeat loads. Hitting the 30-requests-per-session cap means the unit of work is too big, not that the cap should be raised.

## Where query code lives

In the data-access or handler layer, inside the session: a **deployed static index** for anything beyond a trivial filter, a dynamic `query(collection)` only for simple ad-hoc equality or range.

## One shape per collection

Nothing in RavenDB rejects a field-name drift between write paths (the seeder writes `Qty`, the API `Quantity`), and a query on either name silently misses the other's documents. Own one canonical shape and normalize at the boundary.
