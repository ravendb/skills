# RavenDB .NET client: operations and their traps

Operation traps for the .NET client. The APIs: `../client-docs.md`.

## Traps

### Dispatch

- Create, delete and list databases through `store.Maintenance.Server.Send(...)`; `store.Maintenance.Send(...)` runs
  database-level operations against `store.Database`, `store.Operations.Send(...)` runs data operations such as patches.

### Subscriptions

- **A named subscription is create-once, not upsert.** `Create` with a taken `Name` fails with "already in use in a
  subscription with different Id". Check `GetSubscriptions` first. An unnamed `Create` gets a generated name you cannot
  find again.
- The worker dials the **TCP** port that `GET /info/tcp` advertises, not HTTP. Behind a Docker remap of that port it
  dials the wrong place, and the error names a missing database, not a port: `../install.md` has the fix.
- `worker.Run(...)` returns a `Task` that completes only on a terminal error (`SubscriptionClosedException`,
  `SubscriptionInvalidStateException`, `SubscriptionDoesNotExistException`); transient drops reconnect on their own.
  Awaiting it inline blocks the caller for the worker's whole life.

### Patching

- `PatchByQueryOperation` runs in the background: call `WaitForCompletion()` on the `Operation` that
  `store.Operations.Send(...)` returns before reading results (tests too); it also surfaces script errors.

### Document extensions

- `session.Advanced.Attachments.Get(...)` returns an `AttachmentResult` holding the open stream: dispose it.
- `session.Advanced.Revisions.GetFor<T>(id)` returns at most 25 revisions unless you pass `start` and `pageSize`, and
  nothing says the list was cut.
- Over the revision caps (`../version-gate.md`) the server answers HTTP 402 and the client throws
  `Raven.Client.Exceptions.Commercial.LicenseLimitException`. Unlicensed, a database-wide `Default` configuration is
  refused at any numbers: configure per collection.

### Concurrency

- **(client 7.2.2+)** `session.Advanced.UseOptimisticConcurrency` is `[Obsolete]` and fails a `TreatWarningsAsErrors`
  build (`CS0618`): set `session.Advanced.OptimisticConcurrencyMode = OptimisticConcurrencyMode.Writes` (or
  `WritesAndReads`; default `None`), never both on one session (that throws). Older clients have only the boolean
  (`../version-gate.md`).

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
| Facets, suggestions, more like this, spatial from code | `../rql-docs.md` (Facets; Suggestions; More like this; Spatial on a dynamic query) |
