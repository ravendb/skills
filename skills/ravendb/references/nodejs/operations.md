# RavenDB Node.js client: operations and their traps

This file holds the safety rule and the traps for work beyond CRUD: databases, subscriptions, the Changes API, patching,
attachments, counters, time series, revisions, cluster-wide transactions and concurrency, and facet calls. Every API
here is in the docs: find the page in `../client-docs.md` and read its `.nodejs.md` copy for the server's version. An
operation this file does not show still exists: check the docs page for your server version before saying it does not.

**Most of these are writes.** Creating or deleting a database, creating or deleting a subscription, patching one
document or by query, a revisions configuration, and putting or deleting a compare-exchange value all change state that
outlives your task. Under the production rule in `SKILL.md`, name the operation and the database it lands on and get the
user's agreement first. Deleting a database with `hardDelete` removes its files for good.

## Creating and deleting a database

```js
const { CreateDatabaseOperation, DeleteDatabasesOperation, GetDatabaseNamesOperation } = require("ravendb");

// ensure-exists: create only if missing
const names = await store.maintenance.server.send(new GetDatabaseNamesOperation(0, 100));
if (!names.includes("Reports")) {
    await store.maintenance.server.send(new CreateDatabaseOperation({ databaseName: "Reports" }, 1));
}

// hardDelete: true also erases the data files, not just the record
await store.maintenance.server.send(new DeleteDatabasesOperation({ databaseNames: ["Reports"], hardDelete: true }));
```

## Traps

### Dispatch

- Server-level operations (create, delete or list databases) go through `store.maintenance.server.send(...)`.
  `store.maintenance.send(...)` (no `.server`) targets the store's own database, and `store.operations.send(...)` runs
  data operations such as patches.

### Subscriptions

- **A named subscription is create-once, not upsert.** A second `create({ name, query })` with a taken name is rejected
  ("already in use in a subscription with different Id"), and the error does not say to look first. Bootstrap code that
  reruns must check `getSubscriptions(0, 100)` (each state carries the name as `subscriptionName`) or
  `getSubscriptionState(name)` and create only when missing; change an existing one with `update({ name, query })`. An
  unnamed `create()` lets the server generate the name, at the cost of not finding it again.
- The worker connects over the server's **TCP** port, not HTTP: the client reads `GET /info/tcp` and dials what the
  server advertises there. A server whose TCP port is published on a different host port than it binds (a Docker remap)
  sends the worker to the wrong place, and the error names a missing database rather than a wrong port. `../install.md`
  has the fix.
- Delivery is at least once: a crash before the batch is acked (the `batch` handler's `callback()`) replays the batch on
  the next worker. Make the processing idempotent.
- The `end` event fires with no argument on a clean dispose and after a fatal error alike, so it tells you nothing about
  why. A wrong-address failure ends the worker instead of entering `connectionRetry`, so a supervisor that only watches
  `connectionRetry` waits forever.
- Unlicensed servers cap subscriptions per database, and concurrent workers on one subscription need a license: read
  `MaxNumberOfSubscriptionsPerDatabase` and `HasConcurrentDataSubscriptions` from `GET /license/status` first
  (`../version-gate.md`).

### Changes

- `store.changes()` is an ephemeral feed: no server-side task, no resume after a restart. For durable, acked processing
  use a subscription instead.
- Keep the handle that `.on("data", ...)` returns and call its `dispose()` when the consumer goes away (in an SSE handler,
  on the request's `close` event). `off("data", () => {})` with a **fresh** function removes nothing: the original
  listener and its connection observer leak, once per connect and disconnect cycle. Dispose the whole `store.changes()`
  connection only when no observable on it is still needed.

### Patching

- `PatchByQueryOperation` runs in the background on the server. `store.operations.send(...)` returns an operation
  handle: `await op.waitForCompletion()` before reading what it changed (in tests too), which also surfaces script
  errors. It resolves to `undefined`, not a count of patched documents, so query again if you need the number.

### Document extensions

- Revisions only appear for documents in a real collection. An object literal stored without
  `findCollectionNameForObjectLiteral` (`client.md`) lands in `@empty`, and `revisions.getFor` then returns an empty
  array with no error to explain it.
- `revisions.getFor(id)` and `revisions.getMetadataFor(id)` return at most 25 entries unless you pass
  `{ start, pageSize }`. Nothing says the list was cut.
- There is no revert operation in the Node.js client, and the docs page on reverting has only a C# copy. Revert by
  loading the revision (`revisions.get(changeVector)`), copying its fields onto the live document and calling
  `saveChanges()`.
- Revision retention is license-capped. `minimumRevisionsToKeep` above the cap is refused with HTTP 402 and a message
  ending "exceeds the licensed one", and the unlicensed cap is low enough that any round number trips it. There is no
  `LicenseLimitException` among this client's error names, so there is nothing to catch by type. A `defaultConfig` is
  refused outright on an unlicensed server whatever the number: configure per collection. Read
  `MaxNumberOfRevisionsToKeep` and `CanSetupDefaultRevisionsConfiguration` from `GET /license/status` first
  (`../version-gate.md`).

### Concurrency

- `session.advanced.useOptimisticConcurrency = true` works on every supported client. `optimisticConcurrencyMode`
  (`"Writes"`, `"WritesAndReads"`, default `"None"`) exists from **(client 7.2.2+)**. On an older client, assigning it
  is an ordinary property write that turns nothing on: read the package version first (`../version-gate.md`).

### Facets and advanced queries

- A facet query written as raw RQL runs through `session.advanced.rawQuery(rql).executeAggregation()`. The ordinary
  `all()` fails: the server answers "Raw query with aggregation by facet should be called by executeAggregation method".
  The builder form, `session.query(...).aggregateBy(...)`, ends in `execute()`.

## Docs

| You need | `../client-docs.md` topic |
|---|---|
| Which executor runs an operation | Operations: `maintenance`, `maintenance.server`, `operations` |
| Database options, replication factor, listing | Creating a database, Deleting a database, Listing databases |
| Subscriptions: create, consume, worker options, list, update, delete | Creating a data subscription, Consuming a data subscription, Subscription worker options, Subscription maintenance |
| Live change notifications | Changes API, Document change notifications |
| Session patches, `PatchOperation`, patch by query | Patching one document, Patch by query |
| Attachments | Storing attachments, Loading attachments |
| Counters | Counters, Reading counters |
| Time series | Appending time series entries, Reading time series entries |
| Revisions | Configuring revisions, Loading revisions |
| Cluster-wide sessions, compare exchange | Cluster-wide transactions, Compare exchange, Creating compare-exchange items |
| Optimistic concurrency, change vectors | Optimistic concurrency |
| Facets, suggestions, more like this, spatial from code | Facets, Suggestions, More like this, Spatial queries; the RQL side is in `../rql-docs.md` |
