---
title: Network Forensics
domain: sciences-appliquées
subdomain: informatique / sécurité / dfir
tags: [forensics, réseau, dfir, pcap, wireshark, investigation, sécurité]
date: 2026-03-22
---

# Network Forensics

L'analyse forensique réseau consiste à capturer, préserver et analyser le trafic réseau pour reconstituer des événements, détecter des intrusions, et identifier des exfiltrations de données.

## Capture de trafic

### tcpdump

```bash
# Capture basique
tcpdump -i eth0 -w capture.pcap

# Avec un filtre
tcpdump -i eth0 -w capture.pcap 'host 192.168.1.10'
tcpdump -i eth0 -w capture.pcap 'port 443'
tcpdump -i eth0 -w capture.pcap 'tcp and not port 22'

# Taille de fichier limitée — rotation
tcpdump -i eth0 -w capture_%Y%m%d_%H%M%S.pcap -G 3600  # Rotation toutes les heures
tcpdump -i eth0 -w capture.pcap -C 100                  # Nouveau fichier tous les 100 Mo

# Capture complète avec snaplen
tcpdump -i eth0 -s 0 -w capture.pcap                    # -s 0 = paquets complets (pas de troncation)

# Afficher sans fichier (analyse en direct)
tcpdump -i eth0 -n -v 'tcp[tcpflags] & tcp-syn != 0'   # SYN packets (tentatives de connexion)
```

### Wireshark (GUI et tshark)

```bash
# tshark — Wireshark en ligne de commande
tshark -r capture.pcap -Y "http.request"                # Requêtes HTTP
tshark -r capture.pcap -Y "dns"                         # Trafic DNS
tshark -r capture.pcap -Y "tcp.flags.syn==1"            # Paquets SYN

# Extraire des champs spécifiques
tshark -r capture.pcap -Y "http.request" \
    -T fields -e http.host -e http.request.uri -e ip.src

# Statistiques
tshark -r capture.pcap -q -z conv,tcp        # Conversations TCP
tshark -r capture.pcap -q -z io,phs          # Hiérarchie des protocoles
tshark -r capture.pcap -q -z endpoints,ip    # Endpoints IP

# Extraire des fichiers HTTP (fichiers transférés)
tshark -r capture.pcap --export-objects http,/tmp/exported/
```

## Analyse Wireshark — filtres de display essentiels

```
# Trafic par hôte
ip.addr == 192.168.1.10
ip.src == 10.0.0.1
ip.dst == 8.8.8.8

# Protocoles
http
dns
ftp
smtp
tls

# Ports
tcp.port == 443
udp.port == 53

# Flags TCP
tcp.flags.syn == 1 && tcp.flags.ack == 0    # SYN (nouvelles connexions)
tcp.flags.reset == 1                          # RST (connexions réinitialisées)
tcp.flags.fin == 1                            # FIN (connexions fermées)

# Patterns suspects
tcp.analysis.retransmission                   # Retransmissions (instabilité/scan)
tcp.analysis.zero_window                      # Saturation buffer

# Rechercher du contenu
frame contains "password"
http contains "login"
dns.qry.name contains "attaquant"

# Combinaisons
http.request.method == "POST" && http.request.uri contains "login"
dns.qry.type == 1 && dns.qry.name matches ".*\.ru$"   # Requêtes DNS vers .ru
```

## Analyse de captures — scénarios courants

### Exfiltration DNS

```bash
# Requêtes DNS anormalement longues = tunneling potentiel
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name |
    awk '{print length($0), $0}' | sort -rn | head -20

# Fréquence élevée vers un domaine = tunneling ou DGA
tshark -r capture.pcap -Y "dns.qry.type==1" -T fields -e dns.qry.name |
    awk -F'.' '{print $(NF-1)"."$NF}' | sort | uniq -c | sort -rn | head -20

# Sous-domaines avec encodage base32/64 (caractères inhabituels)
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name |
    grep -E "[a-z0-9]{30,}"  # Sous-domaines de plus de 30 caractères
```

### Scan de ports

```bash
# Détecter un scan Nmap (SYN scan)
# Beaucoup de SYN vers différents ports depuis une même IP
tshark -r capture.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0" \
    -T fields -e ip.src -e tcp.dstport |
    sort | uniq -c | sort -rn

# Connexions RST en réponse = port fermé (scan SYN)
# SYN+ACK en réponse = port ouvert

# Scan ICMP (ping sweep)
tshark -r capture.pcap -Y "icmp.type==8" -T fields -e ip.dst |
    sort | uniq -c | sort -rn
```

### Exfiltration HTTP/HTTPS

```bash
# Volumes de données par IP (exfiltration = upload important)
tshark -r capture.pcap -q -z conv,tcp | grep -E "[0-9]+ bytes" |
    sort -k5 -rn | head -20

# Requêtes HTTP POST volumineuses
tshark -r capture.pcap -Y "http.request.method==POST" \
    -T fields -e ip.src -e http.host -e http.request.uri -e http.content_length

# User-Agent suspects
tshark -r capture.pcap -Y "http" -T fields -e http.user_agent |
    sort | uniq -c | sort -rn

# Fichiers téléchargés via HTTP (reconstitution)
tshark -r capture.pcap --export-objects http,/tmp/http_files/
```

### C2 (Command & Control)

```bash
# Connexions périodiques régulières (beaconing)
# Trafic toutes les X secondes vers la même IP = C2 potentiel
tshark -r capture.pcap -Y "ip.dst == 203.0.113.1" \
    -T fields -e frame.time_relative -e ip.len |
    awk '{diff=$1-prev; prev=$1; print diff}' |
    sort | uniq -c | sort -rn

# Connexions sortantes sur des ports inhabituels
tshark -r capture.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0" \
    -T fields -e ip.dst -e tcp.dstport |
    grep -v " 80\| 443\| 53\| 22\| 25\| 587" | sort | uniq -c | sort -rn

# TLS avec des certificats auto-signés ou suspects
# Extraire les SNI (Server Name Indication) des connexions TLS
tshark -r capture.pcap -Y "tls.handshake.type==1" \
    -T fields -e ip.dst -e tls.handshake.extensions_server_name
```

## Zeek (anciennement Bro)

Zeek est un analyseur de protocoles réseau qui génère des logs structurés à partir de captures.

```bash
# Analyser un pcap avec Zeek
zeek -r capture.pcap

# Fichiers générés :
# conn.log    → toutes les connexions (IP src/dst, ports, durée, octets)
# dns.log     → requêtes DNS
# http.log    → requêtes HTTP
# files.log   → fichiers transférés
# ssl.log     → connexions TLS (SNI, certificat, JA3)
# weird.log   → anomalies détectées

# Analyser conn.log
cat conn.log | zeek-cut id.orig_h id.resp_h id.resp_p proto duration orig_bytes |
    sort -k6 -rn | head  # Top connexions par volume

# JA3 fingerprinting (empreinte du client TLS)
cat ssl.log | zeek-cut ja3 ja3s server_name |
    sort | uniq -c | sort -rn
# JA3 permet d'identifier le type de client (Metasploit, Cobalt Strike ont leurs signatures)
```

## Suricata — NIDS sur PCAP

```bash
# Analyser un pcap avec les règles Suricata
suricata -r capture.pcap -l /tmp/suricata_output/ -c /etc/suricata/suricata.yaml

# Examiner les alertes
cat /tmp/suricata_output/fast.log
cat /tmp/suricata_output/eve.json | jq 'select(.event_type=="alert")'

# Règle Suricata exemple (détection de beaconing toutes les 60s)
alert tcp any any -> any any (
    msg:"Possible C2 Beaconing";
    detection_filter:track by_src,count 5,seconds 300;
    sid:9999001;
)
```

## NetworkMiner — Extraction de fichiers

```bash
# Extraire automatiquement les fichiers, credentials, et sessions
# NetworkMiner (GUI) : File > Open > capture.pcap
# → Onglet Files : tous les fichiers transférés
# → Onglet Credentials : identifiants HTTP, FTP, SMTP en clair
# → Onglet Sessions : reconstruction des sessions

# En ligne de commande (alternative)
foremost -i capture.pcap -o /tmp/extracted/     # Extraction par magic bytes
```

## Artefacts réseau sur un hôte

```bash
# Connexions actives et en écoute
ss -tulnp
netstat -antp

# Table ARP — machines sur le réseau local
arp -a
ip neigh

# Table de routage
ip route
route -n

# Connexions DNS récentes (cache)
systemd-resolve --statistics
resolvectl statistics

# Connexions récentes (non temps réel)
# /proc/net/tcp  → connexions TCP actives (adresses en hex)
cat /proc/net/tcp | awk '{print $2, $3, $4}'
# Format : adresse_locale:port_local adresse_distante:port_distant état

# Convertir hex vers IP
python3 -c "
import socket, struct
def hex_to_ip(hex_str):
    ip = struct.pack('<I', int(hex_str, 16))
    return socket.inet_ntoa(ip)
print(hex_to_ip('0101007F'))  # 127.0.1.1
"
```
