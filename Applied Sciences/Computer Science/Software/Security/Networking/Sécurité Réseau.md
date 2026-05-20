---
title: "Sécurité Réseau"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2026-02-22"
---

# Sécurité Réseau

## Firewalls

Un firewall filtre le trafic entre des zones de confiance différentes selon des règles. Deux approches fondamentales :

### Stateless vs Stateful

| Type | Principe | Limites |
|---|---|---|
| **Stateless** (filtrage de paquets) | Chaque paquet évalué indépendamment (IP src/dst, port, protocole) | Ne voit pas les connexions ; facile à contourner avec des paquets ACK forgés |
| **Stateful** | Maintient une table des connexions établies ; un paquet retour est autorisé seulement s'il correspond à une session initiée | Standard depuis 20 ans. Plus de mémoire, mais bien plus sûr |

### Next-Generation Firewall (NGFW)

Les NGFW ajoutent à l'inspection stateful :
- **Deep Packet Inspection (DPI)** — analyse le contenu applicatif (pas juste les en-têtes)
- **Identification applicative** — distingue YouTube de HTTPS générique sur le même port 443
- **IPS intégré** — détection de signatures et comportements
- **Filtrage URL / catégorie** — blocage par réputation
- **Déchiffrement TLS** — inspection du trafic chiffré (MITM légitime, pose des questions de vie privée)

Exemples : Palo Alto, Fortinet FortiGate, Cisco Firepower, pfSense (open source, stateful + packages).

### Bonnes pratiques firewall

- **Default deny** : tout est bloqué sauf ce qui est explicitement autorisé
- **Principe du moindre privilège** : ouvrir le minimum nécessaire (port + IP source + protocole)
- **Règles ordonnées du plus spécifique au plus général** — le firewall s'arrête à la première règle qui matche
- **Logging des deny** pour détecter les tentatives
- **Revue régulière** des règles — les ACL s'accumulent et deviennent illisibles

## Segmentation réseau

Séparer les flux pour limiter la propagation latérale en cas de compromission.

### Architecture type

```
Internet
    │
    ▼
[ Firewall externe ]
    │
    ├── DMZ (zone démilitarisée)
    │     ├── Serveurs web (80/443)
    │     ├── Reverse proxy
    │     └── Serveur mail (25/587)
    │
    ├── Réseau interne (utilisateurs)
    │     ├── VLAN Bureautique
    │     ├── VLAN Développement
    │     └── VLAN Invités (isolé)
    │
    ├── Réseau serveurs
    │     ├── Base de données
    │     └── Serveurs applicatifs
    │
    └── Réseau d'administration
          ├── Switches, routeurs
          ├── Consoles de management
          └── Bastion / jump host
```

### VLAN (Virtual LAN)

Les VLAN segmentent le réseau au niveau 2 (Ethernet) sans matériel physique séparé.

- **VLAN tagging (802.1Q)** : chaque trame porte un tag VLAN ID (12 bits → 4094 VLANs)
- **Trunk port** : transporte plusieurs VLANs entre switches
- **Access port** : un seul VLAN, vers un hôte final

Limites : un VLAN n'est pas un firewall. Le trafic inter-VLAN passe par un routeur ou un firewall L3 — c'est là que le filtrage se fait.

### Zero Trust

Le modèle **Zero Trust** (formalisé par John Kindervag, Forrester, 2010) part du principe qu'aucun réseau interne n'est de confiance.

Principes :
- **Never trust, always verify** — chaque requête est authentifiée et autorisée, même depuis le LAN
- **Microsegmentation** — politiques granulaires par workload, pas par sous-réseau
- **Least privilege dynamique** — accès accordé au cas par cas, révoqué automatiquement
- **Inspection continue** — le comportement post-authentification est surveillé

Implémentations courantes : Google BeyondCorp, Zscaler, Cloudflare Access, Azure AD Conditional Access.

## VPN (Virtual Private Network)

Un VPN chiffre un tunnel entre deux points à travers un réseau non sûr (Internet).

### Types

| Type | Usage |
|---|---|
| **Site-to-Site** | Connexion permanente entre deux réseaux (siège ↔ filiale) |
| **Remote Access** | Un utilisateur se connecte au réseau d'entreprise depuis l'extérieur |
| **Client-to-Site** | Variante remote access, le client route tout ou partie de son trafic via le VPN |

### Protocoles

| Protocole | Chiffrement | Port | Avantage | Inconvénient |
|---|---|---|---|---|
| **WireGuard** | ChaCha20, Curve25519 | UDP 51820 | Très rapide, code minimal (~4000 lignes), moderne | Jeune, logging limité par design |
| **OpenVPN** | OpenSSL (AES-256-GCM) | UDP 1194 ou TCP 443 | Mature, flexible, traverse les firewalls en TCP/443 | Plus lent que WireGuard, config complexe |
| **IPsec (IKEv2)** | AES, HMAC-SHA | UDP 500 + 4500 (NAT-T) | Natif sur iOS/Windows/macOS, reconnexion rapide (MOBIKE) | Config serveur plus lourde |
| **IPsec (L2TP)** | AES via IPsec | UDP 1701 + 500 + 4500 | Supporté partout | Double encapsulation = overhead |

WireGuard est le choix par défaut pour les nouvelles installations. OpenVPN reste pertinent quand il faut traverser des firewalls restrictifs (TCP 443 se fait passer pour du HTTPS).

## IDS / IPS

### IDS (Intrusion Detection System)

Écoute passivement le trafic (port mirror / SPAN) et génère des alertes. Ne bloque rien.

### IPS (Intrusion Prevention System)

Positionné en coupure (inline) : il analyse et peut **dropper** un paquet avant qu'il n'atteigne sa cible.

### Méthodes de détection

| Méthode | Principe | Forces | Faiblesses |
|---|---|---|---|
| **Signature** | Compare le trafic à des patterns connus (règles Snort/Suricata) | Rapide, peu de faux positifs sur signatures bien écrites | Aveugle aux attaques inconnues (zero-day) |
| **Anomalie** | Apprend un baseline "normal" et alerte sur les déviations | Détecte l'inconnu | Beaucoup de faux positifs, temps d'apprentissage |
| **Comportemental** | Analyse les séquences d'actions (ex. scan puis exploit puis exfil) | Contextuel, résistant à l'obfuscation | Complexe à configurer, coûteux en compute |

### Outils principaux

- **Suricata** — IDS/IPS open source, multi-threaded, supporte les règles Snort + ses propres règles. Standard de fait.
- **Snort** (Cisco/Talos) — historique (1998), toujours maintenu. Snort 3 est multi-threaded.
- **Zeek** (ex-Bro) — pas un IDS classique mais un analyseur de protocoles réseau qui produit des logs structurés. Complémentaire à Suricata.

## Network Access Control (NAC)

Contrôle **qui** et **quoi** peut se connecter au réseau.

### 802.1X

Standard IEEE pour l'authentification réseau au niveau du port (couche 2).

**Trois acteurs** :
1. **Supplicant** — le client qui demande l'accès (poste, téléphone)
2. **Authenticator** — le switch ou la borne WiFi qui contrôle le port
3. **Authentication Server** — serveur RADIUS (FreeRADIUS, Microsoft NPS) qui valide les credentials

**Flux** : le supplicant s'authentifie via EAP (EAP-TLS avec certificat client, ou PEAP avec login/password). Si le RADIUS valide, le switch ouvre le port et peut assigner dynamiquement un VLAN.

### Posture checking

Avant d'accorder l'accès complet, le NAC vérifie l'état du poste :
- Antivirus à jour ?
- OS patché ?
- Disque chiffré ?
- Agent de sécurité installé ?

Si non conforme → placement dans un **VLAN de quarantaine** avec accès limité (portail de remédiation uniquement).

## DNS Security

Le DNS est un vecteur d'attaque sous-estimé (DNS spoofing, DNS tunneling, exfiltration par sous-domaines).

### DNSSEC

Signe cryptographiquement les réponses DNS pour garantir leur authenticité. Protège contre le **DNS cache poisoning** (attaque Kaminsky). Déploiement encore incomplet sur Internet.

### DNS over HTTPS (DoH) / DNS over TLS (DoT)

Chiffrent les requêtes DNS entre le client et le résolveur :
- **DoT** — port 853 dédié, facile à bloquer par un firewall
- **DoH** — port 443 (mélangé avec le HTTPS normal), difficile à bloquer sans DPI

Avantage vie privée, inconvénient sécurité : le SOC perd la visibilité sur les requêtes DNS si les postes utilisent DoH vers un résolveur externe.

### Sinkholing

Technique défensive : le résolveur DNS interne redirige les domaines malveillants connus vers une IP contrôlée (sinkhole) au lieu de la vraie destination. Bloque les communications C2 sans toucher au poste.

## Monitoring réseau

### NetFlow / sFlow / IPFIX

Protocoles qui exportent des **métadonnées de flux** (IP src/dst, ports, octets, durée) depuis les routeurs et switches vers un collecteur. Ne capture pas le contenu, mais permet de détecter les anomalies volumétriques (DDoS, exfiltration, scan) sur de grands réseaux.

### SNMP

*Simple Network Management Protocol* — interroge les équipements réseau pour récupérer des métriques (CPU, bande passante, erreurs d'interface). **SNMPv3** obligatoire (v1/v2c transmettent la community string en clair).

### Centralisation des logs

Tous les équipements réseau (firewalls, switches, routeurs, proxies) doivent envoyer leurs logs vers un **SIEM** via syslog (UDP 514 ou TCP 514/TLS). Sans centralisation, la corrélation d'événements est impossible.
