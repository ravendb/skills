# Testing RavenDB code: Python

Pick the route in `../testing.md` first.

## Route 1: test driver

```python
# pip install ravendb-test-driver
from ravendb_test_driver import RavenTestDriver

class TestDeals(TestCase):
    def setUp(self):
        self.driver = RavenTestDriver()

    def tearDown(self):
        self.driver.close()

    def test_won_deals(self):
        with self.driver.get_document_store() as store:
            with store.open_session() as session:
                session.store({"Status": "won", "collection": "Deals"})
                session.save_changes()
            RavenTestDriver.wait_for_indexing(store)
```

- Each `get_document_store()` call creates a new database: nothing leaks between tests, no cleanup code.
- Override `setup_database` to seed or configure (revisions, say) each database once.
- `wait_for_indexing` and `configure_server` are `@staticmethod`s on `RavenTestDriver`. Calling them on an instance works but implies per-instance state that does not exist.
- `configure_server(options)` must run before the first `get_document_store()`; after that the server is up and it throws.
- The store the driver returns is already initialized, so its conventions are frozen (`operations.md`). Anything that must be set before `initialize()` needs a store you construct yourself.

The server is a real process started from `ravendb-embedded`, so it needs the runtime patch named in `../testing.md`. Point the driver at it:

```python
from ravendb_embedded import ServerOptions
from ravendb_test_driver import RavenTestDriver

options = ServerOptions()
options.dot_net_path = "<dir>/dotnet"
RavenTestDriver.configure_server(options)
```

`framework_version` on the same options becomes `--fx-version`, which covers only `Microsoft.NETCore.App`: it cannot satisfy the ASP.NET Core half, so it does not fix a too-old runtime.

## Route 2: one server, database per test

Easiest form: the driver against a server you already run. It still names and hard-deletes a database per test, with no embedded boot and no .NET needed. Call it before the first `get_document_store()`:

```python
RavenTestDriver.configure_external_server(url, certificate_pem_path=None, trust_store_path=None)
```

Env vars instead: `RAVENDB_TEST_SERVER_URL` / `_CERT` / `_CA`. Hand-roll it (`CreateDatabaseOperation` / `DeleteDatabaseOperation` from `operations.md`) when the suite must control the names or the database record.

## Route 3: embedded server, driven directly

```python
from ravendb_embedded import EmbeddedServer, ServerOptions

options = ServerOptions()
options.data_directory = temp_dir
options.server_url = "http://127.0.0.1:38712"   # omit and the server picks a free port
server = EmbeddedServer()          # not enforced as a singleton: hold this instance, a second one has no server
server.start_server(options)
store = server.get_document_store("Tests")      # creates the database too
try:
    server.close()
except RuntimeError:
    pass                            # the server process is already down: see close() below
```

- `get_document_store(name)` **creates the database** unless you pass `DatabaseOptions` with `skip_creating_database = True` via `get_document_store_from_options`, so a following `CreateDatabaseOperation` is redundant.
- `close()` kills the server process, then raises `RuntimeError: dictionary changed size during iteration` while closing the stores it tracks (ravendb-embedded 7.2.5.post1). The shutdown succeeded; catch it rather than failing the teardown.
- No public accessor for the server's pid: to assert the process is gone, check the port or the process table.
- `open_studio_in_browser()` opens Studio on the server.

## Waiting for indexing without the driver

Hand-rolled Route 2, Route 3 or a seed script has no `wait_for_indexing`. After a bulk seed or an index deploy, poll the database statistics:

```python
import time
from ravendb import GetStatisticsOperation
from ravendb.documents.indexes.definitions import IndexState

def wait_for_indexing(store):
    while True:
        stats = store.maintenance.send(GetStatisticsOperation())
        indexes = [i for i in stats.indexes if i.state != IndexState.DISABLED]
        if all(not i.stale for i in indexes):
            return
        time.sleep(0.1)
```

Skip disabled indexes or the wait never returns. `i.state` is an `IndexState` enum, so compare it to `IndexState.DISABLED`, not to a string: an enum never equals a string, and the filter would keep every index.
