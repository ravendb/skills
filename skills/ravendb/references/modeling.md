# Document modeling

## Documents and collections

- A document's collection is its `@metadata.@collection`, a label with no schema behind it. Name collections plural PascalCase (`Clients`, `Contracts`).

## Ids

| Form | Meaning |
|---|---|
| `clients/1-A` | Default id (`collection/number-node`) |
| `clients/` suffix | Server assigns the tail on store |
| `clients\|` suffix | Cluster-wide sequential identity |
| `clients/acme` | Semantic id: for a natural key that is stable and known |

Ids are strings, unique across all collections. A known id loads directly with `load()`, no query. Id forms and generation: `client-docs.md` (Document ids).

## Embed or reference

- **Embed** what is owned and always read with the parent (deal → its lines): one load, one write.
- **Reference by id** what lives on its own or is shared (deal → `clientId: "clients/1-A"`). Follow it with `include` or `load` in the same round-trip, never a query per reference: `rql-cheatsheet.md` (include / load), your language's `client.md`.
- Independent children store `parentId` and are queried by it (auto-index), rather than an id array on the parent that grows unbounded.
- Many-to-many: an array of ids on the lighter side (`triggerSignals: ["signals/m-and-a"]`), queried with `where triggerSignals in ('signals/m-and-a')`.
- Counts and sums over many documents belong in a **map-reduce index** (your language's `indexes.md`), not in a document updated on every write. The exception is a value that gates a write: seats against a room's capacity, stock against a reorder floor. Indexes are eventually consistent, so an index total cannot gate a write; keep that counter on the document and defend it with optimistic concurrency (your language's `operations.md`).

## Metadata

`@metadata` carries `@id`, `@collection`, `@change-vector`, `@last-modified`, plus any custom keys. `@change-vector` is the concurrency token: send it back on a write to fail on a conflicting update.
