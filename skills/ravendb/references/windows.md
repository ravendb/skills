# RavenDB on Windows

`install.md` and `install-native.md` apply, but their commands are POSIX. Use the forms below, and read the rules: several are not a translation of a command.

## Probing for an existing server

```powershell
foreach ($u in 'http://localhost:8080','http://localhost:80') {
  try { $r = Invoke-WebRequest "$u/setup/alive" -UseBasicParsing -TimeoutSec 3; "$u $($r.StatusCode)" }
  catch { "$u unreachable" }
}
Get-Service RavenDB* -ErrorAction SilentlyContinue | Select-Object Name, Status
Get-Process Raven.Server -ErrorAction SilentlyContinue | Select-Object Id, Path
Get-NetTCPConnection -LocalPort 8080,80 -State Listen -ErrorAction SilentlyContinue |
  ForEach-Object { "{0} ← {1}" -f $_.LocalPort, (Get-Process -Id $_.OwningProcess).ProcessName }
docker ps -a --format '{{.Names}} {{.Image}} {{.Status}}' | Select-String raven
```

`Invoke-WebRequest` **throws** on any non-2xx, so a 404 from `/databases/<db>/stats` is an exception, not a status code: wrap probes in `try/catch` (PowerShell 7 also has `-SkipHttpErrorCheck`). In PowerShell 5.1 `curl` is an alias for `Invoke-WebRequest` and ignores curl flags; call `curl.exe` for the real one (Windows 10 1803+).

## Docker Desktop

`ravendb/ravendb:latest` is a Linux image and needs the WSL2 (or Hyper-V) backend, the default. Its published ports reach `http://localhost:8080` on Windows, so the compose file in `install.md` works unchanged: write it with LF endings, and use named volumes, not host paths (a bind-mounted Windows directory gives the container's non-root `ravendb` user permission errors on the data path).

Windows containers are a separate image family (`ravendb/ravendb:<version>-windows-ltsc2022` or `-windows-1809`), only for a daemon in Windows-container mode, where the Linux image cannot run and its tag looks absent.

## Native install

```powershell
Invoke-WebRequest -Uri "https://hibernatingrhinos.com/downloads/RavenDB%20for%20Windows%20x64/latest" -OutFile ravendb.zip
Expand-Archive -Path ravendb.zip -DestinationPath C:\RavenDB -Force ; Remove-Item ravendb.zip
$server = (Get-ChildItem C:\RavenDB -Recurse -Filter Raven.Server.exe | Select-Object -First 1).FullName
& $server --Setup.Mode=None --ServerUrl=http://127.0.0.1:8080 --ServerUrl.Tcp=tcp://127.0.0.1:38888
```

Locate `Raven.Server.exe` rather than assuming `C:\RavenDB\Server\`: the zip holds a single top-level `RavenDB\` directory, so extracting to `C:\RavenDB` yields `C:\RavenDB\RavenDB\Server\`.

## Run as a service

There is **no** `Raven.Server.exe` service flag. Both routes need an **elevated** PowerShell:

```powershell
.\setup-as-service.ps1                                    # ships in the package; prompts for port, ACLs the dir, registers
& '<package>\Server\rvn.exe' windows-service register --service-name RavenDB -- --Setup.Mode=None --ServerUrl=http://127.0.0.1:8080
Start-Service RavenDB                                      # rvn windows-service start|stop also work
Get-Service RavenDB
```

`rvn.exe` is in the package's `Server\` directory (`--server-dir` points it at another). Arguments after `--` pass through to the server; without them the service reads `Server\settings.json`, whose defaults boot the setup wizard on a random port. Service account, `unregister`, and the "not digitally signed" error from `setup-as-service.ps1`: `client-docs.md` (Running as a service).

## WSL2

- **Windows → WSL:** a server started inside WSL answers on `http://localhost:8080` from Windows (localhost forwarding is on by default).
- **WSL → Windows:** `localhost` does **not** reach the Windows host. Use the host IP (`ip route show default | awk '{print $3}'`) or mirrored networking (`networkingMode=mirrored` in `%UserProfile%\.wslconfig`, Windows 11 22H2+), after which `localhost` works both ways.
- A server bound to `127.0.0.1` inside WSL is invisible to Windows regardless. Bind `0.0.0.0` when it must be shared; an unsecured server then needs `Security.UnsecuredAccessAllowed` widened beyond `Local`, so do it only for a dev server on a trusted machine.
- A `.sh` helper written from Windows or on a Windows-mounted path gets CRLF endings, and a `#!/bin/bash\r` shebang fails with a confusing "No such file or directory". Strip them: `sed -i 's/\r$//' <file>`.

## Firewall

Localhost needs nothing. Another machine reaching a **secured** server needs both ports opened (clients reach subscriptions over TCP), from an elevated shell. The parameter is `-LocalPort`; `-Port` does not exist:

```powershell
New-NetFirewallRule -DisplayName "RavenDB" -Direction Inbound -LocalPort 8080,38888 -Protocol TCP -Action Allow
```

## Paths

Native: data lives where `DataDir` points (`<package>\Server\settings.json`, or `--DataDir=D:\RavenData`); a relative path resolves against `Server\`. Move it off the install directory before an upgrade replaces that tree. The Linux Docker image uses `/var/lib/ravendb/data` and `/etc/ravendb` inside the container (`install.md`).
