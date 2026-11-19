# Testing code that talks to RavenDB

Test against a **real server**: id generation, change vectors, index staleness and RQL are what a mocked `IDocumentStore` or session cannot reproduce.

## Pick a route, then read your language's file

| Route | What it is | Available in |
|---|---|---|
| **1: test driver** | Boots an embedded server (a real server process, not in-memory) on first use and hands each test its own fresh database; teardown is automatic. The default where it exists. Needs a matching .NET runtime. | .NET, Python |
| **2: one server, database per test** | A server you run once for the suite (`install.md`), each test creating and hard-deleting its own database. No runtime dependency; the only route for Node.js, and the route when tests must hit the server the app uses. | any language |
| **3: embedded server, driven directly** | The embedded server of Route 1, but you own its lifetime, data directory and settings. | .NET, Python |

Call forms and each driver's traps: `dotnet/testing.md`, `python/testing.md`, `nodejs/testing.md`. Read one.

Give every test its own database: a shared one makes tests order-dependent. The drivers name and delete one per test. A hand-rolled Route 2 names it (`test-<suite>-<n>`), hard-deletes it on teardown, and deletes leftovers at suite start, because a crashed run leaves databases behind.

CI: run the server as a service container (`install.md`), unsecured on localhost, its URL from an env var. Subscription tests also need its TCP port published as the server binds it, or the worker dials another server and reports a missing database (`install.md`).

## Routes 1 and 3: the embedded server pins an exact runtime patch

The embedded package's `RavenDBServer/Raven.Server.runtimeconfig.json` names the `Microsoft.NETCore.App` *and* `Microsoft.AspNetCore.App` versions the server needs. Roll-forward only moves up, so a machine one patch behind fails at first use with `Could not find a matching runtime for '<version>+'`. Read the version from that file, install that ASP.NET Core runtime (`dotnet-install.sh --runtime aspnetcore --version <v> --install-dir <dir>` needs no root) and point the driver at `<dir>/dotnet` (call form in your language's file), or use a CI image that has it. No matching runtime at all: Route 2.

## Staleness is the #1 test flake

Every write-then-query test must wait for indexing (why: `rql-cheatsheet.md`): the driver's wait-for-indexing helper, the polling helper in your language's file, or the per-query wait in its `client.md`. A test that passes locally and fails in CI under load is almost always a missing wait. Loading by id needs no wait: only queries go through indexes.

To *prove* the stale window, do not rely on losing the race: on a local server the index often catches up before the query. Pause indexing with `StopIndexingOperation` (a database maintenance operation, same name in each client), write, query (now deterministically stale), then `StartIndexingOperation` and wait. Calls: `client-docs.md` (Pausing indexing).
