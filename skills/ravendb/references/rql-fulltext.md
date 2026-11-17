# RQL: full-text search traps

Syntax for `search()`, `boost()`, `exact()`, `fuzzy()`, `proximity()`, `lucene()`, wildcards, phrases and analyzers: the
text search rows in `rql-docs.md`. These are the parts that parse, run, and return the wrong rows.

- **`search()` and `=` match different things, and both mismatches are silent.** `search()` tokenizes the query and
  needs a field the index stored as analyzed (`Indexing: Search`); `=` and `startsWith()` match the raw value.
  `search()` against a field that is not analyzed returns zero rows, and `=` against one that is matches single tokens
  instead of the whole string. Neither raises. `GET /databases/<db>/indexes?name=<index>` reports the `Indexing` mode
  per field.
- **Terms are OR'ed by default, so two bare words are not a phrase.** `search(Notes, 'raven black')` matches either
  word. Quote inside the string for a phrase: `search(Notes, '"raven black"')` matches the two words adjacent and in
  that order, so `'"black raven"'` is a different query. Pass `and` as the third argument to require every term:
  `search(Notes, 'raven black', and)`. The reverse also happens: one term the analyzer splits, such as
  `sales%representative`, is searched as a phrase.
- **`score()` works only in `order by`.** It is not valid in `select`. Each result's score is in its metadata under
  `@index-score`: project it with `select { Meta: getMetadata(x) }`.
- **The engine is decided per index.** `fuzzy()`, `proximity()` and `lucene()` run only on a Lucene index. Corax, the
  default for new databases since 6.0, rejects each outright with `InvalidQueryException: Method 'Fuzzy' is not
  supported.` One database can hold indexes of both engines, so check the index that will serve the query:
  `GET /databases/<db>/indexes/stats` reports `SearchEngineType` per index. What else Corax does not support: the
  search engine row in `rql-docs.md`.

Suggestions, more-like-this, highlighting and vector search: `rql-docs.md`.
