# Question 24 — System Logs

## Notes d'apprentissage

Sur un système systemd, le journal centralisé est tenu par **journald**. `journalctl` est l'outil pour l'interroger. Comprendre où vivent les logs et comment les filtrer est indispensable au diagnostic.

**Modèle mental : journald, un journal binaire indexé.**

```
services, noyau, auth... ──► systemd-journald ──► journal binaire
                                                   │
                              journalctl ──────────┘  (filtrer, formater)
```

Contrairement aux vieux fichiers texte de `/var/log`, le journal est **binaire et structuré** : chaque entrée porte des métadonnées (unit, priorité, PID, boot…) qu'on peut filtrer précisément.

**La grande question : volatile ou persistant ?** Par défaut, si `/var/log/journal/` n'existe pas, journald écrit dans `/run/log/journal/` — en **RAM**, donc **perdu au reboot**. Pour conserver les logs entre redémarrages :

```
Storage=volatile   → /run  (RAM, perdu au reboot)
Storage=persistent → /var/log/journal/  (disque, conservé)   ◄── à configurer
Storage=auto       → persistant SI le dossier /var/log/journal existe
```

On crée donc `/var/log/journal/` (ou on met `Storage=persistent` dans `/etc/systemd/journald.conf`) puis on redémarre journald. C'est le cœur de l'exercice.

**Filtrer avec `journalctl` — les axes clés :**
```bash
journalctl -u nginx.service     # par unit
journalctl -b / -b -1           # ce boot / le boot précédent
journalctl -k                   # messages du noyau (= dmesg)
journalctl -p err               # priorité ≤ erreur
journalctl --since "2024-01-01" # par date
journalctl -f                   # suivre en direct (tail -f)
```
Ces filtres se combinent (`-k -p err --since ...`).

**Maîtriser la taille** : le journal peut grossir indéfiniment. `SystemMaxUse=200M` dans la conf, ou `journalctl --vacuum-size=200M` pour purger immédiatement.

**Les fichiers texte coexistent encore** (via `rsyslog`) : `/var/log/syslog` (Debian) ou `/var/log/messages` (RHEL), `/var/log/auth.log` / `/var/log/secure` pour l'authentification. La **rotation** est gérée par `logrotate` (`/etc/logrotate.d/`).

**Pièges** :
- Sans `/var/log/journal/`, les logs disparaissent au reboot — vérifier `journalctl --disk-usage` et le réglage `Storage`.
- Après modif de `journald.conf` : `systemctl restart systemd-journald`.
- Noms de fichiers de log différents Debian/RHEL — voir [[q45-rhel-vs-debian-equivalents]].
- `-b 0` = boot courant, `-b -1` = précédent : utile pour analyser un crash après redémarrage.

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

