# RavenDB Node.js client: operations and their traps

Operation traps for the Node.js client. The APIs: `../client-docs.md`.

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

- Create, delete and list databases through `store.maintenance.server.send(...)`; `store.maintenance.send(...)` (no
  `.server`) targets the store's own database, `store.operations.send(...)` runs data operations such as patches.

### Subscriptions

- **A named subscription is create-once, not upsert.** A second `create({ name, query })` with a taken name fails with
  "already in use in a subscription with different Id". Check `getSubscriptions(0, 100)` (name in `subscriptionName`) or
  `getSubscriptionState(name)` first; `update({ name, query })` changes an existing one. An unnamed `create()` gets a
  generated name you cannot find again.
- The worker dials the **TCP** port that `GET /info/tcp` advertises, not HTTP. Behind a Docker remap of that port it
  dials the wrong place, and the error names a missing database, not a port: `../install.md` has the fix.
- The `end` event fires with no argument on a clean dispose and a fatal error alike. A wrong-address failure ends the
  worker without `connectionRetry`, so a supervisor watching only `connectionRetry` waits forever.

### Changes

- `store.changes()` is ephemeral: no server-side task, no resume after a restart. For durable, acked processing use a
  subscription.
- Keep the handle `.on("data", ...)` returns and `dispose()` it when the consumer leaves (in an SSE handler, on the
  request's `close`). `off("data", () => {})` with a **fresh** function removes nothing, leaking the listener and its
  connection observer per connect and disconnect. Dispose `store.changes()` itself only when nothing on it is still
  needed.

### Patching

- `PatchByQueryOperation` runs in the background: `await op.waitForCompletion()` on the handle from
  `store.operations.send(...)` before reading results (tests too); it also surfaces script errors. It resolves to
  `undefined`, not a patched count.

### Document extensions

- Revisions exist only for documents in a real collection: an object literal stored without
  `findCollectionNameForObjectLiteral` (`client.md`) lands in `@empty`, and `revisions.getFor` returns an empty array
  with no error.
- `revisions.getFor(id)` and `revisions.getMetadataFor(id)` return at most 25 entries unless you pass
  `{ start, pageSize }`, and nothing says the list was cut.
- The Node.js client has no revert operation: load the revision (`revisions.get(changeVector)`), copy its fields onto
  the live document, `saveChanges()`.
- Over the revision caps (`../version-gate.md`), `minimumRevisionsToKeep` is refused with HTTP 402, message ending
  "exceeds the licensed one"; the unlicensed cap is below any round number. No `LicenseLimitException` exists here to
  catch by type. Unlicensed, a `defaultConfig` is refused at any number: configure per collection.

### Concurrency

- `session.advanced.useOptimisticConcurrency = true` works on every supported client. `optimisticConcurrencyMode`
  (`"Writes"`, `"WritesAndReads"`, default `"None"`) needs **(client 7.2.2+)**; on an older client, assigning it is a
  plain property write that turns nothing on (`../version-gate.md`).

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
| Facets, suggestions, more like this, spatial from code | `../rql-docs.md` (Facets; Suggestions; More like this; Spatial on a dynamic query) |
