---
title: "Reconnaissance (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, reconnaissance, pnpt]
date: "2026-05-18"
---

# Reconnaissance

La reconnaissance, c'est l'étape où on transforme "j'ai une cible" en "j'ai une liste d'IPs, de ports et de services concrets à attaquer". Tout ce qui suit (exploitation, post-exploitation) dépend de la qualité de cette phase. Une recon bâclée = on attaque des fantômes, on rate les vrais points d'entrée.

## Passif vs actif

Deux philosophies, deux niveaux de bruit. Connaître la différence évite de griller son anonymat trop tôt.

```
                          ┌──────────────────────┐
                          │   PHASE DE RECON     │
                          └──────────┬───────────┘
                                     │
              ┌──────────────────────┴──────────────────────┐
              ▼                                             ▼
        PASSIVE                                         ACTIVE
   (rien envoyé à la cible)                  (paquets envoyés à la cible)
              │                                             │
        ┌─────┴─────┐                                ┌──────┴──────┐
        ▼           ▼                                ▼             ▼
   Whois, DNS    Shodan,                       Ping sweep,    Scans Nmap,
   public,       Censys,                       ARP scan,      enumération
   crt.sh        archives                      DNS brute      services
              │                                             │
              ▼                                             ▼
    Indétectable côté cible                Détectable, journalisé
                                            (IDS, WAF, logs)
```

L'OSINT (`04-osint`) est entièrement passif. La reconnaissance active commence ici.

## Découverte d'hôtes

Avant de scanner des ports, il faut savoir quelles machines existent dans la plage cible.

```bash
# Ping sweep — rapide mais ICMP est souvent filtré
nmap -sn 192.168.1.0/24

# ARP scan — sur le réseau local uniquement, mais imparable (couche 2)
arp-scan -l                           # interface par défaut
arp-scan -I eth0 192.168.1.0/24
netdiscover -r 192.168.1.0/24         # passif si pas d'option -p

# Découverte par broadcast (utile en interne)
nmap -sn --send-eth 192.168.1.0/24
```

**Pourquoi ARP scan bat ping sweep en local** : ARP est obligatoire pour communiquer sur Ethernet. Un firewall hôte peut bloquer ICMP, mais ne peut pas bloquer l'ARP sans se déconnecter du réseau.

## Scan de ports

Une fois les hôtes identifiés, on cherche quels services écoutent.

```
Types de scan nmap

-sS    SYN scan (par défaut en root) — envoie SYN, attend SYN-ACK, ne complète pas
       → semi-furtif, pas de connexion complète, rapide

-sT    Connect scan (par défaut sans root) — complète le 3-way handshake
       → bruyant, loggé par le service

-sU    UDP scan — envoie un datagramme UDP, attend "ICMP port unreachable"
       → lent (la cible peut rate-limiter ICMP)

-sn    Ping scan seulement (host discovery, pas de ports)

-sV    Version detection — interroge le service pour identifier exactement quel logiciel/version
-sC    Default scripts — lance les scripts NSE par défaut
-A     Tout activer : -sV -sC -O (OS detect) + traceroute
```

```bash
# Scan rapide initial
nmap -T4 -p- IP                       # tous les ports TCP

# Scan détaillé sur les ports trouvés
nmap -sC -sV -p 22,80,443,3389 IP -oN scan.txt

# UDP — limiter aux ports utiles, sinon trop lent
nmap -sU --top-ports 50 IP

# Furtif (toujours détectable, mais ralenti pour passer sous les seuils IDS)
nmap -T2 -f --data-length 25 IP
```

**À retenir** : `nmap -T4 -p-` d'abord pour avoir la liste, puis `nmap -sC -sV` ciblé sur les ports ouverts. Lancer `-sC -sV -p-` direct est inutilement lent.

## Énumération DNS

```bash
# Lookups basiques
dig cible.com
dig MX cible.com                      # serveurs mail
dig NS cible.com                      # serveurs de noms

# Zone transfer — si autorisé, on récupère toute la zone d'un coup
dig axfr @ns.cible.com cible.com
host -t axfr cible.com ns.cible.com

# Brute force de sous-domaines
dnsenum cible.com
fierce --domain cible.com
gobuster dns -d cible.com -w wordlist.txt
```

**Zone transfer** = misconfig classique. Un DNS qui répond à AXFR depuis n'importe quelle IP donne instantanément toute la cartographie interne. Ça vaut toujours la peine d'essayer.

## Énumération web

```bash
# Identification des technos
whatweb http://IP
nikto -h http://IP                    # scan de vulnérabilités web basiques

# Brute force de répertoires
gobuster dir -u http://IP -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
feroxbuster -u http://IP -w wordlist.txt -d 3        # récursif sur 3 niveaux
ffuf -u http://IP/FUZZ -w wordlist.txt

# Fuzzing de paramètres
ffuf -u "http://IP/page.php?FUZZ=value" -w params.txt -fs SIZE_BASELINE
```

**Pourquoi ffuf/feroxbuster > gobuster aujourd'hui** : plus rapides, meilleur filtrage des faux positifs (option `-fs` pour exclure une taille de réponse, `-fc` pour un code).

## Énumération par service

Une fois un port identifié, on adapte l'outil au service. Voir `06-scanning-enumeration` pour le détail par service (SMB, HTTP, FTP, SSH, DNS, SMTP, SNMP, LDAP, RPC, MSSQL, MySQL, WinRM, NFS, Redis...).

## Workflow type

```
1. OSINT (passif)                → liste de domaines, IPs candidates
2. Découverte d'hôtes            → quelles IPs répondent
3. Scan rapide -p-               → ports ouverts
4. Scan détaillé -sC -sV         → versions, scripts NSE
5. Énumération service-spécifique → endpoints, shares, users
6. Documentation                  → tout dans des fichiers nommés (IP_service.txt)
```

Documenter au fur et à mesure est non négociable. Sur un engagement avec 50 hôtes, on perd vite le fil sans arborescence claire.

## Pièges courants

- **`-p-` est lent** : sur une cible avec firewall, prévoir du temps ou paralléliser plusieurs cibles avec `-iL targets.txt`.
- **Les ports "filtered" ne sont pas "fermés"** : un firewall les drop sans répondre. Parfois un autre type de scan (`-sA` ACK) révèle la règle de filtrage.
- **UDP est piégeux** : "open|filtered" = pas de réponse. Combiner avec des scripts NSE spécifiques au service suspect.
- **Le rate-limiting nmap** : `-T4` est ok sur réseau interne, `-T5` peut perdre des paquets et créer des faux négatifs.
- **Trop scanner = se faire bloquer** : sur des cibles externes, un scan agressif déclenche le WAF/IDS et bannit ton IP. Adapter `-T` et `--max-rate`.
- **Ne jamais oublier IPv6** : `nmap -6 ...`. Beaucoup de cibles ont des services IPv6 non filtrés alors que l'IPv4 est verrouillée.
