---
title: Forensique Réseau
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [forensique, réseau, wireshark, tcpdump, pcap, network-forensics, dfir, sécurité]
date: 2026-03-23
---

# Forensique Réseau

La forensique réseau consiste à capturer, enregistrer et analyser le trafic réseau pour détecter des incidents, reconstituer des attaques, ou extraire des artefacts. Elle est complémentaire à la forensique système (mémoire, disque).

## Capture de trafic

### tcpdump — Capture en ligne de commande

```bash
# Capture basique sur une interface
tcpdump -i eth0

# Avec résolution de noms désactivée (plus rapide, IPs brutes)
tcpdump -i eth0 -n

# Sauvegarder dans un fichier PCAP
tcpdump -i eth0 -w capture.pcap

# Avec horodatage précis
tcpdump -i eth0 -w capture.pcap -tttt

# Limiter la taille des fichiers (rotation)
tcpdump -i eth0 -w capture-%Y%m%d%H%M.pcap -G 3600 -C 100

# Capturer toutes les interfaces
tcpdump -i any -w all_interfaces.pcap

# Filtres BPF (Berkeley Packet Filter)
tcpdump -i eth0 host 192.168.1.50           # Trafic vers/depuis une IP
tcpdump -i eth0 src 192.168.1.50            # Seulement depuis cette IP
tcpdump -i eth0 dst 8.8.8.8                 # Seulement vers cette IP
tcpdump -i eth0 port 443                    # Seulement le port 443
tcpdump -i eth0 tcp                         # Seulement TCP
tcpdump -i eth0 udp port 53                 # DNS (UDP 53)
tcpdump -i eth0 net 192.168.0.0/16          # Tout un sous-réseau
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'  # Paquets SYN uniquement

# Combinaisons
tcpdump -i eth0 'host 192.168.1.50 and (port 80 or port 443)'
tcpdump -i eth0 'not port 22 and not host 192.168.1.1'

# Afficher le contenu ASCII des paquets
tcpdump -i eth0 -A port 80
tcpdump -i eth0 -X port 80   # Hex + ASCII
```

### Wireshark — Analyse graphique

```
Filtres d'affichage Wireshark (display filters) :
  (différents des filtres BPF de tcpdump)

  ip.addr == 192.168.1.50             → Trafic d'une IP
  ip.src == 192.168.1.50              → Source spécifique
  tcp.port == 443                     → Port TCP 443
  http                                → Tout le trafic HTTP
  http.request.method == "POST"       → Seulement les POST HTTP
  dns                                 → Trafic DNS
  dns.qry.name contains "evil"        → Requêtes DNS contenant "evil"
  tcp.flags.syn == 1 && tcp.flags.ack == 0  → Paquets SYN (début de connexion)
  tcp.flags.rst == 1                  → Paquets RST (reset)
  frame.len > 1400                    → Gros paquets (exfiltration ?)
  http.response.code == 200           → Réponses HTTP 200
  ssl.handshake.type == 1             → Client Hello TLS
  smb || smb2                         → Trafic SMB

Raccourcis utiles :
  Ctrl+Shift+F → Find packet (chercher dans le contenu)
  Ctrl+Alt+Shift+T → Follow TCP Stream → reconstituer une conversation
  Statistiques → Protocol Hierarchy → vue globale des protocoles
  Statistiques → Conversations → liste des flux TCP/UDP/IP
  Statistiques → IO Graph → graphe du volume de trafic dans le temps
  Analyse → Expert Information → anomalies détectées automatiquement
```

### tshark — Wireshark en ligne de commande

```bash
# Analyser un PCAP avec des filtres display Wireshark
tshark -r capture.pcap -Y "http.request.method == POST"

# Extraire des champs spécifiques
tshark -r capture.pcap -Y "http" -T fields -e ip.src -e ip.dst -e http.host -e http.request.uri

# Statistiques de conversations
tshark -r capture.pcap -q -z conv,tcp

# Top des protocoles
tshark -r capture.pcap -q -z io,phs

# Extraire les flux HTTP
tshark -r capture.pcap -Y "http.request" \
    -T fields -e ip.src -e ip.dst -e http.request.method -e http.request.full_uri

# Exporter des objets HTTP (fichiers téléchargés)
tshark -r capture.pcap --export-objects http,/tmp/http_objects/
```

## Analyse d'incidents — Patterns

### Scan de ports

```bash
# Wireshark — détecter un scan nmap
# tcp.flags.syn == 1 && tcp.flags.ack == 0    → SYN scan
# icmp.type == 3 && icmp.code == 3            → UDP scan (port unreachable)
# tcp.flags == 0x000                          → NULL scan
# tcp.flags == 0x029                          → XMAS scan (FIN+PSH+URG)

# tshark — trouver une source envoyant des SYN vers de nombreux ports distincts
tshark -r capture.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0" \
    -T fields -e ip.src -e ip.dst -e tcp.dstport | sort | uniq -c | sort -rn | head -20
```

### Exfiltration DNS

```bash
# DNS tunneling — caractéristiques :
#   → Requêtes DNS très fréquentes
#   → Noms de domaine très longs (> 60 caractères dans le sous-domaine)
#   → Haute entropie dans les sous-domaines (base64, hex)
#   → Beaucoup de requêtes vers le même domaine racine

# Wireshark
dns && dns.qry.name.len > 50                  # Requêtes longues
dns && dns.qry.type == 16                     # Requêtes TXT (souvent utilisées pour C2)

# tshark — extraire les noms DNS suspects
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name | \
    awk '{print length, $0}' | sort -rn | head -20

# Calculer l'entropie des sous-domaines (haut = suspect)
tshark -r capture.pcap -Y "dns.qry.type == 1" -T fields -e dns.qry.name | \
    python3 -c "
import sys, math, collections
for line in sys.stdin:
    sub = line.split('.')[0]
    freq = collections.Counter(sub)
    entropy = -sum(f/len(sub)*math.log2(f/len(sub)) for f in freq.values())
    if entropy > 3.5 and len(sub) > 20:
        print(f'{entropy:.2f} {line.strip()}')
" | sort -rn | head -20
```

### Beaconing C2

```bash
# Beaconing — connexions HTTP/HTTPS périodiques vers un C2
# Caractéristiques :
#   → Intervalles réguliers (± jitter)
#   → Même User-Agent, même taille de requête
#   → URI aléatoires ou fixes
#   → Petites quantités de données échangées

# tshark — trouver des connexions périodiques
tshark -r capture.pcap -Y "http.request" \
    -T fields -e frame.time -e ip.dst -e http.host -e http.request.uri | \
    sort -k3 | awk '{print $1, $3}'   # Grouper par host, analyser les intervalles

# RITA — Real Intelligence Threat Analytics (outil dédié)
# Analyse automatique du beaconing
rita import capture.pcap db_name
rita show-beacons db_name | head -20

# Zeek (anciennement Bro) — analyse comportementale
zeek -r capture.pcap local
cat conn.log | zeek-cut id.orig_h id.resp_h id.resp_p proto duration | sort | head -20
```

### Credentials en clair

```bash
# HTTP Basic Auth (base64 dans le header Authorization)
tshark -r capture.pcap -Y "http.authorization" \
    -T fields -e ip.src -e http.authorization | \
    while read ip auth; do
        echo "IP: $ip, Creds: $(echo ${auth#Basic } | base64 -d)"
    done

# FTP credentials
tshark -r capture.pcap -Y "ftp" -T fields -e ip.src -e ftp.request.command -e ftp.request.arg

# Telnet (interactif, reconstituer le flux)
# Wireshark → Follow TCP Stream → sur une connexion port 23

# SMTP credentials
tshark -r capture.pcap -Y "smtp" -T fields -e smtp.req.command -e smtp.req.parameter

# LDAP Bind (credentials)
tshark -r capture.pcap -Y "ldap.bindRequest" \
    -T fields -e ip.src -e ldap.name -e ldap.simple
```

## Extraction d'artefacts

```bash
# Extraire des fichiers d'un PCAP (Wireshark)
# File → Export Objects → HTTP/SMB/DICOM/...

# NetworkMiner — extraction automatique d'artefacts
wine NetworkMiner.exe -r capture.pcap

# Xplico — reconstruction des sessions applicatives
# Supporte HTTP, email (POP3/IMAP/SMTP), VoIP, FTP

# Extraire les certificats TLS
tshark -r capture.pcap -Y "ssl.handshake.certificate" \
    -T fields -e ssl.handshake.certificate > certs.hex
# Ou via Wireshark : Statistics → Endpoint Lists → TLS

# Extraire les hachages des credentials NTLM (pour cracking)
# Pcredz — extraction automatique de credentials depuis des PCAPs
python3 Pcredz.py -f capture.pcap
# → Extrait NTLM hashes, Kerberos tickets, HTTP basic auth, FTP, telnet...

# Volatility plugin NetworkConnections (si dump mémoire disponible)
vol.py -f memory.dmp windows.netstat
```

## Zeek — Analyse comportementale

```bash
# Zeek génère des logs structurés (JSON ou TSV) par type de trafic
zeek -r capture.pcap local

# Logs principaux générés :
# conn.log      : toutes les connexions (IP, port, durée, bytes)
# dns.log       : requêtes DNS
# http.log      : requêtes HTTP (URL, méthode, user-agent, code réponse)
# ssl.log       : sessions TLS (SNI, certificat, version)
# files.log     : fichiers transférés
# notice.log    : détections d'anomalies

# Analyser les connexions longues (C2, exfiltration)
cat conn.log | zeek-cut id.orig_h id.resp_h id.resp_p duration orig_bytes | \
    sort -k4 -rn | head -20

# User-Agents inhabituels
cat http.log | zeek-cut user_agent | sort | uniq -c | sort -rn | head -20

# JA3 fingerprinting TLS (identifier les clients par leur handshake TLS)
cat ssl.log | zeek-cut ja3 ja3s | sort | uniq -c | sort -rn | head -10
# Comparer avec la base ja3er.com pour identifier des malwares connus

# Détection de DNS over HTTPS (DoH)
cat dns.log | zeek-cut query | grep -E "cloudflare-dns|dns.google|1.1.1.1"
```

## Contre-mesures côté défenseur

```
Déploiement de la capture réseau :
  ✓ Full packet capture sur les liens critiques (TAP ou SPAN port)
  ✓ NetFlow/IPFIX pour une vue légère sur tout le réseau (moins de détail, plus de volume)
  ✓ Rétention : 7 à 30 jours pour les PCAPs, 90+ jours pour les métadonnées (NetFlow)

Outils de détection temps réel :
  ✓ Suricata / Snort : IDS/IPS avec règles Emerging Threats
  ✓ Zeek : analyse comportementale
  ✓ RITA : beaconing, long connections, DNS anomalies
  ✓ Arkime (Moloch) : full packet capture + interface de recherche

Chiffrement et détection :
  ✓ TLS inspection (SSL bumping) sur les proxies sortants
  ✓ Analyse des métadonnées TLS (JA3, SNI, certificat) même sans déchiffrement
  ✓ DNS : déployer un resolver interne loggé, bloquer le DNS direct vers internet
  ✓ DNS over HTTPS : forcer le passage par le resolver interne (bloquer DoH externe)
```
