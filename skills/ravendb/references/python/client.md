# RavenDB Python client: minimal start and traps

This file holds the minimal start, verbatim, and the traps. Every other call is in the docs, routed through
`../client-docs.md`: read the page as the `.python.md` copy for the server's version. Where `../client-docs.md` lists
no `python` copy, read the C# page for the concept and take the call names from this file or the client's source. A
call this file does not show still exists: check the docs page for your server version before saying it does not.

## Minimal start

```python
from ravendb import DocumentStore

class User:                                     # __init__ keywords = the stored JSON property names
    def __init__(self, name: str = None, status: str = None, age: int = None):
        self.name, self.status, self.age = name, status, age

store = DocumentStore("http://127.0.0.1:8080", "ConsultingDeals")
store.initialize()

with store.open_session() as session:
    session.store(User(name="Acme"))            # id auto: "users/1-A"; the prefix is lower-cased
    session.save_changes()                      # one batch request; nothing hits the server before this

    user = session.load("users/1-A", User)      # the entity, or None

    results = list(
        session.query_collection("Users", User)
        .where_equals("status", "active")
    )

    # RQL text, e.g. copied from Studio or written from ../rql-cheatsheet.md:
    rows = list(session.advanced.raw_query("from users where age > $a", User).add_parameter("a", 18))

# on shutdown:
store.close()
```

- One `DocumentStore` per app; also usable as a context manager (`with DocumentStore(...) as store:`). `initialize()` is mandatory before any use; conventions are frozen at that point.
- A session is a unit of work with an identity map. It holds every document it received in full (`load`, an include, a query without `select_fields`), keyed by id, with a copy of the JSON as it arrived. `save_changes()` diffs the tracked documents against those copies and sends the differences, plus anything stored or deleted, in one batch; nothing else reaches the server. The same id loaded twice in one session hits the cache.
- `query_collection(name, Type)` is a dynamic query (auto index); `query_index("Users/ByName", Type)` targets a static index (`indexes.md`); `session.query(object_type=User)` infers the collection from the class.
- Execute a query by iterating (`list(query)`), or `.first()` / `.single()` / `.count()`.

## Secured server (certificate)

```python
store = DocumentStore("https://a.myapp.ravendb.cloud", "ConsultingDeals")
store.certificate_pem_path = os.environ["RAVENDB_CERT_PEM"]   # cert + key in ONE .pem
store.trust_store_path = os.environ.get("RAVENDB_CA_PEM")     # only for a self-signed CA
store.initialize()
```

- **PEM only**: the setter raises `ValueError` on a `.pfx` path, and also on a PEM missing either the `BEGIN CERTIFICATE` or the `PRIVATE KEY` block, so the certificate and its key must live in the same file. Convert a pfx once: `openssl pkcs12 -in client.pfx -out client.pem -nodes`.
- Both must be set before `initialize()` (`certificate_pem_path` asserts it). URL must be `https://`: the mismatch is rejected by the client at initialization, not by the server. Never commit the pem: take the path from the environment.

## Traps

- `session.query()` takes only `source` and `object_type`. There is no `collection_name` or `index_name` keyword on it, and passing one raises `TypeError: DocumentSession.query() got an unexpected keyword argument`. Name a collection with `query_collection`, an index with `query_index`.
- **Sorting on a number or a date needs the ordering type as a second argument.** `order_by`/`order_by_descending` name the field as a string and default to `OrderingType.STRING`, so `.order_by_descending("amount")` puts `99952` above `243889170`. Pass `OrderingType.FLOAT` for numbers (the member is `FLOAT`, there is no `DOUBLE`), `OrderingType.LONG`, or `OrderingType.ALPHA_NUMERIC`: `.order_by_descending("amount", OrderingType.FLOAT)`. Import it from `ravendb`. This returns wrong rows with no error. Do **not** pass the ordering as a plain string: the second argument is `sorter_name_or_ordering_type`, so `.order_by_descending("amount", "Double")` (the form that is correct in the Node client) is read as the name of a custom sorter and the server answers `NotSupportedInCoraxException: Corax doesn't support Custom OrderBy`.
- `where(name="John", age=3)` sugar exists but joins the kwargs with OR: prefer explicit `where_equals` chains.
- Field names in queries are the literal JSON property names: the client does no case conversion; use exactly what you stored.
- `raw_query` needs `object_type` whenever the RQL projects (`select ...`). Without it the client raises `AttributeError: 'NoneType' object has no attribute '__dict__'` from inside its deserializer, which names neither the query nor the missing argument. `session.advanced.raw_query(rql, dict)` is the general form.
- Without `object_type`, both `load` and queries return a `DynamicStructure`, whose fields are read as **attributes** (`d.Amount`); it is not a dict and subscripting it raises `TypeError: 'DynamicStructure' object is not subscriptable`. Pass `dict` explicitly to get plain dicts, or a class to get instances.
- **Class instances**: collection = pluralized class name (`User` → `Users`, via `inflect`). Deserialization calls `YourClass(**fields)`: the `__init__` keyword args must match the stored JSON property names, or define a `from_json` classmethod. Otherwise the documents fail to deserialize.
- **Plain dicts**: collection is derived from the pluralized document-key prefix (`session.store({...}, "clients/1")` → collection `clients`). A dict stored *without* an explicit key lands in collection `dicts`: always pass an explicit `"collection/..."` id for dicts.
- The identity property is the attribute `Id` (capital I). The client sets it after `store()`; it is not part of the document body. To read the id of a document you **queried** rather than stored, use `session.advanced.get_document_id(entity)`. It works on any tracked entity, including a plain `dict` result, which has no `Id` key of its own. Projections are not tracked, so project `id()` in the query instead.
- Not in the identity map, so not tracked: projections (`select_fields`, `raw_query` with `select`), streams, aggregations, facets. Mutating one and calling `save_changes()` writes nothing and raises nothing; `get_document_id` and `get_metadata_for` cannot see it either. To change documents without loading them in full, patch (`operations.md`).
- `session.include("deal_ids").load("clients/1-A", Client)` returns `{id: entity}`, not the entity: read it as `clients["clients/1-A"]`. A later `session.load(client.deal_ids[0], Deal)` is then served from the session.
- Include paths are resolved on what the query returns. On a projected query the include is silently dropped unless the field it walks is in the projection: `select DealName, AccountId include AccountId` includes the accounts, `select DealName include AccountId` includes nothing and every later load is a request.
- `session.advanced.stream(query)` returns a plain **iterator**, not a context manager, so iterate it directly rather than with `with`. Each item is a `StreamResult` read by attribute (`item.document`, `item.key`, `item.metadata`), not by subscript. Results are not tracked.
- 30 requests per session (`store.conventions.max_number_of_requests_per_session`); exceeding raises. Open a new session instead of raising it. Current count: `session.advanced.number_of_requests`.

## Bulk insert

```python
with store.bulk_insert() as bulk:
    for row in rows:
        bulk.store(entity)                 # returns the assigned key
        bulk.store_as(entity, "deals/7")   # explicit key
```

Streams to the server; far faster than session `store()` loops for seeding. Exiting the `with` block flushes and
finishes the operation; nothing persists before that.

## Staleness

Queries run on indexes that update asynchronously; a query right after `save_changes()` may return stale results. Per
query: `session.query_collection("Users", User).wait_for_non_stale_results(timedelta(seconds=5))`, never on hot
production paths. Waiting for every index at once: the helper in `testing.md`. Test-suite discipline: `../testing.md`; the driver and
per-test database call forms: `testing.md`.

## Docs

| You need | `../client-docs.md` topic |
|---|---|
| Store settings and conventions | Creating the document store; Conventions |
| Explicit ids, the server-assigned tail (`/` suffix), cluster-wide identities (pipe suffix) | Document ids |
| Load several ids, `load_starting_with`, `include` on load | Loading documents, `include` on load |
| `include` on a query | Related documents: `include`, `load` |
| Delete a document | Deleting documents |
| `get_metadata_for` and metadata keys | Metadata |
| A higher request limit | Requests per session limit |
| `where_in`, `where_between`, `where_starts_with`, `where_exists`, `contains_any` | Filtering |
| `or_else`, `not_`, subclauses, `using_default_operator` (before any condition) | Logical operators |
| The query builder as a whole | Document query API |
| A static index | Querying a static index |
| `statistics(callback)`: `total_results`, `is_stale` | Query statistics: total results, staleness |
| `count()`, `first()`, `single()` | Counting results |
| `select_fields` | Projections |
| `distinct()` | Distinct |
| `skip`, `take` | Paging |
| `lazily()` | Lazy queries |
| `search(...)` and `SearchOperator`; sorting | `../rql-docs.md` (Full-text search; Sorting) |
