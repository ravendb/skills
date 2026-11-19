# RavenDB indexes from Python: traps

Index traps for the Python client. Defining, deploying and querying indexes: `../client-docs.md`.

## Traps

- **Maps are C# LINQ strings, not Python**: `self.map = "from d in docs.Deals select new { d.clientName, d.value }"`, with the stored JSON property names, case included. JavaScript maps also exist (`AbstractJavaScriptIndexCreationTask`, `self.maps`).
- **Query a static index by its `/` name**: class `Deals_ByClientName` deploys as `Deals/ByClientName`, and the `_` spelling names no index. Use `session.query_index("Deals/ByClientName", Deal)` or `session.query_index_type(Deals_ByClientName, Deal)`.
- **A computed field reads back only when stored and projected.** Projecting it with `.select_fields(...)` returns `None` on every row, silently, until the index has `self._store("total", FieldStorage.YES)`, though filtering and sorting on it work. Map-reduce indexes are exempt.
- **A stored numeric field reads back as a string** (`"650.0"`): cast it in the projection class (`float(total)`), or `:.2f` and arithmetic raise. Map-reduce results keep their numeric type.
- **`search()` needs the field indexed as `FieldIndexing.SEARCH`**, and only fields the map emits are queryable. What `=` and `search()` then match: `../rql-cheatsheet.md`.
- **Vector fields need the Corax search engine** (Lucene lacks them): set `self.search_engine_type = SearchEngineType.CORAX` in `__init__`, per index.
- **Multi-map indexes drop vector fields silently** `(client 7.2.3)`: `AbstractMultiMapIndexCreationTask.create_index_definition()` does not copy `_vector_indexes_strings` into the definition. Override it and set `definition.fields[field].vector` from each entry.
- **The typed vector query** on a static-index field is `.vector_search_with_text_field("NameVector", text, minimum_similarity=0.2)`; it sends raw text for the server to embed.

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
