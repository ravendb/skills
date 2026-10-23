# RQL docs by server version

The last resort, after the `rql-*.md` file for your feature. Replace `<version>` with the server's major.minor, the
`ProductVersion` from `GET /build/version` (`6.2`, `7.1`, `7.2`). Docs for another version describe syntax and behavior
this server may not have. Every link below resolves on 6.2, 7.1 and 7.2; 7.2 redirects some of them into its
reorganized `querying/` section.

## Core RQL

| Topic | URL |
|---|---|
| What RQL is: `from` `where` `group by` `select` `include` `load`, operators, functions | `https://docs.ravendb.net/<version>/client-api/session/querying/what-is-rql` |
| How to query | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-query` |
| Sorting: `order by`, casts, `score()`, `random()`, distance | `https://docs.ravendb.net/<version>/client-api/session/querying/sort-query-results` |
| Projections: `select`, JS projections, `load` | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-project-query-results` |
| `group by` | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-perform-group-by-query` |

## Text search

| Topic | URL |
|---|---|
| Full-text search | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/full-text-search` |
| Boosting | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/boost-search-results` |
| Exact match | `https://docs.ravendb.net/<version>/client-api/session/querying/text-search/exact-match-query` |

## Advanced

| Topic | URL |
|---|---|
| Spatial: `spatial.within` `circle` `wkt` distance | `https://docs.ravendb.net/<version>/indexes/querying/spatial` |
| Time series queries | `https://docs.ravendb.net/<version>/document-extensions/timeseries/querying/overview-and-syntax` |
| Facets | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-perform-a-faceted-search` |
| Suggestions | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-work-with-suggestions` |
| More like this | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-use-morelikethis` |
| Highlighting | `https://docs.ravendb.net/<version>/indexes/querying/highlighting` |
| Vector search (7.0+; 404 on 6.2) | `https://docs.ravendb.net/<version>/ai-integration/vector-search/vector-search-using-dynamic-query/` |

Everything else for that version: `https://docs.ravendb.net/<version>/`.
