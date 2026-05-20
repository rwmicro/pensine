---
title: "ARP (Address Resolution Protocol)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2025-05-04"
---

# ARP (Address Resolution Protocol)

L'ARP est le protocole qui fait le lien entre les adresses **IP** (couche réseau) et les adresses **MAC** (couche liaison). C'est grâce à lui que les machines d'un même réseau local savent à qui envoyer physiquement les données.

## Principe de base

Sur un réseau local, les données circulent via des **adresses MAC** (adresses physiques des cartes réseau). Mais on connaît généralement l'adresse IP de la destination, pas son adresse MAC.

ARP résout ce problème : il traduit une IP en MAC.

## Fonctionnement

```
Machine A (192.168.1.10) veut parler à Machine B (192.168.1.20)
    ↓
A envoie une requête ARP en broadcast :
"Qui a l'IP 192.168.1.20 ? Donnez-moi votre MAC !"
    ↓
Toutes les machines du réseau reçoivent la requête
    ↓
Machine B répond en unicast :
"C'est moi ! Ma MAC est AA:BB:CC:DD:EE:FF"
    ↓
A stocke cette info dans son cache ARP
    ↓
A peut maintenant envoyer les trames directement à B
```

## Cache ARP

Pour éviter de répéter cette requête à chaque fois, chaque machine garde un **cache ARP** (table IP → MAC temporaire).

```bash
# Voir le cache ARP (Linux/Mac)
arp -n
ip neigh show

# Windows
arp -a
```


## ARP Poisoning / ARP Spoofing

C'est l'attaque classique exploitant ARP. ARP n'a **aucune authentification** — n'importe qui peut envoyer une fausse réponse ARP.

**Objectif** : faire croire à une machine que l'attaquant est la passerelle (routeur), pour intercepter tout le trafic.

```
Normal :     PC → Routeur → Internet
Attaqué :    PC → Attaquant → Routeur → Internet
                  (MITM : Man In The Middle)
```

**Outil** : `arpspoof`, `ettercap`, `bettercap`

```bash
# Exemple avec arpspoof
arpspoof -i eth0 -t 192.168.1.10 192.168.1.1
# Envoie de fausses réponses ARP à 192.168.1.10 en disant "je suis le routeur 192.168.1.1"
```

## Protection contre l'ARP Poisoning

- **ARP Inspection Dynamique** (DAI) — fonctionnalité des switchs managés qui valide les réponses ARP
- **ARP statique** — entrées manuelles non modifiables (pas pratique à grande échelle)
- **Chiffrement** (TLS/HTTPS) — même si intercepté, les données restent illisibles
- **Surveillance réseau** — détecter les changements d'adresses MAC suspects

## ARP vs RARP vs GARP

| Protocole | Direction | Usage |
|-----------|-----------|-------|
| **ARP** | IP → MAC | Standard |
| **RARP** | MAC → IP | Obsolète (remplacé par DHCP) |
| **Gratuitous ARP** | Auto-annonce | Machine annonce sa propre paire IP/MAC |
