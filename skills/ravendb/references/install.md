# Getting a RavenDB server running

## Find a server before installing one

Probe, then ask. On Windows use the equivalents in `windows.md`; the commands below are POSIX.

```bash
for u in http://localhost:8080 http://localhost:80; do
  printf '%s ' "$u"; curl -s -o /dev/null -w '%{http_code}\n' --max-time 3 "$u/setup/alive"   # 204 → RavenDB here
done
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Ports}}' | grep -i raven                       # running container + its published port
docker ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}' | grep -i raven                   # stopped one: `docker start <name>` beats a fresh install
pgrep -af 'Raven.Server' | head                                                               # native process; Windows: Get-Service RavenDB
ss -tlnp | grep -E ':(80|8080|8081|8090|9090|38888|38889)\b'                                  # macOS: lsof -i :8080
```

**A port list is not a discovery protocol.** List everything listening (`ss -tln`, no filter) and curl `/setup/alive` on each candidate, 8090 included (the remap suggested below).

**`docker port <name>` settles which of a native process and a container holds a port.** `ss -tlnp` shows no process for other users' sockets unless you are root, and a container's server appears in the host's `pgrep -af Raven.Server` like a native one: check `docker top` or the process owner before calling it a native install.

Read what the project declares too: `appsettings*.json`, `.env` and `docker-compose*.yml` often name a URL (non-default port included) and a database to use verbatim.

Then, in one interaction:

- **Something answered:** report each URL with its version, databases (each `Environment`) and license, then ask which server and database to use, and wait. The license matters: a shared licensed server and an unlicensed one of your own lead to opposite advice. Ask even for exactly one server and one plausible database (the user may want an isolated instance or another database), and say so when the task needs a kind of server not running (secured, isolated, a specific version).
- **A RavenDB process or container exists but answers nothing:** offer to start it (`docker start <name>`, `systemctl start ravendb`) before offering to install, and say why it looked unreachable (wrong port, wizard mode, dead container).
- **Nothing found:** say so and ask whether to install a local dev server, naming the method (Docker if the daemon is up, otherwise native) and the port. Install only after a yes. If the user has a server elsewhere (cloud, team dev box), ask for its URL, database and certificate. For a throwaway experiment, offer `http://live-test.ravendb.net`: free, but **shared, public and periodically wiped**, so never for real or private data.

**A server whose `GET /databases` lists databases you did not create is shared.** Creating a database, changing server settings or registering a license there touches other people's work: report what you found and get a yes first. Being the only server running is not consent.

## Installing a dev server

Target: one unsecured single-node server on `http://localhost:8080`, Docker if the daemon is up, otherwise native (`install-native.md`). Unsecured means no certificate and no auth, so keep it on localhost. It publishes two host ports, **8080 and 38888** (TCP), and both must be free; another RavenDB container already holding 38888 is the common clash. The HTTP port remaps freely (`-p 8090:8080`): report the URL you settled on.

## TCP port: remap it on the server, not only in Docker

`-p 38889:38888` alone breaks data subscriptions. A client that needs TCP (subscriptions, cluster traffic) asks `GET /info/tcp` and dials the port the server binds; the server knows nothing about the Docker mapping. Clients dial 38888 on the host, reach whichever other RavenDB holds it, and fail with a missing database rather than a wrong port. HTTP work (CRUD, queries, bulk insert) succeeds either way, so this stays hidden until the first subscription.

Use the same port number in all three places, one you checked is free:

```bash
-p <free>:<free> -e RAVEN_ServerUrl_Tcp=tcp://0.0.0.0:<free>
# add -e RAVEN_PublicServerUrl_Tcp=tcp://<host clients dial>:<free> when that hostname is not the bind address
```

Published ports are fixed when the container is created: `docker rm -f` it and re-run with the same named volumes, which keep the data. On a server you do not control, run your own with matching ports; the server chooses the TCP address, so there is no client-side fix.

## Docker (development, unsecured)

`docker-compose.ravendb.yml`:

```yaml
services:
  ravendb:
    image: ravendb/ravendb:latest
    container_name: ravendb-dev
    ports:
      - "8080:8080"
      - "38888:38888"
    environment:
      - RAVEN_Setup_Mode=None
      - RAVEN_License_Eula_Accepted=true
      - RAVEN_DATABASE=MyApp
    volumes:
      - ravendb-data:/var/lib/ravendb/data
      - ravendb-config:/etc/ravendb

volumes:
  ravendb-data:
  ravendb-config:
```

```bash
docker compose -f docker-compose.ravendb.yml up -d     # stop / down -v to remove data
```

Single-shot equivalent:

```bash
docker run -d --name ravendb-dev -p 8080:8080 -p 38888:38888 \
  -e RAVEN_Setup_Mode=None -e RAVEN_License_Eula_Accepted=true -e RAVEN_DATABASE=MyApp \
  -v ravendb-data:/var/lib/ravendb/data -v ravendb-config:/etc/ravendb \
  ravendb/ravendb:latest
```

- `RAVEN_Setup_Mode=None` is required: the image defaults to `Initial`, which boots the setup wizard and serves no API. Any config key works as `RAVEN_` plus the key with dots as underscores, or through `RAVEN_ARGS=--Setup.Mode=None`. Other image options and tags: `client-docs.md` (Docker image).
- `RAVEN_DATABASE` creates the database a moment **after** `/setup/alive` starts answering: poll for the database, not the server.
- The two volumes are what survives `docker rm`: `/var/lib/ravendb/data` holds the databases, `/etc/ravendb` the settings and certificates. `/opt/RavenDB/Server/RavenData`, the path of older images, is unused by the current one: mounting it persists nothing, silently.
- Leave `RAVEN_Security_UnsecuredAccessAllowed` unset: the image default `PrivateNetwork` already admits the published port. `PublicNetwork` is for multi-node setups whose nodes advertise a `PublicServerUrl` to each other.

## Wait for ready, then verify

```bash
for i in $(seq 1 20); do
  [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://localhost:8080/setup/alive)" = "204" ] && break
  sleep 3
done
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080/databases/MyApp/stats    # 200 once the database exists
```

Never ready: `docker logs ravendb-dev` (native: the console output). Usual causes: a port already bound, a missing `RAVEN_Setup_Mode=None`, a volume the container user cannot write.

## Create a database explicitly

`PUT /admin/databases` with `{"DatabaseName":"MyApp"}` (`http-api.md`). A name that exists returns **409** `ConcurrencyException`: treat it as success so provisioning stays idempotent. Deleting: `DELETE /admin/databases` with `{"DatabaseNames":["MyApp"],"HardDelete":true}`. From application startup instead: `structure.md` and your language's `operations.md`.

## Version and license check

Run both on every server you connect to, installed or found. The server and client version checks, and what to say when either side is short: `version-gate.md`. The license:

```bash
curl -s http://localhost:8080/license/status
```

`Type` is `None` on an unlicensed server. Beyond the `Has*` flags in `version-gate.md`:

- **Going over a `Max*` cap throws `LicenseLimitException` (HTTP 402).** Besides the subscription and revisions caps in `version-gate.md`, custom analyzers and sorters, cluster size, cores and memory are capped the same way. Read the number before configuring: unlicensed values are small, and `Has*` will not warn you.
- **Caps are not enforced for about the first minute after startup.** An over-cap configuration is then accepted with a 200, persisted to the database record and honoured afterwards; the same call a minute later gets 402. Provisioning that runs as the container comes up lands exactly there, so read the cap first: a 200 does not prove you were inside it.
- **`Can*` flags are a third category.** `CanSetupDefaultRevisionsConfiguration` is `false` unlicensed and refuses a database-wide default revisions configuration at any size ("Your license doesn't allow the creation of a default configuration for revisions"); per-collection configuration inside the caps still works.
- **A retention cap limits the configured number, not the history kept.** `MinimumRevisionsToKeep` is a floor against pruning, and with an age limit set, age drives pruning: three writes under a cap of `2` can keep three revisions, so an unlicensed server can hold more than two.

**When `Type` is `None` or the license has expired, warn the user before building on it**, and never install a license silently. State the limits that bite, with the numbers from the response (cores, cores per node, memory, cluster size), and that every add-on is off: AI agents, embeddings generation, encryption, ETL and cluster features fail at runtime, not at startup. Then ask whether they want a **free Developer license** now, and continue on their answer:

- Yes: `license.md` (who requests the key, activation, verification).
- No: say which features the plan can no longer use, and keep the design inside what an unlicensed server can do.

## Secured server

**The setup wizard needs a license; security does not.** An unlicensed server runs fully secured (HTTPS plus client-certificate authentication) when configured directly, which is the route for a local secured dev server:

```bash
-e RAVEN_Setup_Mode=None -e RAVEN_License_Eula_Accepted=true \
-e RAVEN_ServerUrl=https://0.0.0.0:<port> -e RAVEN_PublicServerUrl=https://<host clients dial>:<port> \
-e RAVEN_Security_Certificate_Path=/certs/server.pfx \
-e RAVEN_Security_Certificate_Password=<password> \
-e RAVEN_Security_WellKnownIssuers_Admin="$(openssl x509 -in ca.crt -outform DER | base64 -w0)"
```

- The server certificate needs a SAN matching the host clients dial (`DNS:localhost`, `IP:127.0.0.1` locally). The server's own certificate authenticates as cluster admin, which is how you register the first client certificate without already having one.
- `Security.WellKnownIssuers.Admin` takes **base64 of the issuer's DER bytes**, not a thumbprint. A thumbprint kills the server at boot: `Unable to parse the provided 'Security.WellKnownIssuers.Admin' value` → `ASN1 corrupted data`. Client certificates signed by that issuer are admitted; any other gets `403 InvalidAuth` naming the unknown certificate.
- With a certificate configured, `Security.UnsecuredAccessAllowed` no longer applies: every request needs a certificate.
- `RAVEN_DATABASE` does **not** work on a secured server: the entrypoint fails (`./cert-utils.sh: No such file or directory`) and the container exits 1. Create the database with `PUT /admin/databases`, presenting your client certificate.
- `rvn` cannot generate certificates, only consume them (`put-client-certificate`, `create-setup-package -m own-certificate`): generate them with `openssl`. `put-client-certificate` accepts no password, so the pfx you hand it must have none.

Other certificate settings: `client-docs.md` (Manual certificate configuration).

For a public-facing server use the wizard: start with only `RAVEN_License_Eula_Accepted=true`, open the server URL and follow it. It issues a Let's Encrypt certificate (on a free `*.development.run` domain) or takes your own, and hands back a client-certificate bundle. **It needs a license key to complete.** Steps: `client-docs.md` (Setup wizard).

Client side: the "Secured server" section of your language's `client.md`.
