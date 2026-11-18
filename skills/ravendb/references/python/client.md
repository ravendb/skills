# RavenDB Python client: minimal start and traps

Minimal start and traps for the Python client. Every other call: `../client-docs.md`.

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

- The session tracks every document it receives in full (`load`, an include, a query without `select_fields`): `save_changes()` sends their changes, plus stores and deletes, in one batch. Loading an id again is served from the session.

## Secured server (certificate)

```python
store = DocumentStore("https://a.myapp.ravendb.cloud", "ConsultingDeals")
store.certificate_pem_path = os.environ["RAVENDB_CERT_PEM"]   # cert + key in ONE .pem
store.trust_store_path = os.environ.get("RAVENDB_CA_PEM")     # only for a self-signed CA
store.initialize()
```

- **PEM only, certificate and key in one file**: the setter raises `ValueError` on a `.pfx` path, or on a PEM missing the `BEGIN CERTIFICATE` or `PRIVATE KEY` block. Convert once: `openssl pkcs12 -in client.pfx -out client.pem -nodes`.
- Set both before `initialize()` (`certificate_pem_path` asserts it).

## Traps

- `session.query(object_type=User)` infers the collection from the class and takes only `source` and `object_type`: a `collection_name` or `index_name` keyword raises `TypeError: DocumentSession.query() got an unexpected keyword argument`. Use `query_collection` or `query_index` (`indexes.md`).
- **Numeric and date sorts need an `OrderingType`.** `order_by`/`order_by_descending` default to `OrderingType.STRING`, so `.order_by_descending("amount")` puts `99952` above `243889170`, silently. Pass `OrderingType.FLOAT` (no `DOUBLE`), `OrderingType.LONG` or `OrderingType.ALPHA_NUMERIC`, from `ravendb`: `.order_by_descending("amount", OrderingType.FLOAT)`. A string there is a custom sorter name (`sorter_name_or_ordering_type`): `.order_by_descending("amount", "Double")` (the Node form) fails with `NotSupportedInCoraxException: Corax doesn't support Custom OrderBy`.
- `where(name="John", age=3)` joins its kwargs with OR: chain `where_equals` instead.
- A projecting `raw_query` (`select ...`) without `object_type` raises `AttributeError: 'NoneType' object has no attribute '__dict__'` from the deserializer, naming neither the query nor the argument. Pass a class or `dict`: `session.advanced.raw_query(rql, dict)`.
- Without `object_type`, `load` and queries return a `DynamicStructure`: read fields as attributes (`d.Amount`); subscripting raises `TypeError: 'DynamicStructure' object is not subscriptable`. Pass `dict` for plain dicts, or a class.
- **Class instances**: the collection is the pluralized class name (`User` → `Users`, via `inflect`). Deserialization calls `YourClass(**fields)`, so documents fail to deserialize unless the `__init__` keywords match the stored JSON names or the class defines a `from_json` classmethod.
- **Plain dicts**: the collection comes from the pluralized id prefix (`session.store({...}, "clients/1")` → `clients`); a dict stored without an id lands in `dicts`. Always pass a `"collection/..."` id.
- The id is the attribute `Id` (capital I), set by `store()`; the document body does not hold it. For a queried entity, `dict` results included (no `Id` key), use `session.advanced.get_document_id(entity)`; for a projection (untracked), project `id()`.
- Not tracked: projections (`select_fields`, `raw_query` with `select`), streams, aggregations, facets. Changing one and calling `save_changes()` writes nothing, silently, and `get_document_id`/`get_metadata_for` cannot see it. To change documents without loading them in full, patch (`operations.md`).
- `session.include("deal_ids").load("clients/1-A", Client)` returns `{id: entity}`, not the entity: read `clients["clients/1-A"]`.
- `session.advanced.stream(query)` returns a plain iterator, not a context manager: iterate it without `with`. Each item is a `StreamResult` read by attribute (`item.document`, `item.key`, `item.metadata`), not by subscript.
- 30 requests per session (`store.conventions.max_number_of_requests_per_session`), then it raises: open a new session rather than raising the limit. Current count: `session.advanced.number_of_requests`.

## Bulk insert

```python
with store.bulk_insert() as bulk:
    for row in rows:
        bulk.store(entity)                 # returns the assigned key
        bulk.store_as(entity, "deals/7")   # explicit key
```

Exiting the `with` block flushes and finishes the operation; nothing persists before that. Other calls:
`../client-docs.md` (Bulk insert).

## Staleness

Per query: `session.query_collection("Users", User).wait_for_non_stale_results(timedelta(seconds=5))`. Every index at
once: the helper in `testing.md`.

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
| `where_in`, `where_between`, `where_starts_with`, `where_exists`, `contains_any` | `../rql-docs.md` (Filtering) |
| `or_else`, `not_`, subclauses, `using_default_operator` (before any condition) | Logical operators |
| The query builder as a whole | Document query API |
| A static index | Querying a static index |
| `statistics(callback)`: `total_results`, `is_stale` | Query statistics: total results, staleness |
| `count()`, `first()`, `single()` | Counting results |
| `select_fields` | `../rql-docs.md` (Projections) |
| `distinct()` | Distinct |
| `skip`, `take` | `../rql-docs.md` (Paging) |
| `lazily()` | Lazy queries |
| `search(...)` and `SearchOperator`; sorting | `../rql-docs.md` (Full-text search; Sorting) |
