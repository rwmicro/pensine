# Question 33 — DNS Server

## Notes d'apprentissage

Le DNS traduit les noms (`web-srv1.lfcs.lan`) en adresses IP. BIND9 est le serveur de référence. Cet exercice combine deux rôles distincts qu'il faut bien séparer dans sa tête.

**Modèle mental : cache vs autorité.**

```
client ──► serveur BIND ┬─► CACHE : interroge l'Internet pour le compte du client,
                        │           mémorise les réponses (résolveur récursif)
                        └─► AUTORITÉ : détient lui-même les zones (lfcs.lan),
                                       répond pour les noms qu'il possède
```

- **Caching-only** : le serveur ne possède aucune zone, il résout récursivement et met en cache. Accélère et mutualise les requêtes du réseau.
- **Master zone** : le serveur fait *autorité* sur un domaine — c'est lui la source de vérité pour `lfcs.lan`.

**Résolution directe vs inverse.** Le DNS répond à deux questions opposées :
- **Directe** (zone normale, enregistrement `A`) : nom → IP (`web-srv1.lfcs.lan` → `192.168.50.10`).
- **Inverse** (zone `in-addr.arpa`, enregistrement `PTR`) : IP → nom. Indispensable pour les logs, le mail, l'authentification.

**Les types d'enregistrements à connaître :**

| Type | Rôle |
|---|---|
| `A` / `AAAA` | nom → IPv4 / IPv6 |
| `PTR` | IP → nom (résolution inverse) |
| `CNAME` | alias d'un autre nom |
| `MX` | serveur de courrier du domaine |
| `NS` | serveurs DNS faisant autorité |
| `SOA` | en-tête de zone (numéro de série, TTL…) |

**Le numéro de série SOA — le piège n°1.** Chaque modification d'un fichier de zone **doit** s'accompagner d'une incrémentation du `serial` dans le SOA, sinon les serveurs secondaires ignorent le changement. Convention : `AAAAMMJJNN`.

**Valider avant de recharger :**
```bash
named-checkconf                       # vérifier la syntaxe de la conf
named-checkzone lfcs.lan /chemin/zone # vérifier un fichier de zone
systemctl reload named  # ou bind9
dig @serveur web-srv1.lfcs.lan        # tester depuis un client
```

**Pièges** :
- Oublier d'incrémenter le `serial` SOA = changements invisibles pour les secondaires.
- Service nommé différemment : `bind9` (Debian) vs `named` (RHEL) ; conf `/etc/bind/` vs `/etc/named.conf`.
- Pour servir un réseau, il faut `listen-on` + `allow-query` corrects, sinon BIND ne répond qu'en local.
- Tester avec `dig` (et non `ping`) : `dig` parle directement au serveur DNS et montre la réponse brute.

## Énoncé

Solve this question on: `data-001`

1. Configure `BIND9` as a **caching-only** DNS server, listening on port 53 of all interfaces.
2. Add a master zone for `lfcs.lan` resolving `web-srv1.lfcs.lan` to `192.168.50.10`.
3. Reverse-resolve `192.168.50.10` to `web-srv1.lfcs.lan`.
4. Verify with `dig` from a remote client and write the answer into `/opt/course/33/lookup`.

## Solution

### Install BIND

```bash
sudo apt install bind9 bind9utils dnsutils       # Debian
sudo dnf install bind bind-utils                  # RHEL (service: named)
```

Config files (Debian paths shown — RHEL uses `/etc/named.conf`):
- `/etc/bind/named.conf` — main include hub
- `/etc/bind/named.conf.options` — global options
- `/etc/bind/named.conf.local` — local zones
- `/var/cache/bind/` (Debian) or `/var/named/` (RHEL) — zone files

### Step 1 — Caching-only options

Edit `/etc/bind/named.conf.options`:
```
options {
    directory "/var/cache/bind";

    listen-on    { any; };
    listen-on-v6 { any; };

    allow-query     { any; };
    allow-recursion { 192.168.50.0/24; localhost; };
    recursion yes;

    forwarders { 1.1.1.1; 9.9.9.9; };
    forward only;

    dnssec-validation auto;
};
```

Check + restart:
```bash
sudo named-checkconf
sudo systemctl restart bind9            # or named on RHEL
sudo systemctl enable bind9
```

### Step 2 — Forward zone

In `/etc/bind/named.conf.local`:
```
zone "lfcs.lan" IN {
    type master;
    file "/etc/bind/db.lfcs.lan";
    allow-update { none; };
};
```

Create `/etc/bind/db.lfcs.lan`:
```
$TTL 3600
@   IN  SOA  ns1.lfcs.lan. admin.lfcs.lan. (
                2026052401  ; serial (YYYYMMDDNN)
                3600        ; refresh
                1800        ; retry
                604800      ; expire
                86400 )     ; minimum TTL
    IN  NS   ns1.lfcs.lan.

ns1      IN  A   192.168.50.1
web-srv1 IN  A   192.168.50.10
```

Validate:
```bash
sudo named-checkzone lfcs.lan /etc/bind/db.lfcs.lan
```

### Step 3 — Reverse zone

```
zone "50.168.192.in-addr.arpa" IN {
    type master;
    file "/etc/bind/db.192.168.50";
};
```

`/etc/bind/db.192.168.50`:
```
$TTL 3600
@   IN  SOA  ns1.lfcs.lan. admin.lfcs.lan. ( 2026052401 3600 1800 604800 86400 )
    IN  NS   ns1.lfcs.lan.

10  IN  PTR  web-srv1.lfcs.lan.
```

Reload:
```bash
sudo named-checkzone 50.168.192.in-addr.arpa /etc/bind/db.192.168.50
sudo systemctl reload bind9
```

### Step 4 — Verification

```bash
dig @192.168.50.1 web-srv1.lfcs.lan +short
dig @192.168.50.1 -x 192.168.50.10 +short
dig @192.168.50.1 web-srv1.lfcs.lan > /opt/course/33/lookup
```

### Common DNS record types

| Type | Purpose |
|---|---|
| `A` | IPv4 address |
| `AAAA` | IPv6 address |
| `CNAME` | alias to another name |
| `MX` | mail exchanger (with priority) |
| `NS` | name server for the zone |
| `PTR` | reverse pointer |
| `SOA` | start of authority |
| `TXT` | free text (SPF, DKIM, verification) |
| `SRV` | service location (with port + priority) |

### `/etc/resolv.conf` and resolution order

`/etc/nsswitch.conf` controls the order:
```
hosts: files dns
```
- `files` → `/etc/hosts`
- `dns` → servers from `/etc/resolv.conf`

`/etc/resolv.conf` is often managed by `systemd-resolved` or NetworkManager — edit via those, not directly.

### Alternative: `dnsmasq` for a small caching server

```bash
sudo apt install dnsmasq
# /etc/dnsmasq.conf
listen-address=192.168.50.1
domain=lfcs.lan
expand-hosts
server=1.1.1.1
# /etc/hosts is automatically served
sudo systemctl restart dnsmasq
```

