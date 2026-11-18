# RQL cheat-sheet

Minimal syntax, and the traps that parse and then return the wrong rows. Signatures and options: `rql-docs.md`.

## Before you filter, look at one document

Run `from <Collection> limit 1` (it creates no index) and filter only on field names you saw in it. Field names are case-sensitive: a wrong one in `where` on a collection is no error, it returns no rows and leaves an auto-index on the wrong name (`where company = …` against `Company` creates `Auto/Orders/Bycompany`); against an index that stored `Type`, `type` is a hard error. Values are not: `where Stage = 'closed won'` matches `'Closed Won'`.

| You reach RavenDB through | Run it with |
|---|---|
| Raw HTTP | `POST /databases/<db>/queries` with `{ "Query": "from Orders limit 1" }` (`http-api.md`) |
| A client library | `RawQuery` (.NET), `rawQuery` (Node.js) or `raw_query` (Python), in your language's `client.md` |
| The RavenDB MCP server | its `run_query` tool |

## Clause order
```
declare <fn>
from <source> [as alias]
[ group by <fields> ]
[ where <predicate> ]
[ order by <field> [as <type>] [asc|desc] ]
[ load <ref> as x ]
[ filter <predicate> ]
[ select <projection> ]
[ include <related> ]
[ limit <skip>, <take> | limit <take> offset <skip> ]
[ filter_limit <n> ]
```
Each clause appears **at most once**. `where` runs against the index before `load` resolves anything, so a condition on a loaded document goes in `filter`, not a second `where`. Strings `'…'` or `"…"`, parameters `$name`, comments `// line` and `/* block */`.

## from
```
from Users                     # collection
from "Order Lines"             # quoted name
from @all_docs                 # every document
from index 'Orders/Totals'     # named static index
from Users as u                # alias (needed for load / JS projections)
```

## where
```
where Age > 30 and IsActive = true          # = == , != <>, < <= > >=
where Address.City = 'Albuquerque'          # nested path via dot
where Age between 18 and 65
where Country in ('US','UK')                # any listed value
where Lines[].Sku all in ('A','B')          # array field: all listed present
where startsWith(Name,'Jo')  where endsWith(Email,'@acme.com')
where exists(MiddleName)                    # anchor optional fields
where regex(Sku,'^A-\d+$')
where search(Bio,'raven database')          # full-text: rql-fulltext.md
where id() = 'users/1-A'                    # id() or id(alias)
where boost(Name = 'Bob', 10)
```
`not` cannot start a `where`: write `exists(X) and not X in (…)`.

## order by
```
order by Name                                        # default asc, lexical
order by Amount as double desc                       # cast numbers/dates (long|double), else lexical; also string|alphaNumeric
order by UnitsInStock as long desc, score(), Name    # chained (Corax: max 16)
order by score()  |  random()  |  random(1234)       # relevance / random / seeded
order by custom(Field,'MySorter')                    # Lucene engine only
```

## select (projection): applied last, results not session-tracked
```
select Name, Address.City as City         # fields + aliases
select id() as Id                         # the source document's id
select distinct Country
select { Name: x.FirstName + ' ' + x.LastName, Meta: getMetadata(x) }   # JS object, needs from … as x
```
- `id()` in `select` takes no argument and returns the source document's id: `select id(d)` or `select id(a)` fails with `id(doc) must be called with an object argument`, whether `d` came from `from … as d` or `a` from `load … as a`. A loaded document's id is the field you loaded through (`AccountId` after `load AccountId as a`); `a.Id` returns 200 with the field silently missing.
- A computed value (`Price * 0.9`, a date part, a JS expression) cannot be filtered or sorted on: `select` runs last, and `where` has no math or date operators. Compute it as a field in a static index map (`DiscountedPrice = p.Price * 0.9`) and query that index.
- `include` resolves on the projection: `select DealName include AccountId` silently includes nothing. Project the field it walks (`select DealName, AccountId include AccountId`), or do not project.

## group by / aggregation

**`group by` comes before `where`, the reverse of SQL:** `from Deals group by Stage where Stage = 'Closed Won'`; the SQL order fails with `Expected end of query but got: group`. That `where` takes only the group key. Anything else, an aggregate too (`where count() = 3`), fails with `Field '...' is neither an aggregation operation nor part of the group by key` (the Python client shows only the status 500): to filter groups by an aggregate, fetch all groups (`select key(), count()`) and filter client-side, or use a map-reduce index.

```
from Orders
group by ShipTo.City
select ShipTo.City as City, count() as N, sum(Amount) as Total
```
Dynamic `group by` has **only `count()` and `sum()`**; avg/min/max fail (use a facet, a map-reduce index or a JS projection). `group by array(Tags)` keys on the whole array, `key()` returns the key, `order by count() as long` sorts by an aggregate. It creates an `Auto/…` index, and runs on a collection only: `from index 'X' group by …` is rejected, because an aggregating index must already be map-reduce.

**On a named index, aggregate with a facet.** The aggregates are **arguments to `facet(...)`, not a block**:
```
from index 'Deals/ByAccount' where Stage = 'Closed Won' select facet(Stage, sum(Amount), avg(Amount))
```
`select facet() { sum(Amount) }` does not parse; a bare `select sum(Amount)` fails with `sum may only be used in group by queries`. Bucket keys come back as lowercased index terms. `facet(...)` and `morelikethis(...)` need `from index '…'`, never `from Collection` (`suggest()` and `highlight()` also run on dynamic queries). Options and range facets: `rql-docs.md` (Facets).

**Through a client, a facet query needs the aggregation call:** `ExecuteAggregation()` (.NET), `executeAggregation()` (Node.js), `execute_aggregation()` (Python). The ordinary call fails with `Raw query with aggregation by facet should be called by executeAggregation method`; in .NET it does not compile, as `IRawDocumentQuery<T>` has no `ToFacets`.

## include / load (avoid N+1)
```
from Orders as o load o.CustomerId as c select c.Name
include CustomerId, Lines[].ProductId       # related docs, one round-trip
include counters(o,'Views')
include timeseries('HeartRate', $from, $to)
include revisions('2026-02-23T07:40:54Z')
```

## filter (post-index scan)
`filter` scans the rows `where` returned, server-side, for checks the index cannot answer. `filter_limit <n>` caps the scan and goes last: `filter … select … filter_limit 2000` parses, `filter … filter_limit 2000 select …` does not.

`TotalResults` is wrong under `filter`: an index query reports the pre-filter total, a dynamic query only the matches in the window scanned so far (with `limit 5`, 5 whatever the real total).

## paging
```
limit 25            # take 25
limit 50, 25        # skip 50, take 25
limit 25 offset 50  # take 25, skip 50
```

## Counting

The wrong route returns a wrong number, not an error.
- Collection or index query: `limit 0`, read `TotalResults`.
- `group by`: `count()`. `select count()` anywhere else fails, **including inside `facet(...)`**.
- Facet: read each bucket's `Count`.
- `select distinct`: count the rows; `TotalResults` counts before deduplication (8 distinct stages, `TotalResults` 1200). Distinct values under a filter on another field: `from Deals where Stage = 'Closed Won' select distinct AccountId`.
- **`filter`: count the rows of a full (or `filter_limit`-bounded) result.** `limit 0` reports the wrong `TotalResults` (above) and returns no rows to notice it by.

## spatial
```
where spatial.within(spatial.point(Lat, Lng), spatial.circle(5, 40.7128, -74.0060))   # 5 km
order by spatial.distance(spatial.point(Lat, Lng), spatial.point(40.7128, -74.0060))
```
- **Coordinate order flips between forms.** `spatial.point(lat, lng)` and `spatial.circle(radius, lat, lng)` take latitude first; WKT is `x y`, longitude first: `spatial.wkt('POLYGON((-74.1 40.6, -73.9 40.6, -73.9 40.8, -74.1 40.8, -74.1 40.6))')`. Swapped coordinates return the wrong rows.
- **The third argument of `spatial.distance(field, point, x)` rounds the distance**, grouping nearby results; it is not a unit. Units are kilometers unless the shape passes `'miles'`: `spatial.circle(5, 40.7128, -74.0060, 'miles')`.

## Coming from SQL

These have no RQL equivalent; most fail with a parse error that does not name the replacement.

| SQL | RQL |
|---|---|
| `count(*)` | `count()`, only in `group by` (Counting, above) |
| `sum(x)` on its own | `group by`, a map-reduce index, or a facet |
| `like '%x%'` | `startsWith` / `endsWith`, or `search()` on an analyzed field |
| `is null` / `is not null` | `where x = null` / `where exists(x)` |
| `now() - interval '30 days'` | `rql-docs.md` (Dates) |
| `join` | `load` (projection) or `include` (one round-trip) |
| `update t set c = v` | `from t where ... update { ... }`, a write, on a different endpoint |

Two that return wrong rows instead of failing:
- Quoting a number makes the comparison lexical: `where Amount > '10000'` matches almost everything.
- On a field indexed as analyzed (`Indexing: Search`), `=` matches single tokens, not the whole string: `where Name = 'Acme Data Group'` finds nothing, while `search(Name, 'Acme Data Group')` ORs the terms and floods (phrases: `rql-fulltext.md`). `debug=entries` in `diagnostics.md` shows what the index stored.

## Stale reads

Queries are not read-your-writes: indexes update asynchronously, so a query right after a write can miss it, and the only sign is `IsStale: true` in the response (`diagnostics.md`). Wait for non-stale results in tests and seed scripts, never on hot production paths; the per-query wait call is in your language's `client.md`.

Next: full-text traps in `rql-fulltext.md`, time series traps in `rql-timeseries.md`, everything else in `rql-docs.md`.
