# Question 45 — RHEL vs Debian Equivalents

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
