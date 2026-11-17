# RavenDB Python client: operations and their traps

This file holds the safety rule and the traps for work beyond CRUD: databases, subscriptions, patching, attachments,
counters, time series, revisions, cluster-wide transactions and concurrency, and facet calls. Every API here is in the
docs: find the page in `../client-docs.md` and read its `.python.md` copy for the server's version. An operation this
file does not show still exists: check the docs page for your server version before saying it does not.

**Most of these are writes.** Creating or deleting a database, creating or deleting a subscription, patching one
document or by query, a revisions configuration, and putting or deleting a compare-exchange value all change state that
outlives your task. Under the production rule in `SKILL.md`, name the operation and the database it lands on and get the
user's agreement first. Deleting a database with `hard_delete` removes its files for good.

## Creating and deleting a database

```python
from ravendb import CreateDatabaseOperation, GetDatabaseNamesOperation
from ravendb.serverwide.database_record import DatabaseRecord
from ravendb.serverwide.operations.common import DeleteDatabaseOperation

# ensure-exists: create only if missing
if "Reports" not in store.maintenance.server.send(GetDatabaseNamesOperation(0, 100)):
    store.maintenance.server.send(CreateDatabaseOperation(DatabaseRecord("Reports")))

# hard_delete=True also erases the data files, not just the record
store.maintenance.server.send(DeleteDatabaseOperation("Reports", hard_delete=True))
```

- `DatabaseRecord` is not exported at the package root, so `from ravendb import DatabaseRecord` fails. Import it from
  `ravendb.serverwide.database_record`.
- There is no `DeleteDatabasesOperation` in this client, even where a docs page shows one.
  To delete several, pass
  `DeleteDatabaseOperation(parameters=DeleteDatabaseOperation.Parameters(database_names=[...], hard_delete=True))`.

## Traps

### Dispatch

- Server-level operations (create, delete or list databases) go through `store.maintenance.server.send(...)`.
  `store.maintenance.send(...)` targets the store's own database (or `.for_database(name)`), and
  `store.operations.send(...)` runs data operations such as patches.

### Subscriptions

- **A named subscription is create-once, not upsert.** `create_for_options` with a name that already exists is rejected
  (`RachisApplyException`, "already in use in a subscription with different Id"), and the error does not say to look
  first. Bootstrap code that reruns must list with `store.subscriptions.get_subscriptions(start, take)` and create only
  when missing.
- The worker connects over the server's **TCP** port, not HTTP: the client reads `GET /info/tcp` and dials the address
  the server advertises there. A server whose TCP port is published on a different host port than it binds (a Docker
  remap) sends the worker to the wrong place, and the error names a missing database rather than a wrong port.
  `../install.md` has the fix.
- Delivery is at least once: a crash before the batch is acknowledged replays it on the next worker. Make the
  processing idempotent.
- `worker.run(...)` returns a `concurrent.futures.Future` that completes only on an error or on close; the batch loop
  runs on a background thread. `future.result()` blocks until then, so keep the worker alive and `close()` it to stop.
- Unlicensed servers cap subscriptions per database, and concurrent workers on one subscription need a license: read
  `MaxNumberOfSubscriptionsPerDatabase` and `HasConcurrentDataSubscriptions` from `GET /license/status` first
  (`../version-gate.md`).

### Patching

- Patch by query, delete by query and other long-running operations run in the background on the server. Send them
  with `store.operations.send_async(op)`, which returns an `Operation`, and call `.wait_for_completion()` before reading
  what they changed: nothing waits for you.

### Document extensions

- `session.advanced.revisions.get_for(id, T)` and `get_metadata_for(id)` return at most 25 entries unless you pass
  `start` and `page_size`. Nothing says the list was cut.
- Revision retention is license-capped: a configuration above `MaxNumberOfRevisionsToKeep` or
  `MaxNumberOfRevisionAgeToKeepInDays` is refused with HTTP 402. There is no `LicenseLimitException` class in this
  package: what you catch is a `RavenException` (from `ravendb.exceptions.raven_exceptions`) whose message carries the
  server's "LicenseLimitException: ... exceeds the licensed one". A `default_config` (database-wide rather than per
  collection) is refused outright on an unlicensed server whatever the numbers: configure per collection. Read both caps
  and `CanSetupDefaultRevisionsConfiguration` from `GET /license/status` first (`../version-gate.md`).

### Concurrency

- Conventions freeze at `store.initialize()`. `store.conventions.use_optimistic_concurrency` works only before it; on a
  store handed to you already initialized (the test driver's, for one) it raises
  `RuntimeError: Conventions has been frozen`. Use the per-session `session.advanced.use_optimistic_concurrency = True`
  instead.
- **(client 7.2.2+)** adds `session.advanced.optimistic_concurrency_mode` (`WRITES`, `WRITES_AND_READS`, default
  `NONE`). The boolean stays as a view of it and is not deprecated, unlike in .NET. On conventions, setting both the
  boolean and the mode raises.

### Facets and advanced queries

- A facet query written as raw RQL runs through `session.advanced.raw_query(rql, T).execute_aggregation()`. The ordinary
  result path fails: the server answers "Raw query with aggregation by facet should be called by executeAggregation
  method". The builder form, `query.aggregate_by(...)`, ends in `.execute()` and returns `{field: FacetResult}`.
- Every field on a returned `FacetValue` ends in an underscore: `count_`, `sum_`, `min_`, `max_`, `average_`,
  `range_`. The bare names do not exist, so `value.average` raises
  `AttributeError: 'FacetValue' object has no attribute 'average'`, and the Python docs pages do not show the
  underscores.

## Docs

| You need | `../client-docs.md` topic |
|---|---|
| Which executor runs an operation | Operations: `maintenance`, `maintenance.server`, `operations` |
| Database record options, listing databases | Creating a database, Deleting a database, Listing databases |
| Subscriptions: create, consume, worker options, list, update, delete | Creating a data subscription, Consuming a data subscription, Subscription worker options, Subscription maintenance |
| Session patches, `PatchOperation`, patch by query | Patching one document, Patch by query |
| Attachments | Storing attachments, Loading attachments |
| Counters | Counters, Reading counters |
| Time series | Appending time series entries, Reading time series entries |
| Revisions | Configuring revisions, Loading revisions |
| Cluster-wide sessions, compare exchange | Cluster-wide transactions, Compare exchange, Creating compare-exchange items |
| Optimistic concurrency | Optimistic concurrency |
| Facets, suggestions, more like this, spatial from code | Facets, Suggestions, More like this, Spatial queries; the RQL side is in `../rql-docs.md` |
