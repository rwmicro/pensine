---
title: "ARP Poisoning / ARP Spoofing"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2024-09-13"
---

# ARP Poisoning / ARP Spoofing

L'**ARP Poisoning** (ou ARP Spoofing) est une attaque réseau qui consiste à envoyer de **fausses réponses ARP** pour se faire passer pour une autre machine — typiquement le routeur — et intercepter tout le trafic qui lui est destiné.


## Pourquoi c'est possible

Le protocole ARP n'a **aucun mécanisme d'authentification**. N'importe quelle machine sur le réseau peut envoyer une réponse ARP, et les autres machines la croiront sans vérification.


## Ce que ça permet : l'attaque MITM

```
Situation normale :
  Victime  ──────────────►  Routeur  ──► Internet

Après ARP Poisoning :
  Victime  ──► Attaquant ──► Routeur  ──► Internet
               (intercepte et relaie tout)
```

L'attaquant reçoit tout le trafic, peut le lire, le modifier, et le retransmettre. La victime ne voit rien d'anormal.


## Déroulement de l'attaque

**1. Empoisonner le cache ARP de la victime**
L'attaquant envoie à la victime : *"L'IP du routeur (192.168.1.1) correspond à MA MAC address"*

**2. Empoisonner le cache ARP du routeur**
L'attaquant envoie au routeur : *"L'IP de la victime (192.168.1.50) correspond à MA MAC address"*

**3. Résultat**
Tout le trafic victime ↔ routeur passe par l'attaquant.


## Avec Bettercap

[Bettercap](https://www.bettercap.org/) est l'outil moderne pour ce type d'attaque (remplace ettercap).

```bash
# Lancer bettercap sur l'interface réseau
sudo bettercap -iface eth0

# Dans la console bettercap :
set arp.spoof.fullduplex true          # Empoisonner dans les deux sens
set arp.spoof.targets 192.168.1.50     # IP de la cible (laisser vide = tout le réseau)
arp.spoof on                           # Lancer l'empoisonnement

# Sniffer le trafic intercepté
set net.sniff.local true
set net.sniff.verbose false
set net.sniff.output ./capture.pcap    # Sauvegarder dans un fichier pcap
net.sniff on
```

Analyser la capture ensuite avec **Wireshark** :
```bash
wireshark capture.pcap
```


## Ce qu'on peut récupérer

| Protocole | Données récupérables |
|-----------|---------------------|
| HTTP | Tout (requêtes, mots de passe, contenu) |
| DNS | Requêtes DNS (quels sites sont visités) |
| FTP, Telnet | Credentials en clair |
| HTTPS/TLS | Chiffré — illisible sauf avec SSL stripping |


## SSL Stripping

Pour contourner HTTPS, l'attaquant peut tenter un **SSL Stripping** : dégrader la connexion HTTPS en HTTP entre la victime et lui-même, tout en maintenant HTTPS avec le serveur.

Contre-mesure : **HSTS** (HTTP Strict Transport Security) — le navigateur refuse les connexions HTTP sur les domaines déclarés HSTS.


## Protection

| Mesure | Efficacité |
|--------|-----------|
| **ARP Inspection Dynamique (DAI)** sur les switchs managés | Excellente |
| **HTTPS / HSTS** | Protège le contenu même si intercepté |
| **VPN** | Chiffre tout le trafic |
| **802.1X** (authentification réseau) | Empêche les inconnus de se connecter |
| ARP statique | Efficace mais impossible à maintenir à grande échelle |


## Cadre légal

Cette attaque est **illégale** sans autorisation explicite. À utiliser uniquement :
- Sur son propre réseau / lab
- Dans le cadre d'un pentest avec autorisation écrite
- Sur des plateformes dédiées (TryHackMe, HackTheBox)
