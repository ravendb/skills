# RQL docs by server version

Where RQL syntax lives: the skill keeps the traps (`rql-cheatsheet.md`, `rql-fulltext.md`, `rql-timeseries.md`), and
the docs page below holds the syntax, options and examples.

Replace `<version>` with the server's major.minor and read each page as "Official docs" in `SKILL.md` describes.

## Core RQL

| Topic | URL |
|---|---|
| What RQL is: `from` `where` `group by` `select` `include` `load`, operators, functions | `https://docs.ravendb.net/<version>/querying/rql/what-is-rql` |
| Filtering: `where`, nested fields, `in`, `all in`, prefixes | `https://docs.ravendb.net/<version>/querying/filtering-query-results/filter-query-results` |
| Sorting: `order by`, casts, `score()`, `random()`, distance | `https://docs.ravendb.net/<version>/querying/sorting-query-results/sort-query-results` |
| Dates: `now()`, `today()`, offsets | `https://docs.ravendb.net/<version>/querying/filtering-query-results/filter-by-date-and-time` |
| Projections: `select`, JS projections, `load` | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-project-query-results` |
| `group by` | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-perform-group-by-query` |
| Paging: `limit`, `offset` | `https://docs.ravendb.net/<version>/indexes/querying/paging` |
| Field presence: `exists()` | `https://docs.ravendb.net/<version>/querying/filtering-query-results/filter-by-field-presence` |
| `intersect()` | `https://docs.ravendb.net/<version>/indexes/querying/intersection` |
| `cmpxchg()` in queries | `https://docs.ravendb.net/<version>/compare-exchange/cmpxchg-in-dynamic-queries` |
| Scoring explanations: `include explanations()` | `https://docs.ravendb.net/<version>/client-api/session/querying/debugging/include-explanations` |
| Query timings: `include timings()` | `https://docs.ravendb.net/<version>/client-api/session/querying/debugging/query-timings` |
| Including counters: `include counters()` | `https://docs.ravendb.net/<version>/document-extensions/counters/including-counters` |
| Including revisions: `include revisions()` | `https://docs.ravendb.net/<version>/document-extensions/revisions/client-api/session/including` |
| Including time series: `include timeseries()` | `https://docs.ravendb.net/<version>/document-extensions/timeseries/client-api/session/include/with-raw-queries` |

## Text search

| Topic | URL |
|---|---|
| Full-text search | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/full-text-search` |
| Boosting | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/boost-search-results` |
| Exact match | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/exact-match-query` |
| Prefix: `startsWith()` | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/starts-with-query` |
| Suffix: `endsWith()` | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/ends-with-query` |
| `regex()` | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/using-regex` |
| Fuzzy: `fuzzy()`, Lucene indexes only | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/fuzzy-search` |
| Proximity: `proximity()`, Lucene indexes only | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/proximity-search` |
| Lucene syntax: `lucene()` | `https://docs.ravendb.net/<version>/querying/filtering-query-results/filter-with-lucene-syntax` |
| Search engine: Corax vs Lucene, what Corax does not support | `https://docs.ravendb.net/<version>/indexes/search-engine/corax` |
| Highlighting on a dynamic query | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/highlight-query-results` |

## Advanced

| Topic | URL |
|---|---|
| Spatial: `spatial.within` `circle` `wkt` distance | `https://docs.ravendb.net/<version>/indexes/querying/spatial` |
| Spatial on a dynamic query: shapes, relations, units, distance rounding | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-make-a-spatial-query` |
| Spatial indexing: spatial fields in a static index | `https://docs.ravendb.net/<version>/indexes/indexing-spatial-data` |
| Time series queries | `https://docs.ravendb.net/<version>/document-extensions/timeseries/querying/overview-and-syntax` |
| Time series range: `between`, `first`, `last`, `offset` | `https://docs.ravendb.net/<version>/document-extensions/timeseries/querying/choosing-query-range` |
| Time series filtering: `where` on values and tags | `https://docs.ravendb.net/<version>/document-extensions/timeseries/querying/filtering` |
| Time series aggregation: `group by` buckets, aggregation functions | `https://docs.ravendb.net/<version>/document-extensions/timeseries/querying/aggregation-and-projections` |
| Indexing time series, to filter documents by series values | `https://docs.ravendb.net/<version>/document-extensions/timeseries/indexing` |
| Indexing counters, to filter documents by counter values | `https://docs.ravendb.net/<version>/document-extensions/counters/indexing` |
| Facets: value and range facets, aggregations, options, `FacetSetup` | `https://docs.ravendb.net/<version>/indexes/querying/faceted-search` |
| Suggestions | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-work-with-suggestions` |
| Suggestions on a static index: full page, options | `https://docs.ravendb.net/<version>/indexes/querying/suggestions` |
| More like this | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-use-morelikethis` |
| More like this: index setup, options | `https://docs.ravendb.net/<version>/indexes/querying/morelikethis` |
| Highlighting | `https://docs.ravendb.net/<version>/indexes/querying/highlighting` |
| Vector search | `https://docs.ravendb.net/<version>/ai-integration/vector-search/vector-search-using-dynamic-query` |

Everything else for that version starts at `https://docs.ravendb.net/<version>` (no trailing slash).
