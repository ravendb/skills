# RQL: time series traps

Syntax for `select timeseries(...)`, `declare timeseries`, ranges, filters, time buckets, `scale`, `offset` and the
aggregation functions: the time series rows in `rql-docs.md`. These are the parts that fail without naming the fix, or
return something other than what the query asked for.

- **The range is a clause, not a function.** `between … and …`, `first <n> <unit>` and `last <n> <unit>` go right after
  `from` inside the `timeseries(...)` block or the `declare timeseries` body: never in `where`, never called like
  `last(...)`. A range takes one form: `first` or `last` cannot be combined with `between`.
  ```
  from Employees as e
  select timeseries(from e.HeartRates last 30 min)
  ```
- **Aggregates come back under other names, as arrays.** Each bucket is `{From, To, Key, Count, Min, Max, Average,
  First, Last}`: `avg()` reads back as `Average`, and every aggregate is an array with one element per value column, so
  a single-value series is `Average[0]`. Reading `Avg` or `avg` gives `undefined`/`None`, which looks like a broken
  query rather than a wrong field name.
- **`where` on the document cannot see time series or counter values,** and `include timeseries(...)` /
  `include counters(...)` only side-load them onto rows already selected. To filter or sort documents by those values,
  query a time series or counters index: the indexing rows in `rql-docs.md`.
