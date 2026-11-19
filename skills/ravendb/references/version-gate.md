# Version & license gate

Run the matching check before writing code against a marked feature.

| Gate | Check |
|---|---|
| Server version | `GET /build/version` → `{"BuildVersion":…,"ProductVersion":"<major.minor>","FullVersion":"<full>"}`. |
| Client library version | The project's manifest, not the docs: `package.json` (`ravendb`), `.csproj`/`Directory.Packages.props` (`RavenDB.Client`), `requirements.txt`/`pyproject.toml` (`ravendb`). A new server with an old client still fails: `store.ai` needs client 7.2+, vector search client 7.0+. Whether a type exists, without compiling: `strings ~/.nuget/packages/ravendb.client/<v>/lib/<tfm>/Raven.Client.dll \| grep <TypeName>`, `grep -r <name> node_modules/ravendb/dist/`, or `grep -r` the installed Python package. |
| License | `GET /license/status` → `Type` plus a boolean per feature (`HasAiAgent`, `HasEmbeddingsGeneration`, `HasGenAi`, `HasConcurrentDataSubscriptions`, `HasTimeSeriesRollupsAndRetention`, …). No client wrapper: call the endpoint. |

Unlicensed servers also cap counts, and going over is refused with HTTP 402 (`LicenseLimitException`): subscriptions
per database (`MaxNumberOfSubscriptionsPerDatabase`), concurrent workers on one subscription
(`HasConcurrentDataSubscriptions`), revisions kept (`MaxNumberOfRevisionsToKeep`, `MaxNumberOfRevisionAgeToKeepInDays`)
and a database-wide revisions default (`CanSetupDefaultRevisionsConfiguration`). Read them before creating a
subscription or a revisions configuration.

A server gap shows as a 404 or a missing endpoint, a client gap as a name that does not exist or an obsolete-API
warning. An API can also move on the client alone while every supported server handles it.

If a gate fails, say which one and what passing it takes, then ask. Do not silently substitute another approach, and do
not write code that needs a feature the deployment cannot run. The license check and the free Developer
license: "Version and license check" in `install.md`, then `license.md`.

Support can also depend on the search engine of the index serving a query (Corax or Lucene, set per index), not on the
server version: `rql-fulltext.md`.
