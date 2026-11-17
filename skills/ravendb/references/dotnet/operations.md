# RavenDB .NET client: operations and their traps

This file holds the safety rule and the traps for work beyond CRUD: databases, subscriptions, patching, attachments,
counters, time series, revisions, cluster-wide transactions and concurrency, and facet calls. Every API here is in the
docs: find the page in `../client-docs.md` and read its C# copy (`<path>.md`) for the server's version. An operation
this file does not show still exists: check the docs page for your server version before saying it does not.

**Most of these are writes.** Creating or deleting a database, creating or deleting a subscription, patching one
document or by query, a revisions configuration, and putting or deleting a compare-exchange value all change state that
outlives your task. Under the production rule in `SKILL.md`, name the operation and the database it lands on and get the
user's agreement first. Deleting a database with `hardDelete` removes its files for good.

## Traps

### Dispatch

- Server-level operations (create, delete or list databases) go through `store.Maintenance.Server.Send(...)`.
  `store.Maintenance.Send(...)` runs database-level operations against `store.Database`, and `store.Operations.Send(...)`
  runs data operations such as patches.

### Subscriptions

- **A named subscription is create-once, not upsert.** `Create` with a `Name` that already exists is rejected ("already
  in use in a subscription with different Id"), and the error does not say to look first. Startup code that reruns must
  check `GetSubscriptions` and create only when missing. An unnamed `Create` lets the server generate the name, at the
  cost of not finding it again.
- The worker connects over the server's **TCP** port, not HTTP: the client reads `GET /info/tcp` and dials the address
  the server advertises there. A server whose TCP port is published on a different host port than it binds (a Docker
  remap) sends the worker to the wrong place, and the error names a missing database rather than a wrong port.
  `../install.md` has the fix.
- Delivery is at least once: a crash before the batch is acknowledged replays it on the next worker. Make the
  processing idempotent.
- `worker.Run(...)` returns a `Task` that completes only on a terminal error (`SubscriptionClosedException`,
  `SubscriptionInvalidStateException`, `SubscriptionDoesNotExistException`); transient drops reconnect on their own.
  Awaiting it inline blocks the caller for the worker's whole life.
- Unlicensed servers cap subscriptions per database, and concurrent workers on one subscription need a license: read
  `MaxNumberOfSubscriptionsPerDatabase` and `HasConcurrentDataSubscriptions` from `GET /license/status` first
  (`../version-gate.md`).

### Patching

- `PatchByQueryOperation` runs in the background on the server. `store.Operations.Send(...)` returns an `Operation`:
  call `WaitForCompletion()` before reading what it changed (in tests too), which also surfaces script errors.
- Pass values into the `update { ... }` script as query parameters (`IndexQuery.QueryParameters`), never by string
  concatenation.

### Document extensions

- `session.Advanced.Attachments.Get(...)` returns an `AttachmentResult` that holds the open stream: dispose it.
- `session.Advanced.Revisions.GetFor<T>(id)` returns at most 25 revisions unless you pass `start` and `pageSize`. Nothing
  says the list was cut.
- Revision retention is license-capped: a configuration above `MaxNumberOfRevisionsToKeep` or
  `MaxNumberOfRevisionAgeToKeepInDays` is refused with HTTP 402 and
  `Raven.Client.Exceptions.Commercial.LicenseLimitException`. A database-wide `Default` configuration is refused outright
  on an unlicensed server whatever the numbers: configure per collection. Read both caps and
  `CanSetupDefaultRevisionsConfiguration` from `GET /license/status` first (`../version-gate.md`).

### Concurrency

- **(client 7.2.2+)** `session.Advanced.UseOptimisticConcurrency` is `[Obsolete]`: it still compiles, but fails the
  build under `TreatWarningsAsErrors` (`CS0618`). Use `session.Advanced.OptimisticConcurrencyMode =
  OptimisticConcurrencyMode.Writes` (or `WritesAndReads`; default `None`) instead, and never set both on one session:
  that throws. On an older client only the boolean exists, so read the package version first (`../version-gate.md`).

### Facets and advanced queries

- A facet query written as raw RQL runs through `session.Advanced.RawQuery<T>(rql).ExecuteAggregation()`. The ordinary
  result path fails: the server answers "Raw query with aggregation by facet should be called by executeAggregation
  method". The builder form, `query.AggregateBy(...)` or `.AggregateUsing(facetSetupId)`, ends in `Execute()` or
  `ExecuteAsync()`.

## Docs

| You need | `../client-docs.md` topic |
|---|---|
| Which executor runs an operation | Operations: `maintenance`, `maintenance.server`, `operations` |
| Creating, deleting, listing databases; `GetDatabaseRecordOperation` | Creating a database, Deleting a database, Listing databases |
| Subscriptions: create, consume, worker options, `batch.OpenSession()`, list, update, delete | Creating a data subscription, Consuming a data subscription, Subscription worker options, Subscription maintenance |
| Live change notifications | Changes API, Document change notifications |
| `Patch`, `Increment`, `AddOrPatch`, `PatchOperation`, patch by query | Patching one document, Patch by query |
| Attachments | Storing attachments, Loading attachments |
| Counters | Counters, Reading counters |
| Time series | Appending time series entries, Reading time series entries |
| Revisions | Configuring revisions, Loading revisions, Reverting to revisions |
| Cluster-wide sessions, compare exchange | Cluster-wide transactions, Compare exchange, Creating compare-exchange items |
| Optimistic concurrency, how it behaves in a cluster-wide session | Optimistic concurrency |
| Facets, suggestions, more like this, spatial from code | Facets, Suggestions, More like this, Spatial queries; the RQL side is in `../rql-docs.md` |
