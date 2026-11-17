# RavenDB indexes from Python: traps

This file holds the traps. Defining, deploying, map-reduce, related documents, analyzers, vector fields and the staleness API are in the docs via `../client-docs.md`: read the `.python.md` copy for the server's version. If the page's header does not list a Python copy, read the C# copy for the concepts and take the call names from this file. A feature this file does not show still exists: check the docs page for your server version before saying it does not.

## Traps

- **Maps are C# LINQ strings, not Python.** The Python client has no Python-syntax index definitions; the map and reduce are strings shipped to the server: `self.map = "from d in docs.Deals select new { d.clientName, d.value }"`. Property names in the string are the stored JSON names, case included. JavaScript-syntax maps also exist (`AbstractJavaScriptIndexCreationTask`, `self.maps`).
- **Query a static index by its `/` name.** The index name is the class name with `_` turned into `/`: class `Deals_ByClientName` deploys as `Deals/ByClientName`. Use `session.query_index("Deals/ByClientName", Deal)` or pass the class, `session.query_index_type(Deals_ByClientName, Deal)`; the `_` spelling names an index that does not exist.
- **Reading a computed field takes two things: store it, and project it.** A field the map computes does not exist on the source document, so `self._store("total", FieldStorage.YES)` plus an explicit `.select_fields(...)` is what makes the server answer from the index; without the store the projection is `None` on every row, silently. Filtering and sorting on the computed field work either way, which is why this reads as a client bug rather than a missing store. Map-reduce indexes are exempt: reduce results always come from the index, stored or not.
- **A stored numeric field comes back from the index as a string** (`"650.0"`, not `650.0`): the store keeps the indexed term, not the JSON type. Cast in the projection class (`float(total)`); formatting it with `:.2f` or doing arithmetic on it raises instead. Map-reduce results keep their numeric type.
- **`=` and `search()` disagree on analyzed fields.** Only fields emitted by the map are queryable. `search()` on a field needs `FieldIndexing.SEARCH` on it, and equality on a Search field matches analyzed terms, not the exact string. RQL side: `../rql-cheatsheet.md`, `../rql-fulltext.md`.
- **Vector fields need the Corax search engine**; Lucene does not support them. Set `self.search_engine_type = SearchEngineType.CORAX` in `__init__`; it applies to that index only.
- **Multi-map indexes drop vector fields silently** `(client 7.2.3)`: `AbstractMultiMapIndexCreationTask.create_index_definition()` does not copy `_vector_indexes_strings` into the definition, so the index deploys without its vector configuration. Override it and set `definition.fields[field].vector` from each entry.
- **The typed vector query** against a static-index field is `.vector_search_with_text_field("NameVector", text, minimum_similarity=0.2)`, which sends raw text for the server to embed.
- **A query right after `save_changes()` can return pre-write results.** Indexes update asynchronously and the response is marked stale, not delayed. Tests and seed scripts that write and then query must wait: `wait_for_indexing` (`testing.md`), or `.wait_for_non_stale_results(timedelta(seconds=5))` on the query. Never wait on hot production paths: it trades latency for consistency, so design UIs to tolerate slightly stale results instead.

## Docs

| You need | `../client-docs.md` topic |
|---|---|
| Auto vs static, when a static index is worth it | What indexes are: auto vs static |
| `AbstractIndexCreationTask`, field options `_index`, `_store`, `_analyze` | Map indexes; Storing fields in the index; Analyzers, full-text fields |
| Deploying: `store.execute_index(task)`, `store.execute_indexes([...])` | Deploying with an operation; Defining and deploying a static index |
| Several collections in one index: `AbstractMultiMapIndexCreationTask`, `_add_map` | Multi-map indexes |
| Map-reduce, `_output_reduce_to_collection` | Map-reduce indexes |
| `LoadDocument` in a map | Indexing related documents: `LoadDocument` |
| Querying a static index | Querying a static index |
| Vector fields: `CreateVector`, `_vector(field, VectorOptions(...))` | Vector search on a static index |
| Waiting for non-stale results per query | Customizing a query: wait for non-stale results, no caching; Stale indexes |
| Polling index statistics | Index statistics, polling for non-stale |

The query side of full-text and vector search, and `group by` without an index: `../rql-docs.md` (Full-text search; Vector search; `group by`).
