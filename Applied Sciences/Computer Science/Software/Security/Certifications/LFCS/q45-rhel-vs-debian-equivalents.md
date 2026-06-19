# Question 45 — RHEL vs Debian Equivalents

## Notes d'apprentissage

L'examen LFCS laisse **choisir la distribution**. La plupart des notes ici utilisent l'outillage Debian/Ubuntu ; sur la famille RHEL (Rocky, AlmaLinux, Fedora…), plusieurs outils centraux diffèrent. Cette note est la carte de correspondance — savoir traduire une question d'une famille à l'autre.

**Modèle mental : ce qui change vs ce qui est identique.**

```
IDENTIQUE partout (systemd) :  systemctl  journalctl  ip  ss  sysctl  LVM  mdadm  nmcli
DIFFÉRENT selon la famille  :  paquets · pare-feu · synchro temps · MAC · réseau
```

Bonne nouvelle : tout ce qui repose sur systemd et le noyau est **commun**. Les différences se concentrent sur quelques sous-systèmes — c'est là qu'il faut connaître les deux.

**Les correspondances à mémoriser :**

| Domaine | Debian/Ubuntu | RHEL/Fedora |
|---|---|---|
| Paquets | `apt` / `dpkg` | `dnf` / `rpm` |
| Pare-feu (façade) | `ufw` / `iptables` | `firewalld` (`firewall-cmd`) |
| Filtrage (backend) | `nftables` / `iptables` | `nftables` / `iptables-nft` |
| Synchro temps | `systemd-timesyncd` | `chronyd` (`chronyc`) |
| MAC | AppArmor (`aa-status`) | SELinux (`getenforce`) |
| Réseau | `netplan` / `ifupdown` | NetworkManager (`nmcli`) |
| initramfs | `update-initramfs -u` | `dracut -f` |

**Trois pièges de traduction les plus fréquents :**

1. **`firewalld` ≠ iptables direct.** Il est *zone-based* : `--permanent` écrit la config mais n'agit qu'après `--reload`. Sans `--permanent`, la règle est *runtime* (perdue au reload/reboot). `--runtime-to-permanent` fige ce qu'on a testé à chaud.

2. **`chrony` au lieu de `timesyncd`** (voir [[q03-time-synchronisation-configuration]]) : conf dans `/etc/chrony.conf`, `iburst` accélère la sync initiale, diagnostic avec `chronyc sources`/`tracking`. `timedatectl` reste commun aux deux.

3. **`nftables` remplace `iptables`** (voir [[q07-network-packet-filtering]]) : syntaxe unifiée table/chaîne, commande `nft`. Sur les systèmes récents, `iptables` est souvent un *shim* `iptables-nft` qui traduit vers nftables — les vieilles règles marchent encore.

**Le pont portable : `nmcli`.** NetworkManager est disponible sur les **deux** familles : c'est la façon la plus universelle de configurer le réseau de manière persistante (voir [[q31-network-configuration]]).

**Stratégie d'examen** : choisir la distribution qu'on maîtrise le mieux, mais savoir reconnaître quand une question suppose implicitement l'autre famille (chemins, noms de services).

## Énoncé

Solve this question on: `data-001` (RHEL family)

The killer.sh simulator and most of these notes use Debian/Ubuntu tooling (`apt`, `iptables`, `systemd-timesyncd`). The real LFCS exam lets you pick your distribution, and on the **RHEL family** (Rocky/AlmaLinux/CentOS/Fedora) several core tools differ. This note collects the equivalents so a question phrased for one family can be solved on the other.

1. Add a persistent NTP server using the RHEL default time daemon.
2. Open TCP port `8080` permanently in the host firewall using `firewalld`.
3. Write a single `nftables` rule that drops inbound TCP `23`.

## Solution

### Step 1 — Time sync with chrony (RHEL default)

On RHEL the time daemon is **`chronyd`**, configured in `/etc/chrony.conf` (Debian uses `systemd-timesyncd` — see [q03](q03-time-synchronisation-configuration.md)).

```bash
# add a server line (drop-in keeps the main file clean)
echo "server 0.pool.ntp.org iburst" | sudo tee -a /etc/chrony.conf
sudo systemctl restart chronyd

chronyc sources -v                  # peers and their state
chronyc tracking                    # current offset / drift
timedatectl                         # confirms "NTP service: active"
```

`iburst` speeds up the initial sync. `timedatectl set-ntp true` enables NTP regardless of which daemon backs it.

### Step 2 — firewalld (RHEL default firewall front-end)

RHEL ships **`firewalld`** (zone-based) instead of raw `iptables`/`ufw`. It is backed by `nftables` on modern releases.

```bash
sudo firewall-cmd --state
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --list-all                     # rules of the default zone

# open a port — --permanent writes config, then reload to apply
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload

# services by name, and a quick check
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
sudo firewall-cmd --query-port=8080/tcp
```

Key rule: changes without `--permanent` are **runtime only** (lost on reload/reboot); changes with `--permanent` need `--reload` to take effect now. Use `--runtime-to-permanent` to persist what you tested live.

### Step 3 — nftables (modern replacement for iptables)

`nftables` (command `nft`) supersedes the `iptables` of [q07](q07-network-packet-filtering.md). It uses a single unified table/chain syntax.

```bash
# create table + base chain, then add the drop rule
sudo nft add table inet filter
sudo nft add chain inet filter input '{ type filter hook input priority 0 ; policy accept ; }'
sudo nft add rule inet filter input tcp dport 23 drop

sudo nft list ruleset               # show everything
```

Persist the ruleset:
```bash
sudo nft list ruleset | sudo tee /etc/nftables.conf
sudo systemctl enable --now nftables
```

The `iptables` command on RHEL 8+/Debian 11+ is usually the `iptables-nft` shim that translates to nftables under the hood, so old rules still work.

---

## Cross-distribution cheat sheet

| Task | Debian / Ubuntu | RHEL / Fedora |
|---|---|---|
| Package install | `apt install X` | `dnf install X` |
| Search / who-owns | `apt-cache search`, `dpkg -S` | `dnf search`, `dnf provides` / `rpm -qf` |
| List pkg files | `dpkg -L X` | `rpm -ql X` |
| Hold/lock a pkg | `apt-mark hold X` | `dnf versionlock add X` (plugin) |
| Add software repo | `/etc/apt/sources.list.d/` | `/etc/yum.repos.d/` |
| Firewall | `ufw` / `iptables` | `firewalld` (`firewall-cmd`) |
| Packet filter backend | `nftables` / `iptables` | `nftables` / `iptables-nft` |
| Time sync | `systemd-timesyncd` | `chronyd` (`chronyc`) |
| MAC security | AppArmor (`aa-status`) | SELinux (`getenforce`) — see [q44](q44-selinux-and-apparmor.md) |
| Network config | `netplan` / `ifupdown` | NetworkManager (`nmcli`) |
| initramfs rebuild | `update-initramfs -u` | `dracut -f` |
| Default web root | `/var/www/html` | `/var/www/html` (same) |
| Network tool pkg name | `net-tools`, `dnsutils` | `net-tools`, `bind-utils` |

> `nmcli` (NetworkManager) is available on both families and is the most portable way to configure interfaces persistently — see [q31](q31-network-configuration.md). `systemctl`, `journalctl`, `ip`, `ss`, `sysctl`, LVM, and `mdadm` are identical across distributions.
