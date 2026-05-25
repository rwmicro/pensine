# Question 23 — Process Management

## Énoncé

Solve this question on: `app-srv1`

1. Find the PID of the process listening on TCP port `8080` and write it into `/opt/course/23/pid`.
2. Renice the process `stress-ng` to priority `10` without killing it.
3. Send `SIGTERM` to all `sleep` processes owned by user `bob`.
4. Identify the top 3 memory-consuming processes and write their command names into `/opt/course/23/top-mem`.

## Solution

### Step 1 — Find the process behind a port

```bash
sudo ss -tlnp | grep :8080
# LISTEN 0 511 *:8080 *:* users:(("node",pid=1423,fd=18))
sudo ss -tlnp 'sport = :8080'
sudo lsof -i :8080
sudo fuser 8080/tcp
```

Pull just the PID:
```bash
sudo ss -tlnpH 'sport = :8080' | grep -oP 'pid=\K[0-9]+' > /opt/course/23/pid
```

### Step 2 — Change priority

Nice values range from `-20` (highest priority) to `19` (lowest). Only root can lower (more negative) the niceness.

```bash
ps -eo pid,ni,cmd | grep stress-ng
sudo renice -n 10 -p $(pgrep stress-ng)
# or rename whole process group / user
sudo renice -n 10 -u bob
sudo renice -n 10 -g 1234
```

Start a process with a given priority:
```bash
nice -n 15 ./long-job.sh
chrt -f 50 ./realtime-job                  # real-time scheduling
ionice -c 3 ./bulk-copy.sh                 # I/O idle class
```

### Step 3 — Kill processes selectively

```bash
pgrep -u bob sleep                          # list matching PIDs
sudo pkill -SIGTERM -u bob sleep            # signal them
sudo killall -u bob sleep                   # by name
```

Signals worth knowing:
- `SIGHUP` (1) — reload config (many daemons)
- `SIGINT` (2) — Ctrl+C
- `SIGKILL` (9) — uncatchable, immediate
- `SIGTERM` (15) — polite termination, default
- `SIGSTOP` / `SIGCONT` — pause / resume

### Step 4 — Top memory consumers

```bash
ps -eo pid,comm,%mem --sort=-%mem | head -n 4
ps -eo pid,comm,%mem --sort=-%mem | awk 'NR>1 && NR<=4 {print $2}' > /opt/course/23/top-mem
```

### Live monitoring

```bash
top                # interactive — press M (mem), P (cpu), k (kill)
htop               # nicer alternative
pidstat 1          # per-process CPU/mem every second
vmstat 1           # global counters
iotop              # I/O per process (needs root)
```

### Background and job control

```bash
./long.sh &                       # background
jobs                              # list shell jobs
fg %1                             # foreground job 1
bg %1
nohup ./long.sh &                 # survive shell logout
disown %1                         # detach existing job
```

---

[← Question 22](q22-systemd-targets-and-services.md) · [Index](Certifications/LFCS/notes.md) · [Question 24 →](q24-system-logs.md)
