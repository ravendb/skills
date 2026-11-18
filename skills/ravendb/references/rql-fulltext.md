# RQL: full-text search traps

Syntax for `search()`, `boost()`, `exact()`, `fuzzy()`, `proximity()`, `lucene()`, wildcards, phrases and analyzers: the
Text search rows in `rql-docs.md`. These parse, run, and return the wrong rows.

- **Terms are OR'ed, so two bare words are not a phrase.** `search(Notes, 'raven black')` matches either word. For a
  phrase, quote inside the string: `search(Notes, '"raven black"')` matches the words adjacent and in that order, so
  `'"black raven"'` is a different query. To require every term, pass `and`: `search(Notes, 'raven black', and)`.
  Conversely, one term the analyzer splits, such as `sales%representative`, is searched as a phrase.
- **`score()` works only in `order by`,** not in `select`. The score is in each result's metadata as `@index-score`:
  project it with `select { Meta: getMetadata(x) }`.
- **The engine is decided per index.** `fuzzy()`, `proximity()` and `lucene()` run only on a Lucene index. Corax, the
  default for new databases, rejects each with `InvalidQueryException: Method 'Fuzzy' is not supported.` Check the
  index that serves the query: `GET /databases/<db>/indexes/stats` reports `SearchEngineType` per index. What else
  Corax does not support: `rql-docs.md` (Search engine).
