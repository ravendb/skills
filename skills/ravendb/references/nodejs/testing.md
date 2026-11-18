# Testing RavenDB code: Node.js

Pick the route in `../testing.md` first.

**There is no Node.js test driver** and no embedded server: Route 2 is the only route, one database per test on a server you run for the suite.

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

- `DatabaseRecord` is a plain object type here, not a class: pass `{ databaseName }`. The delete is plural (`DeleteDatabasesOperation`) and takes a parameter object; there is no singular form.
- Keep **one** long-lived store for creating and deleting databases (any database name: `maintenance.server` ignores it) beside the short-lived per-test stores. `GetDatabaseNamesOperation` on it at suite start finds the leftovers to sweep.

## Waiting for indexing

No driver helper here. After a bulk seed or an index deploy, poll the database statistics until no index is stale:

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
