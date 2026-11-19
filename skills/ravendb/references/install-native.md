# Native installation

No Docker: download the server archive, extract, run the binary. Health check, database creation and licensing are as in `install.md`. Commands here are POSIX; on Windows read `windows.md`.

## Download

`/latest` redirects to the current stable build, so follow redirects (`curl -L`; `Invoke-WebRequest` already does).

| Platform | URL under `https://hibernatingrhinos.com/downloads/` | Archive |
|---|---|---|
| Windows x64 | `RavenDB%20for%20Windows%20x64/latest` | `.zip` |
| Linux x64 | `RavenDB%20for%20Linux%20x64/latest` | `.tar.bz2` |
| Linux ARM64 | `RavenDB%20for%20Linux%20ARM64/latest` | `.tar.bz2` |
| Ubuntu 24.04 x64 | `RavenDB%20for%20Ubuntu%2024.04%20x64%20DEB/latest` | `.deb` |
| macOS Intel (`uname -m` = `x86_64`) | `RavenDB%20for%20macOS%20x64/latest` | `.tar.bz2` |
| macOS Apple Silicon (`uname -m` = `arm64`) | `RavenDB%20for%20macOS%20arm64/latest` | `.tar.bz2` |
| Raspberry Pi | `RavenDB%20for%20Raspberry%20Pi/latest` | `.tar.bz2` |

Labels are case- and word-exact: `macOS%20ARM`, or an Ubuntu label without `%20DEB`, returns 404; read the current list off <https://ravendb.net/download>. Other Ubuntu releases and arm32/arm64 DEBs follow the same pattern. The `.deb` is not extract-and-run: it installs and starts a `ravendb` service in setup-wizard mode on `http://127.0.0.1:53700`, not 8080: `client-docs.md` (Ubuntu DEB package).

```bash
curl -L --progress-bar -o ravendb.tar.bz2 "https://hibernatingrhinos.com/downloads/RavenDB%20for%20Linux%20x64/latest"
mkdir -p ~/ravendb && tar xjf ravendb.tar.bz2 -C ~/ravendb --strip-components=1 && rm ravendb.tar.bz2
```

The archive holds a single top-level `RavenDB/` directory, hence `--strip-components=1`. The binary is `Server/Raven.Server`, with `run.sh` and `install-daemon.sh` next to `Server/`.

## Run (development, unsecured)

```bash
~/ravendb/Server/Raven.Server --Setup.Mode=None \
  --ServerUrl=http://127.0.0.1:8080 --ServerUrl.Tcp=tcp://127.0.0.1:38888 \
  --DataDir=/srv/ravendata
```

- Pass `--Setup.Mode=None` and both URLs: the package's `Server/settings.json` sets `Setup.Mode=Initial` and `ServerUrl=http://127.0.0.1:0`, so a bare `run.sh` boots the setup wizard on a random port.
- Both ports must be free: pick another pair (`8099` / `38899`) when a server holds them, and report the HTTP one.
- Set `--DataDir` before the first database is created: adding it later leaves the earlier tree behind and the server comes up empty.
- No unsecured-access flag is needed on loopback: `Security.UnsecuredAccessAllowed` defaults to `Local`. Do not widen it (`PrivateNetwork`, `PublicNetwork`) for an unsecured server.

## Run as a service

- **Windows:** `windows.md`. There is no `Raven.Server.exe` service flag.
- **Linux:** `install-daemon.sh`, or a systemd unit: `client-docs.md` (Running as a service). The docs unit starts `run.sh`, which reads `Server/settings.json`: set `Setup.Mode`, `ServerUrl`, `ServerUrl.Tcp` and `DataDir` there first, or the service boots into the wizard. Keep `LimitNOFILE` high (65535 in the docs unit): RavenDB memory-maps its data files and hits the default 1024 descriptor cap under load. The steps need `sudo`, so print them for the user rather than running them.

## Data

Data lives where `DataDir` points (`Server/settings.json`, or the flag); a relative path resolves against `Server/`. Deleting that tree resets every database, and an upgrade replaces the install directory, so keep the data outside it.

## Reaching it from another machine

Only once it is secured (`install.md`, Secured server). Then open both the HTTP and the TCP port in the firewall: clients reach subscriptions over TCP.
