# Testing RavenDB code: Node.js

Routes and the language-neutral discipline (staleness, what to test, CI): `../testing.md`.

**There is no Node.js test driver**: no embedded server, no `RavenTestDriver` equivalent. Route 2 is the only route: run a server once for the suite (`../install.md`) and give each test its own database.

```js
const { DocumentStore, CreateDatabaseOperation, DeleteDatabasesOperation } = require("ravendb");

async function testStore(name) {
    const store = new DocumentStore(process.env.RAVENDB_URL || "http://127.0.0.1:8080", name);
    store.conventions.findCollectionNameForObjectLiteral = e => e["collection"];   // literals land in @empty without this
    store.initialize();
    await store.maintenance.server.send(new CreateDatabaseOperation({ databaseName: name }, 1));
    return store;
}
// teardown:
await store.maintenance.server.send(new DeleteDatabasesOperation({ databaseNames: [name], hardDelete: true }));
store.dispose();
```

- `DatabaseRecord` is a plain object type in the Node client, not a class: pass `{ databaseName }`. The delete operation is plural (`DeleteDatabasesOperation`) and parameter-object shaped; there is no singular form.
- Name databases uniquely per test (`test-${suite}-${Date.now()}`), hard-delete on teardown, and delete leftovers at suite start.
- Creating and deleting databases is server-level work, so keep **one** long-lived store for it (any database name; `maintenance.server` ignores it) alongside the short-lived per-test stores. `GetDatabaseNamesOperation` at suite start finds the leftovers to sweep.
- Point the suite at the server with an env var, never a hardcoded URL. Docker for CI: `../install.md`.
- Waiting out staleness has no driver helper here: `.waitForNonStaleResults()` on the query, or the polling helper under "Waiting for indexing" below.
- A suite that tests **subscriptions** needs the server's TCP port reachable at the address the server advertises in `GET /info/tcp`, not just the HTTP port. See the port note in `../install.md`, which is the difference between a working suite and a `database does not exist` error against someone else's server.

## Waiting for indexing

After a bulk seed or an index deploy, poll the database statistics until no index is stale:

```js
const { GetStatisticsOperation } = require("ravendb");

async function waitForIndexing(store) {
    while (true) {
        const stats = await store.maintenance.send(new GetStatisticsOperation());
        if (stats.indexes.every(i => i.state === "Disabled" || !i.isStale)) return;
        await new Promise(r => setTimeout(r, 100));
    }
}
```

Skip disabled indexes or the wait never returns.
