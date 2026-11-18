# Client API docs by topic

Docs pages by topic for everything outside RQL: client calls, install and setup, testing, diagnostics and AI agents.
Replace `<version>` with the server's major.minor and read each page as "Official docs" in `SKILL.md` describes.

## Store and session

| Topic | URL |
|---|---|
| Getting started: store, session, store, load, query | `https://docs.ravendb.net/<version>/start/getting-started` |
| Creating the document store | `https://docs.ravendb.net/<version>/client-api/creating-document-store` |
| Conventions | `https://docs.ravendb.net/<version>/client-api/configuration/conventions` |
| Secured server: client certificate | `https://docs.ravendb.net/<version>/client-api/setting-up-authentication-and-authorization` |
| Opening a session | `https://docs.ravendb.net/<version>/client-api/session/opening-a-session` |
| Loading documents, `include` on load | `https://docs.ravendb.net/<version>/client-api/session/loading-entities` |
| Storing documents | `https://docs.ravendb.net/<version>/client-api/session/storing-entities` |
| Saving changes | `https://docs.ravendb.net/<version>/client-api/session/saving-changes` |
| Deleting documents | `https://docs.ravendb.net/<version>/client-api/session/deleting-entities` |
| Document ids | `https://docs.ravendb.net/<version>/client-api/document-identifiers/working-with-document-identifiers` |
| Metadata | `https://docs.ravendb.net/<version>/client-api/session/how-to/get-and-modify-entity-metadata` |
| Requests per session limit | `https://docs.ravendb.net/<version>/client-api/session/configuration/how-to-change-maximum-number-of-requests-per-session` |
| Related documents: `include`, `load` | `https://docs.ravendb.net/<version>/client-api/how-to/handle-document-relationships` |
| Bulk insert | `https://docs.ravendb.net/<version>/client-api/bulk-insert/how-to-work-with-bulk-insert-operation` |
| Storing dates | `https://docs.ravendb.net/<version>/client-api/how-to/store-dates` |
| Optimistic concurrency | `https://docs.ravendb.net/<version>/client-api/session/configuration/how-to-enable-optimistic-concurrency` |

## Querying from code

| Topic | URL |
|---|---|
| Query overview, raw RQL queries | `https://docs.ravendb.net/<version>/querying/overview` |
| Logical operators | `https://docs.ravendb.net/<version>/querying/filtering-query-results/use-logical-operators` |
| Document query API | `https://docs.ravendb.net/<version>/querying/document-query/what-is-document-query` |
| Customizing a query: wait for non-stale results, no caching | `https://docs.ravendb.net/<version>/querying/customize-query` |
| Querying a static index | `https://docs.ravendb.net/<version>/indexes/querying/query-index` |
| Query statistics: total results, staleness | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-get-query-statistics` |
| Counting results | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-count-query-results` |
| Distinct | `https://docs.ravendb.net/<version>/indexes/querying/distinct` |
| Lazy queries | `https://docs.ravendb.net/<version>/client-api/session/querying/how-to-perform-queries-lazily` |
| Streaming results | `https://docs.ravendb.net/<version>/querying/stream-query-results` |

## Indexes

| Topic | URL |
|---|---|
| What indexes are: auto vs static | `https://docs.ravendb.net/<version>/indexes/what-are-indexes` |
| Defining and deploying a static index | `https://docs.ravendb.net/<version>/indexes/creating-and-deploying` |
| Map indexes | `https://docs.ravendb.net/<version>/indexes/map-indexes` |
| Multi-map indexes | `https://docs.ravendb.net/<version>/indexes/multi-map-indexes` |
| Map-reduce indexes | `https://docs.ravendb.net/<version>/indexes/map-reduce-indexes` |
| Indexing related documents: `LoadDocument` | `https://docs.ravendb.net/<version>/indexes/indexing-related-documents` |
| Storing fields in the index | `https://docs.ravendb.net/<version>/indexes/storing-data-in-index` |
| Analyzers, full-text fields | `https://docs.ravendb.net/<version>/indexes/using-analyzers` |
| Deploying with an operation | `https://docs.ravendb.net/<version>/client-api/operations/maintenance/indexes/put-indexes` |
| Rolling and side-by-side deployment | `https://docs.ravendb.net/<version>/indexes/rolling-index-deployment` |
| Stale indexes | `https://docs.ravendb.net/<version>/indexes/stale-indexes` |
| Index statistics, polling for non-stale | `https://docs.ravendb.net/<version>/monitoring/statistics/client-api` |
| Vector search on a static index | `https://docs.ravendb.net/<version>/ai-integration/vector-search/vector-search-using-static-index` |
| Test driver | `https://docs.ravendb.net/<version>/start/test-driver` |

## Operations and document extensions

| Topic | URL |
|---|---|
| Operations: `maintenance`, `maintenance.server`, `operations` | `https://docs.ravendb.net/<version>/client-api/operations/what-are-operations` |
| Creating a database | `https://docs.ravendb.net/<version>/client-api/operations/server-wide/create-database` |
| Deleting a database | `https://docs.ravendb.net/<version>/client-api/operations/server-wide/delete-database` |
| Listing databases | `https://docs.ravendb.net/<version>/client-api/operations/server-wide/get-database-names` |
| Creating a data subscription | `https://docs.ravendb.net/<version>/client-api/data-subscriptions/creation/how-to-create-data-subscription` |
| Consuming a data subscription | `https://docs.ravendb.net/<version>/client-api/data-subscriptions/consumption/how-to-consume-data-subscription` |
| Subscription worker options | `https://docs.ravendb.net/<version>/client-api/data-subscriptions/consumption/api-overview` |
| Subscription maintenance | `https://docs.ravendb.net/<version>/client-api/data-subscriptions/advanced-topics/maintenance-operations` |
| Changes API | `https://docs.ravendb.net/<version>/client-api/changes/what-is-changes-api` |
| Document change notifications | `https://docs.ravendb.net/<version>/client-api/changes/how-to-subscribe-to-document-changes` |
| Patching one document | `https://docs.ravendb.net/<version>/documents/patching-documents/patch-a-single-document/api-overview` |
| Patch by query | `https://docs.ravendb.net/<version>/documents/patching-documents/patch-multiple-documents/client-api` |
| Storing attachments | `https://docs.ravendb.net/<version>/document-extensions/attachments/store-attachments/store-attachments-local` |
| Loading attachments | `https://docs.ravendb.net/<version>/document-extensions/attachments/get-attachments` |
| Counters | `https://docs.ravendb.net/<version>/document-extensions/counters/create-or-modify` |
| Reading counters | `https://docs.ravendb.net/<version>/document-extensions/counters/retrieve-counter-values` |
| Appending time series entries | `https://docs.ravendb.net/<version>/document-extensions/timeseries/client-api/session/append` |
| Reading time series entries | `https://docs.ravendb.net/<version>/document-extensions/timeseries/client-api/session/get/get-entries` |
| Configuring revisions | `https://docs.ravendb.net/<version>/document-extensions/revisions/client-api/operations/configure-revisions` |
| Loading revisions | `https://docs.ravendb.net/<version>/document-extensions/revisions/client-api/session/loading` |
| Reverting to revisions | `https://docs.ravendb.net/<version>/document-extensions/revisions/revert-documents-to-revisions/revert-documents-to-specific-revisions` |
| Cluster-wide transactions | `https://docs.ravendb.net/<version>/client-api/session/cluster-transaction/overview` |
| Compare exchange | `https://docs.ravendb.net/<version>/compare-exchange/overview` |
| Creating compare-exchange items | `https://docs.ravendb.net/<version>/compare-exchange/create-cmpxchg-items` |

## Install and setup

| Topic | URL |
|---|---|
| Docker image | `https://docs.ravendb.net/<version>/start/containers/image-usage` |
| Setup wizard | `https://docs.ravendb.net/<version>/start/installation/setup-wizard/overview` |
| Manual certificate configuration | `https://docs.ravendb.net/<version>/server/security/authentication/certificate-configuration` |
| Running as a service | `https://docs.ravendb.net/<version>/start/installation/running-as-service` |
| Ubuntu DEB package | `https://docs.ravendb.net/<version>/start/installation/gnu-linux/deb` |
| Activating a license | `https://docs.ravendb.net/<version>/licensing/activate-license` |

## Testing

| Topic | URL |
|---|---|
| Embedded server | `https://docs.ravendb.net/<version>/server/embedded` |
| Pausing indexing | `https://docs.ravendb.net/<version>/client-api/operations/maintenance/indexes/stop-indexing` |

## Diagnostics and raw HTTP

| Topic | URL |
|---|---|
| HTTP endpoints | `https://docs.ravendb.net/<version>/monitoring/debug/debug-endpoints` |
| Logging configuration | `https://docs.ravendb.net/<version>/monitoring/logging/configuration` |
| REST API: batch commands | `https://docs.ravendb.net/<version>/client-api/rest-api/document-commands/batch-commands` |
| REST API: cURL and HTTPS | `https://docs.ravendb.net/<version>/client-api/rest-api/rest-api-intro` |

## AI agents

| Topic | URL |
|---|---|
| Creating AI agents: API | `https://docs.ravendb.net/<version>/ai-integration/ai-agents/creating-ai-agents/creating-ai-agents_api` |
| Multi-agents | `https://docs.ravendb.net/<version>/ai-integration/ai-agents/multi-agents` |
| Reading conversation history | `https://docs.ravendb.net/<version>/ai-integration/ai-agents/reading-conversation-history` |
| AI connection strings | `https://docs.ravendb.net/<version>/ai-integration/connection-strings/overview` |
| Embeddings generation task | `https://docs.ravendb.net/<version>/ai-integration/generating-embeddings/embeddings-generation-task` |
