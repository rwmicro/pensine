# Question 22 — Systemd Targets and Services

## Énoncé

Solve this question on: `web-srv1`

1. Set the default boot target to `multi-user.target`.
2. Enable and start the `nginx` service so it survives a reboot.
3. Mask the `bluetooth.service` so it can never be started.
4. Write the list of currently failed units into `/opt/course/22/failed`.

## Solution

### Step 1 — Change the default target

```bash
systemctl get-default                       # current default
sudo systemctl set-default multi-user.target
```

Common targets (equivalent to old runlevels):

| Target | Equivalent | Purpose |
|---|---|---|
| `poweroff.target` | runlevel 0 | shutdown |
| `rescue.target` | runlevel 1 | single-user / maintenance |
| `multi-user.target` | runlevel 3 | multi-user, no GUI |
| `graphical.target` | runlevel 5 | multi-user + GUI |
| `reboot.target` | runlevel 6 | reboot |
| `emergency.target` | — | minimal shell, no services |

Switch on the fly (no reboot):
```bash
sudo systemctl isolate rescue.target
```

### Step 2 — Enable and start a service

```bash
sudo systemctl enable --now nginx
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
```

Useful variants:
- `enable --now` — enable + start in one shot
- `disable --now` — disable + stop
- `reenable` — recreate symlinks from the unit file (after edits)
- `daemon-reload` — reload unit files after editing them

### Step 3 — Mask a service

A masked service is symlinked to `/dev/null` — it cannot be started, even as a dependency:
```bash
sudo systemctl mask bluetooth.service
sudo systemctl unmask bluetooth.service     # to undo
```

### Step 4 — List failed units

```bash
systemctl --failed --no-legend | awk '{print $2}' > /opt/course/22/failed
```

### Useful day-to-day commands

```bash
systemctl list-units --type=service                  # active services
systemctl list-unit-files --type=service             # all installed
systemctl list-dependencies graphical.target
systemctl cat sshd.service                           # show effective unit file
sudo systemctl edit sshd.service                     # create drop-in override in /etc/systemd/system/sshd.service.d/
sudo systemctl edit --full sshd.service              # full override
```

Drop-ins live in `/etc/systemd/system/<unit>.d/override.conf` and take precedence over `/lib/systemd/system/<unit>` — never edit vendor files directly.

