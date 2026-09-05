# Process supervisor

A small Python arbiter that can replace Supervisord in the CRCON supervisor container when enabled via `CRCON_USE_PROCESS_SUPERVISOR`. It reads the existing `supervisord.conf` INI, speaks the XML-RPC subset the Services UI needs, and starts known Python loops **without** `manage.py` / `rcon.cli`. Registered loops can fork from a preloaded helper so extra services mostly add unique heap instead of another copy of the catalog.

Backend / gunicorn is out of scope. `workers` (rq), `cron`, and `scheduler` still exec their INI commands.

## Why

Each Supervisord child was a new interpreter that imported `rcon.cli`. That paid the ~100+ MB import graph once per loop with no shared pages. This arbiter:

1. Dispatches by program name to a **supervisor-only adapter** (`programs.run_<name>`), which lazy-imports that service (broadcasts does not load automod, Discord, etc. at import time). Adapters may wrap `run()` with try/except, hook imports, or scoreboard sqlite bootstrap; they are not wired into `rcon.cli` until the arbiter is proven in production.
2. Forks registered loops from a **forkserver** that has already mapped `hllrcon` and `rcon.maps`, so children share those pages via copy-on-write.

INI `command=` lines stay as documentation / extra argv. Programs **with** a `run_<name>()` adapter in [`programs.py`](programs.py) use worker/fork spawn; programs **without** an adapter exec the INI `command=` as-is (e.g. `workers`, `cron`, `scheduler`).

## Runtime

```
Container start (entrypoint.sh)
        |
        v
CRCON_USE_PROCESS_SUPERVISOR truthy?
        |
   yes  |  no
        v   v
python -m rcon.process_supervisor   supervisord
        |
        +-- parse INI (config.py)
        +-- arbiter log (logging_setup.py)
        +-- XML-RPC thread :9001/RPC2 (rpc.py)
        +-- ProcessSupervisor.run()  100ms tick
                |
                v
        ManagedProcess.spawn
                |
    +-----------+-----------+
    |                       |
 adapter + fork on      adapter + fork off       no run_<name> adapter
 forkserver -> fork_main    Popen worker -m          Popen INI argv
                |                       |                       |
                +-----------+-----------+                       |
                            v                                   v
                   registry.run_program()              rq / cron / rqscheduler
                            |
                   programs.run_<name>()
```

Entry: [`entrypoint.sh`](../../entrypoint.sh) runs `python -m rcon.process_supervisor` when `CRCON_USE_PROCESS_SUPERVISOR` is `1` / `true` / `yes` / `on`; otherwise it runs `supervisord`. Config path is `/config/supervisord_$SERVER_NUMBER.conf` if it exists, else `/config/supervisord.conf`.

## Spawn policy

| Program set | Condition | Child | INI `command=` |
| --- | --- | --- | --- |
| Has `run_<name>` adapter, fork on | `has_adapter(name)` and `CRCON_SUPERVISOR_FORK` not disabled | `multiprocessing` forkserver → `fork_main` | Ignored except extra argv (`log_recorder -i 10`) |
| Has `run_<name>` adapter, fork off | `CRCON_SUPERVISOR_FORK=0` (or `false` / `no` / `off`) | `Popen python -m rcon.process_supervisor.worker` | Same rewrite; new interpreter, no CoW |
| No adapter | no `programs.run_<name>` | `Popen` of INI argv (Python-shaped commands log a warning) | Honored as-is; rq/cron/scheduler exec silently |

Fork is disabled on Windows. Do not fork from the RPC-threaded arbiter; the forkserver is a separate helper process.

### After fork (`worker/fork_child.py`)

1. Replace `os.environ` with the program’s child env.
2. `os.setsid()` (new process group for `killpg` on stop).
3. Redirect stdout/stderr to the program log file.
4. Import `rcon.settings` (logging from child env).
5. `install_unaccent()`, then drop inherited SQLAlchemy engine and Redis pools; recreate the Redis pool in **bytes** mode (same order as a fresh interpreter). That does not flush Redis keys.
6. `registry.run_program(name, extra)` → `programs.run_<name>()` (or `run_log_recorder(extra)`).

Discord still loads **after** fork in services that use it (`seed_vip`, `scoreboard`, …), so those stay heavier than a tiny poller.

## Control plane and locking

XML-RPC (`SimpleXMLRPCServer`) is **one request at a time**. The arbiter loop and RPC share `ProcessSupervisor._lock`.

- **startProcess:** spawn under the lock (`start(wait=False)`), return immediately. `tick()` promotes STARTING → RUNNING after `startsecs`. The RPC thread must not sleep `startsecs` (10s on automod / blacklists / scoreboard) or it would stall `getAllProcessInfo` and every other program’s reap/backoff.
- **stopProcess:** signal under the lock (`stop(wait=False)`), wait **outside** the lock until the child exits (or SIGKILL after `stopwaitsecs`), then set STOPPED. Wait is required so the next start is not `ALREADY_STARTED`. Concurrent `tick()` / `getAllProcessInfo` must still run during that wait.
- **tick:** left as-is; STOPPING children are reaped here if the child dies before the RPC wait finishes. `ManagedProcess.stop` is idempotent if `popen` is already `None`.

Fault codes match Supervisord for the UI: `BAD_NAME` 10, `ALREADY_STARTED` 60, `NOT_RUNNING` 70.

Methods exposed:

- `supervisor.getAllProcessInfo`
- `supervisor.getProcessInfo`
- `supervisor.startProcess`
- `supervisor.stopProcess`

States: STOPPED, STARTING, RUNNING, BACKOFF, STOPPING, EXITED, FATAL (same integer codes as Supervisord). Autorestart: `true` / `false` / `unexpected`. Backoff before retry is a flat 1s (not Supervisord’s exponential curve).

Client: [`rconweb/api/services.py`](../../rconweb/api/services.py) via `SUPERVISOR_RPC_URL` (typically `http://supervisor:9001/RPC2`).

## Supervisord subset (not a clone)

Implemented: `[program:*]` + `%(ENV_VAR)s`, `[inet_http_server] port`, `[supervisord] logfile` rotation, process info fields the UI reads, start/stop/faults, `stopsignal` / `stopwaitsecs` / `startretries` / `startsecs` / `autostart` / `autorestart`.

Not implemented:

- Unix socket / `supervisorctl` (`[unix_http_server]` in the INI is ignored)
- Per-program log rotation (children append to `LOGGING_PATH` / `LOGGING_FILENAME`)
- HTTP auth on XML-RPC
- `startProcess` wait-until-RUNNING (returns after spawn)

## Adding a Python loop

Opt-in is by code: add `run_<name>()` in [`programs.py`](programs.py). Long-term that entry point may live on the domain module; the supervisor still keys off the same `run_<name>` convention. A new forkable loop needs:

1. `[program:your_name]` in [`config/supervisord.conf`](../../config/supervisord.conf)
2. Implement `run_<name>()` in [`programs.py`](programs.py) with lazy imports and the same exception wrapping as `manage.py` / [`rcon/cli.py`](../../rcon/cli.py) today

CLI is **not** wired to these adapters until the arbiter is proven in production; duplication with CLI wrappers is intentional for now.

Custom `command=` flags on an adapted name are dropped except the hand-rolled `log_recorder` argv parser in `programs.py`. Names without a `run_<name>()` still exec the INI command (use that for non-Python helpers or until you add an adapter). A `manage.py` / `python -m` program without `run_<name>()` still starts, but the arbiter logs a warning; add the adapter to get worker/fork spawn.

## Environment

| Variable | Role |
| --- | --- |
| `CRCON_USE_PROCESS_SUPERVISOR` | Default off (`0` / unset). Set `1` / `true` / `yes` / `on` in `.env` to use this arbiter instead of Supervisord in the supervisor container |
| `SERVER_NUMBER` | Numbered INI path `/config/supervisord_$SERVER_NUMBER.conf` |
| `CRCON_SUPERVISOR_FORK` | When this arbiter is active: default on. Set `0` / `false` / `no` / `off` to exec workers instead of fork |
| `SUPERVISOR_RPC_URL` | Django → this arbiter |
| `LOGGING_PATH` / `LOGGING_FILENAME` | Per-program child logs (from INI `environment=`) |

## Module map

| File | Role |
| --- | --- |
| [`__main__.py`](__main__.py) | Load INI, logging, RPC thread, `run()` |
| [`config.py`](config.py) | INI → `ProgramConfig` / `SupervisorConfig` |
| [`logging_setup.py`](logging_setup.py) | Arbiter stderr + rotating `supervisord.log` |
| [`manager.py`](manager.py) | Lock, autostart, tick, start/stop RPC, signals |
| [`process.py`](process.py) | State machine, Popen vs fork spawn, `killpg` |
| [`preload.py`](preload.py) | Forkserver context; preload `hllrcon`, `rcon.maps` only |
| [`programs.py`](programs.py) | Supervisor-only `run_<name>` adapters and hook/argv helpers |
| [`registry.py`](registry.py) | `has_adapter`, argv rewrite, `run_program` dispatch |
| [`rpc.py`](rpc.py) | XML-RPC subset |
| [`states.py`](states.py) | Supervisord state ints and fault codes |
| [`worker/__main__.py`](worker/__main__.py) | Exec path: settings, unaccent, `run_program` |
| [`worker/fork_child.py`](worker/fork_child.py) | Post-fork env, stdio, resource reset |

Preload must stay tiny. Do not add `rcon.cli`, `rcon.settings`, `rcon.rcon`, or `discord` to `PRELOAD_MODULES` (tests assert this).

## Tests

```bash
uv run pytest tests/test_process_supervisor.py \
  tests/test_process_supervisor_fork.py \
  tests/test_process_supervisor_registry.py \
  tests/test_process_supervisor_worker_main.py -q
```
