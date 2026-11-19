# Testing RavenDB code: .NET

Pick the route in `../testing.md` first.

## Route 1: test driver

NuGet `RavenDB.TestDriver`; derive the test class from `RavenTestDriver`. `GetDocumentStore`, `WaitForIndexing`, `ConfigureServer`, seeding hooks and a full xUnit example: `../client-docs.md` (Test driver). What the page leaves out:

- Each `GetDocumentStore()` call creates a new database, so two calls in one test do not share data.
- The server is a real process started from `RavenDB.Embedded`, so it needs the runtime patch named in `../testing.md`. Point the driver at it:

```csharp
RavenTestDriver.ConfigureServer(new TestServerOptions { DotNetPath = "<dir>/dotnet" });
```

`FrameworkVersion`, which the docs example sets, becomes `--fx-version` and covers only `Microsoft.NETCore.App`: it cannot satisfy the ASP.NET Core half, so it does not fix a too-old runtime.

## Route 2: one server, database per test

`CreateDatabaseOperation` and `DeleteDatabasesOperation` with hard delete: `../client-docs.md` (Creating a database; Deleting a database).

## Route 3: embedded server, driven directly

`EmbeddedServer.Instance.StartServer(...)` and `GetDocumentStore(...)`: `../client-docs.md` (Embedded server). Same runtime pin as Route 1: set `DotNetPath` on its `ServerOptions`, not `FrameworkVersion`.
