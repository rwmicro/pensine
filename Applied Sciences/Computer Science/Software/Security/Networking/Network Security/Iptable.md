---
title: "iptables / nftables"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2025-03-08"
---

# iptables / nftables

iptables est l'interface traditionnelle pour configurer le pare-feu Netfilter du noyau Linux. nftables est son successeur depuis Linux 3.13 (2014), maintenant par défaut dans Debian 10+, RHEL 8+, Arch Linux.

## Architecture Netfilter

```
Paquet entrant → PREROUTING → Routage → INPUT → Processus local
                                  ↓
                              FORWARD → Sortie
                                  ↓
                 Processus local → OUTPUT → POSTROUTING → Sortie réseau
```

### Tables

| Table | Chaînes | Usage |
|-------|---------|-------|
| **filter** (défaut) | INPUT, OUTPUT, FORWARD | Filtrage des paquets |
| **nat** | PREROUTING, OUTPUT, POSTROUTING | Translation d'adresses |
| **mangle** | Toutes | Modification des paquets (TTL, TOS) |
| **raw** | PREROUTING, OUTPUT | Contournement du suivi de connexion |
| **security** | INPUT, OUTPUT, FORWARD | Marquage SELinux |

### Chaînes et flux de paquets

- **INPUT** : paquets destinés à la machine locale
- **OUTPUT** : paquets émis par la machine locale
- **FORWARD** : paquets traversant la machine (routage)
- **PREROUTING** : avant le routage (modification de destination)
- **POSTROUTING** : après le routage (modification de source)

## iptables — Syntaxe de base

### Commandes

```bash
# Lister les règles
iptables -L                    # Table filter, format lisible
iptables -L -v                 # Avec compteurs paquets/bytes
iptables -L -n                 # Format numérique (pas de DNS lookup)
iptables -L -n --line-numbers  # Avec numéros de ligne
iptables -t nat -L -n -v       # Table NAT

# Politique par défaut
iptables -P INPUT DROP         # Tout bloquer par défaut
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Ajouter une règle (fin de chaîne)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Insérer une règle (position spécifique)
iptables -I INPUT 1 -i lo -j ACCEPT  # Règle 1 = loopback

# Supprimer une règle
iptables -D INPUT -p tcp --dport 22 -j ACCEPT
iptables -D INPUT 3  # Par numéro de ligne

# Vider une chaîne
iptables -F INPUT   # Flush
iptables -F         # Toutes les chaînes

# Sauvegarder et restaurer
iptables-save > /etc/iptables/rules.v4
iptables-restore < /etc/iptables/rules.v4

# Systemd (Debian/Ubuntu)
# Via /etc/iptables/rules.v4 + iptables-persistent
apt install iptables-persistent
netfilter-persistent save
```

## Filtrage stateful (conntrack)

Le module `state` (ou `conntrack`) suit l'état des connexions. C'est le cœur d'un firewall moderne.

| État | Description |
|------|-------------|
| NEW | Première paquet d'une nouvelle connexion |
| ESTABLISHED | Connexion déjà établie (dans les deux sens) |
| RELATED | Connexion liée (ex: FTP data, ICMP errors) |
| INVALID | Paquet ne correspondant à aucun état connu |

```bash
# Permettre les connexions établies (retour du trafic légitime)
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Bloquer les paquets invalides
iptables -A INPUT -m conntrack --ctstate INVALID -j DROP
```

## Configuration firewall type (serveur)

```bash
#!/bin/bash
# Réinitialiser
iptables -F
iptables -X
iptables -t nat -F
iptables -t mangle -F

# Politique par défaut : tout bloquer
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Loopback (localhost)
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Connexions établies (réponses aux sorties)
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# SSH depuis IP spécifique
iptables -A INPUT -p tcp -s 192.168.1.100 --dport 22 -m conntrack --ctstate NEW -j ACCEPT

# SSH depuis n'importe où (moins sécurisé)
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT

# Web
iptables -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -m conntrack --ctstate NEW -j ACCEPT

# DNS (si serveur DNS)
iptables -A INPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT -p tcp --dport 53 -j ACCEPT

# ICMP ping (limité)
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT

# Bloquer paquets invalides
iptables -A INPUT -m conntrack --ctstate INVALID -j DROP

# Log les paquets bloqués (avant la politique DROP)
iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables BLOCKED: " --log-level 4
```

## Spécifications de protocoles et ports

```bash
# TCP
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --sport 80 -j ACCEPT

# UDP
iptables -A INPUT -p udp --dport 53 -j ACCEPT

# Plage de ports
iptables -A INPUT -p tcp --dport 8000:9000 -j ACCEPT

# Ports multiples
iptables -A INPUT -p tcp -m multiport --dports 80,443,8080 -j ACCEPT

# Interface réseau
iptables -A INPUT -i eth0 -j ACCEPT
iptables -A OUTPUT -o eth0 -j ACCEPT

# Adresse source/destination
iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -d 10.0.0.1 -j ACCEPT
```

## Rate limiting et protection anti-scan/DDoS

```bash
# Limiter les nouvelles connexions SSH (max 3/min par IP)
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW \
    -m recent --set --name SSH
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW \
    -m recent --update --seconds 60 --hitcount 4 --name SSH -j DROP

# Protection SYN flood
iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP

# Rate limiting global
iptables -A INPUT -m limit --limit 100/second --limit-burst 200 -j ACCEPT

# Bloquer les scans de ports (NULL, FIN, Xmas)
iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP    # NULL scan
iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP     # Xmas scan
iptables -A INPUT -p tcp --tcp-flags ALL FIN,PSH,URG -j DROP  # Xmas variant

# Protection PING flood
iptables -A INPUT -p icmp -m icmp --icmp-type echo-request \
    -m limit --limit 1/s -j ACCEPT
iptables -A INPUT -p icmp -m icmp --icmp-type echo-request -j DROP
```

## NAT (Network Address Translation)

```bash
# MASQUERADE — Partager la connexion internet d'une interface
# (IP source dynamique → adapte automatiquement)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
echo 1 > /proc/sys/net/ipv4/ip_forward

# SNAT — Remplacer l'IP source par une IP fixe
iptables -t nat -A POSTROUTING -o eth0 -j SNAT --to-source 203.0.113.1

# DNAT — Port forwarding (rediriger le port 80 externe vers un serveur interne)
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 192.168.1.10:8080

# Redirection locale (port 80 → 8080 sur la même machine)
iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8080
```

## Logging

```bash
# Logger avec préfixe
iptables -A INPUT -j LOG --log-prefix "INPUT DROP: " --log-level 4

# Limiter le logging (éviter le flood de logs)
iptables -A INPUT -m limit --limit 5/min --limit-burst 10 \
    -j LOG --log-prefix "iptables: "

# Voir les logs
dmesg | grep "iptables:"
tail -f /var/log/kern.log | grep iptables
```

## nftables — Le successeur

nftables remplace iptables avec une syntaxe unifiée et plus puissante.

```bash
# Installation
apt install nftables
systemctl enable --now nftables

# Conversion automatique
iptables-translate -A INPUT -p tcp --dport 22 -j ACCEPT
# → nft add rule ip filter INPUT tcp dport 22 accept

iptables-restore-translate -f /etc/iptables/rules.v4 > /etc/nftables.conf
```

### Syntaxe nftables

```
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;

        # Loopback
        iif lo accept

        # Connexions établies
        ct state established,related accept
        ct state invalid drop

        # SSH
        tcp dport 22 ct state new accept

        # Web
        tcp dport { 80, 443 } ct state new accept

        # ICMP/ICMPv6
        ip protocol icmp icmp type echo-request limit rate 1/second accept
        ip6 nexthdr icmpv6 accept

        # Log et drop par défaut
        log prefix "nft drop: " flags all
    }

    chain forward {
        type filter hook forward priority 0; policy drop;
    }

    chain output {
        type filter hook output priority 0; policy accept;
    }
}

table ip nat {
    chain prerouting {
        type nat hook prerouting priority -100;
        tcp dport 80 dnat to 192.168.1.10:8080
    }
    chain postrouting {
        type nat hook postrouting priority 100;
        oif eth0 masquerade
    }
}
```

```bash
# Appliquer les règles
nft -f /etc/nftables.conf

# Lister les règles
nft list ruleset

# Ajouter une règle
nft add rule inet filter input tcp dport 8080 accept

# Voir les statistiques
nft list ruleset | grep -A2 "counter"
```

## UFW — Interface simplifiée (Ubuntu)

UFW (Uncomplicated Firewall) est une interface haut niveau pour iptables, idéale pour les serveurs simples.

```bash
# Activer
ufw enable

# Politique par défaut
ufw default deny incoming
ufw default allow outgoing

# Autoriser des services
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw allow 'Nginx Full'  # Profil applicatif

# Limiter SSH (rate limiting intégré)
ufw limit ssh

# Par IP source
ufw allow from 192.168.1.100 to any port 22

# Supprimer une règle
ufw delete allow 80/tcp

# Statut détaillé
ufw status verbose
ufw status numbered

# Logs
ufw logging on
tail -f /var/log/ufw.log
```

## Comparaison iptables vs nftables

| Critère | iptables | nftables |
|---------|---------|---------|
| Syntax IPv4/IPv6 | Séparés (iptables/ip6tables) | Unifié (famille `inet`) |
| Performance | Évaluation linéaire | Sets intégrés (O(1) pour listes) |
| Syntaxe | Verbeuse | Plus concise |
| Transactions | Non | Oui (atomique) |
| Sets/Maps | Non natif (ipset séparé) | Natif |
| Disponible depuis | Kernel 2.4 (2001) | Kernel 3.13 (2014) |
| Recommandé | Systèmes anciens | Tous les nouveaux systèmes |
