---
title: "Index WiFi"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, moc]
date: "2026-05-17"
---

# Index WiFi

Cartographie complète du domaine WiFi — fondamentaux, attaques offensives, outils, défense.

## Théorie

- [[01 - Fondamentaux 802.11]] — Standards, trames, bandes, modes d'authentification, protocoles de sécurité
- [[09 - WPA3 et Vulnérabilités Modernes]] — SAE, OWE, KRACK, Dragonblood, FragAttacks

## Reconnaissance

- [[02 - Reconnaissance et Sniffing]] — Mode monitor, airodump, kismet, wardriving, probe sniffing, MAC spoofing

## Attaques offensives

- [[03 - Attaques WPA2-PSK]] — Capture handshake, PMKID, cracking aircrack/hashcat, WEP
- [[04 - Attaques WPS]] — Reaver, Bully, Pixie Dust, Wash
- [[05 - Evil Twin et Phishing]] — Rogue AP, captive portal, fluxion, wifiphisher
- [[06 - Attaques WPA2-Enterprise]] — eaphammer, hostapd-wpe, Karma/MANA, PEAP-MSCHAPv2
- [[07 - DoS et MDK4]] — Deauth, beacon flood, auth flood, WIDS confusion

## Frameworks et automatisation

- [[08 - Frameworks Tout-en-Un]] — airgeddon, wifite2, bettercap

## Pratique

- [[10 - Hardware et Antennes]] — Cartes Alfa, chipsets injection, antennes directives

## Défense

- [[11 - Defense et Detection]] — WIDS, MFP, segmentation, monitoring rogue AP

## Notes connexes

- [[Responder]] — Capture de credentials NTLM (utile après accès WiFi entreprise)
- [[HTTPS]] — Sécurité de la couche transport (intercepter via Evil Twin)

## Conventions

Les commandes supposent une interface `wlan0` passée en monitor sous `wlan0mon`. Adapter selon le chipset.
Les MAC `AA:BB:CC:DD:EE:FF` sont des placeholders pour le BSSID cible.
