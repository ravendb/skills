# RQL: time series traps

Syntax for `select timeseries(...)`, `declare timeseries`, ranges, filters, time buckets, `scale`, `offset` and the
aggregation functions: the Time series rows in `rql-docs.md`. These traps fail without naming the fix, or return
something other than what the query asked for.

- **The range is a clause, not a function.** `between … and …`, `first <n> <unit>` or `last <n> <unit>` goes right
  after `from` inside `timeseries(...)` or the `declare timeseries` body: not in `where`, not as `last(...)`. Pick one
  form: `first` or `last` cannot be combined with `between`.
  ```
  from Employees as e
  select timeseries(from e.HeartRates last 30 min)
  ```
- **Aggregates come back renamed, as arrays.** Each bucket is `{From, To, Key, Count, Min, Max, Average, First, Last}`:
  `avg()` reads back as `Average`, and every aggregate is an array with one element per value column, so a
  single-value series reads `Average[0]`. `Avg` or `avg` reads as `undefined`/`None`, which looks like a broken query.
- **Document `where` cannot see time series or counter values,** and `include timeseries(...)` /
  `include counters(...)` only side-load them onto selected rows. To filter or sort documents by them, query a time
  series or counters index: `rql-docs.md` (Indexing time series; Indexing counters).
