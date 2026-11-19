# RavenDB Python client: operations and their traps

Operation traps for the Python client. The APIs: `../client-docs.md`.

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

- `DatabaseRecord` is not exported at the package root, so `from ravendb import DatabaseRecord` fails: import it from
  `ravendb.serverwide.database_record`.
- This client has no `DeleteDatabasesOperation`, whatever a docs page shows. To delete several, pass
  `DeleteDatabaseOperation(parameters=DeleteDatabaseOperation.Parameters(database_names=[...], hard_delete=True))`.

## Traps

### Dispatch

- Create, delete and list databases through `store.maintenance.server.send(...)`; `store.maintenance.send(...)` targets
  the store's own database (or `.for_database(name)`), `store.operations.send(...)` runs data operations such as
  patches.

### Subscriptions

- **A named subscription is create-once, not upsert.** `create_for_options` with a taken name fails with
  `RachisApplyException`, "already in use in a subscription with different Id". Check
  `store.subscriptions.get_subscriptions(start, take)` first.
- The worker dials the **TCP** port that `GET /info/tcp` advertises, not HTTP. Behind a Docker remap of that port it
  dials the wrong place, and the error names a missing database, not a port: `../install.md` has the fix.
- `worker.run(...)` returns a `concurrent.futures.Future` that completes only on an error or on close (batches run on a
  background thread), so `future.result()` blocks until then. Keep the worker alive; `close()` stops it.

### Patching

- Patch by query, delete by query and other long-running operations run in the background: send them with
  `store.operations.send_async(op)` and call `.wait_for_completion()` on the returned `Operation` before reading
  results.

### Document extensions

- `session.advanced.revisions.get_for(id, T)` and `get_metadata_for(id)` return at most 25 entries unless you pass
  `start` and `page_size`, and nothing says the list was cut.
- Over the revision caps (`../version-gate.md`) the server answers HTTP 402. With no `LicenseLimitException` class here,
  catch `RavenException` (`ravendb.exceptions.raven_exceptions`), whose message carries "LicenseLimitException: ...
  exceeds the licensed one". Unlicensed, a database-wide `default_config` is refused at any numbers: configure per
  collection.

### Concurrency

- On an already initialized store (the test driver's, for one), setting `store.conventions.use_optimistic_concurrency`
  raises `RuntimeError: Conventions has been frozen`. Set `session.advanced.use_optimistic_concurrency = True` per
  session instead.
- **(client 7.2.2+)** adds `session.advanced.optimistic_concurrency_mode` (`WRITES`, `WRITES_AND_READS`, default
  `NONE`). The boolean stays as a view of it, not deprecated as in .NET. Setting both on conventions raises.

### Facets and advanced queries

- Every `FacetValue` field ends in an underscore (`count_`, `sum_`, `min_`, `max_`, `average_`, `range_`), which the
  Python docs pages do not show: `value.average` raises
  `AttributeError: 'FacetValue' object has no attribute 'average'`.

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
| Facets, suggestions, more like this, spatial from code | `../rql-docs.md` (Facets; Suggestions; More like this; Spatial on a dynamic query) |
