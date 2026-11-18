# Raw HTTP API

The request shapes that are easy to get wrong. Base: `http://<host>:<port>/databases/<db>`. Every other endpoint: `GET /debug/routes` lists what the running server has, and `client-docs.md` (HTTP endpoints) describes them.

## Documents

| Call | Shape |
|---|---|
| `GET /docs?id=clients/1-A` | `{ "Results": [ { ...doc, "@metadata": {...} } ] }`; 404 when missing. Repeat `id=` for several ids in one round-trip |
| `PUT /docs?id=clients/1-A` | Body is the document JSON; creates or overwrites. Include `"@metadata": {"@collection": "Clients"}`: without it the write still returns 201 but the document lands in no named collection, so `from Clients` and `/collections/docs?name=Clients` never see it |
| `DELETE /docs?id=clients/1-A` | Deletes |

## Queries (RQL)

```
POST /queries
{ "Query": "from Clients where region = $r limit 25",
  "QueryParameters": { "r": "EU" } }
```

Response: `{ "Results": [...], "TotalResults": n, "IsStale": bool, "IndexName": "..." }`. Page with `limit` in the RQL (`rql-cheatsheet.md`).

Send the body from a file (`curl --data-binary @body.json`), not inline in a shell argument. RQL quotes inside JSON inside shell quotes is where `\x27` appears and the server answers `Invalid escape char, numeric value is 120`. `QueryParameters` keeps literals out of the query text entirely.

## Batch writes

```
POST /bulk_docs
{ "Commands": [
    { "Type": "PUT", "Id": "clients/1-A", "ChangeVector": null, "Document": { ..., "@metadata": { "@collection": "Clients" } } },
    { "Type": "DELETE", "Id": "clients/2-A", "ChangeVector": null } ] }
```

One transaction. `ChangeVector: null` writes unconditionally; a document's current change vector makes the write fail on concurrent modification. A few hundred commands per call suits seeding; larger loads go through the client's bulk insert (`client-docs.md` (Bulk insert)). PATCH, delete-by-prefix and attachment commands: `client-docs.md` (REST API: batch commands).

## Indexes and databases

| Call | Purpose |
|---|---|
| `GET /databases/<db>/stats` | Database exists (non-2xx: missing), document and index counts |
| `GET /databases/<db>/indexes?name=<n>` | One index definition, with each field's `Indexing` mode (decides `=` vs `search()`). Without `?name=`, every static and auto index. `/indexes/<n>` returns `RouteNotFoundException` |
| `DELETE /databases/<db>/indexes?name=<n>` | Delete an index, `Auto/…` included. Not under `admin/`: there is no `admin/indexes` DELETE handler, and asking for one returns `RouteNotFoundException` |
| `PUT /databases/<db>/admin/indexes` | Define a static index: `{"Indexes":[{"Name":"<n>","Maps":["from d in docs.<Collection> select new { … }"],"Fields":{"<field>":{"Indexing":"Search","Storage":"Yes"}}}]}`. The non-admin `/indexes` path rejects a C# map with `UnauthorizedAccessException`. A field the map computes needs `"Storage":"Yes"` to be projectable at all (without it the projection returns `null`), and comes back as a **string** (`"113.598"`): cast before arithmetic |
| `PUT /admin/databases` (server root) | Create database: `{ "DatabaseName": "<db>" }`; an existing name returns 409 `ConcurrencyException` |
| `GET /setup/alive` (server root) | 204 when the server is up: the readiness probe |

## Notes

- Unsecured servers take no auth header; secured servers need the client certificate on the TLS connection, not a header (`client-docs.md` (REST API: cURL and HTTPS)).
- Envelope keys are PascalCase (`Results`, `TotalResults`); document fields keep their stored casing.
