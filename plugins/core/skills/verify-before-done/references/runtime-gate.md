# Runtime gate

Load when local behaviour does not match the code, or before any end-to-end claim.

The question: is the code you are reading the code that is running? Answer it with timestamps and process
facts before you analyse anything else.

## Checks

| Check | Command (examples) |
|---|---|
| Source files changed after the build | `find src -newer dist/server.js -type f` lists every source file newer than the built file |
| Last commit that touched the source | `git log -1 --format=%cI -- src/` |
| Process start time | `ps -o pid,lstart,args -p [pid]` |
| Container start time | `docker inspect -f '{{.State.StartedAt}}' [container]` |
| Image build time | `docker image inspect -f '{{.Created}}' [image]` |
| systemd unit start time | `systemctl show -p ActiveEnterTimestamp [unit]` |
| Who listens on a port | `lsof -nP -iTCP:[port] -sTCP:LISTEN`, or on Linux `ss -ltnp 'sport = :[port]'` |
| Where a process was started | `lsof -a -p [pid] -d cwd`, or on Linux `readlink /proc/[pid]/cwd` |

A process that started before the last change to its source, or a build older than its source, is stale.
Stop the analysis, rebuild or restart, and check again.

## What long-lived processes hold

- Queue workers load the code once at start. A new class, enum case or config value is unknown to them until
  they restart. Symptoms: "undefined constant", "class not found", or an old code path in job logs.
- Persistent app servers (worker-mode PHP servers, Node servers without a file watcher, JVM services) keep
  the code and often the config they booted with.
- Stream and message consumers behave like queue workers.
- Schedulers that run tasks in-process keep the code from their start.
- Dev servers and build watchers may compile translations, routes or config only at boot. A new translation
  key or route can need a restart even with hot reload running.
- Opcode or bytecode caches with timestamp checks turned off serve old code until cleared.
- Hand-started binaries from an earlier session keep running with old behaviour and can own the port your new
  build wanted.

## Restart rules

- Restart processes you started in this session.
- Ask before you stop or restart anything else: a teammate's process, a shared container, a process running as
  another user, anything outside the local machine. `safe-actions` covers this.
- After a restart, repeat the check. The new start time must be later than the last change.

## Recording the gate

Put one line per running component into the completion report: name, start time, source change time, result.

```text
api        started 10:42:07  source changed 10:39:55  ok
worker     started 08:15:31  source changed 10:39:55  stale, restarted 10:43:10
web build  built   10:20:02  source changed 10:39:55  stale, rebuilt 10:44:30
```
