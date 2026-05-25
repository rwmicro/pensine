# Question 24 — System Logs

## Énoncé

Solve this question on: `web-srv1`

1. Write all `nginx.service` log entries from the last boot into `/opt/course/24/nginx.log`.
2. Configure `systemd-journald` to store logs **persistently** across reboots.
3. List all kernel error messages since `2024-01-01` into `/opt/course/24/kernel-errors.log`.
4. Limit the journal disk usage to a maximum of `200M`.

## Solution

### Step 1 — Service logs from current boot

```bash
journalctl -u nginx.service -b 0 > /opt/course/24/nginx.log
```

`journalctl` cheat sheet:

| Flag | Meaning |
|---|---|
| `-u <unit>` | filter by systemd unit |
| `-b` / `-b -1` / `-b 0` | current boot / previous boot / current |
| `--list-boots` | list available boots |
| `-p err` | priority ≤ error (emerg, alert, crit, err, warning, notice, info, debug) |
| `-k` | kernel messages only (= `dmesg`) |
| `-f` | follow (like `tail -f`) |
| `--since "2024-01-01"` `--until "1h ago"` | time-based filter |
| `-n 50` | last 50 lines |
| `-o json-pretty` | output format |
| `--disk-usage` | space used by journal |
| `--vacuum-size=200M` / `--vacuum-time=2weeks` | shrink |

### Step 2 — Make the journal persistent

By default, on systems without `/var/log/journal/`, logs live in `/run/log/journal/` (RAM, lost at reboot).

```bash
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo systemctl restart systemd-journald
```

Or edit `/etc/systemd/journald.conf`:
```ini
[Journal]
Storage=persistent       # persistent | volatile | auto | none
SystemMaxUse=200M
SystemMaxFileSize=50M
MaxRetentionSec=1month
```
Then `sudo systemctl restart systemd-journald`.

### Step 3 — Kernel errors since a date

```bash
journalctl -k -p err --since "2024-01-01" > /opt/course/24/kernel-errors.log
```

### Step 4 — Disk usage cap

Either via the conf file above, or one-shot:
```bash
sudo journalctl --vacuum-size=200M
```

### Traditional log files

Even with systemd, classic `/var/log` files often remain (via `rsyslog`):

| File | Content |
|---|---|
| `/var/log/messages` *(RHEL)* / `/var/log/syslog` *(Debian)* | general system messages |
| `/var/log/secure` *(RHEL)* / `/var/log/auth.log` *(Debian)* | authentication, sudo, sshd |
| `/var/log/kern.log` | kernel ring buffer |
| `/var/log/dmesg` | last boot kernel messages |
| `/var/log/audit/audit.log` | auditd (SELinux denials) |
| `/var/log/boot.log` | boot-time messages |

Rotation is handled by `logrotate` — configs under `/etc/logrotate.d/`. Force a run with `sudo logrotate -f /etc/logrotate.conf`.

---

[← Question 23](q23-process-management.md) · [Index](Certifications/LFCS/notes.md) · [Question 25 →](q25-sysctl-kernel-parameters.md)
