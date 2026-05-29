---
title: "Fondamentaux 802.11"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, 802.11]
date: "2026-05-17"
---

# Fondamentaux 802.11

## Standards IEEE 802.11

| Standard | Année | Débit max | Modulation | Bande |
|----------|-------|-----------|------------|-------|
| 802.11a | 1999 | 54 Mbps | OFDM | 5 GHz |
| 802.11b | 1999 | 11 Mbps | DSSS/CCK | 2,4 GHz |
| 802.11g | 2003 | 54 Mbps | OFDM/DSSS | 2,4 GHz |
| 802.11n (Wi-Fi 4) | 2009 | 450 Mbps | OFDM (MIMO) | 2,4 / 5 GHz |
| 802.11ac (Wi-Fi 5) | 2014 | 6,77 Gbps | OFDM (MU-MIMO) | 5 GHz |
| 802.11ax (Wi-Fi 6/6E) | 2019 | 9,6 Gbps | OFDMA | 2,4 / 5 / 6 GHz |
| 802.11be (Wi-Fi 7) | 2024 | 46 Gbps | 4K-QAM | 2,4 / 5 / 6 GHz |

## Bandes et canaux

| Bande | Canaux usuels | Largeur | Remarques |
|-------|---------------|---------|-----------|
| 2,4 GHz | 1 à 14 (1, 6, 11 non chevauchants en EU) | 20 MHz | Longue portée, encombrée |
| 5 GHz | 36 à 165 (DFS 52-144) | 20/40/80/160 MHz | Plus rapide, portée plus courte |
| 6 GHz | 1 à 233 (Wi-Fi 6E) | jusqu'à 320 MHz | Réservé WPA3, peu d'interférence |

DFS (Dynamic Frequency Selection) impose à l'AP de céder le canal si un radar militaire/météo est détecté.

## Types de trames 802.11

| Type | Sous-types | Usage |
|------|------------|-------|
| Management | Beacon, Probe Req/Resp, Auth, Assoc, Deauth, Disassoc | Découverte, association, gestion |
| Control | RTS, CTS, ACK, Block ACK | Contrôle d'accès au médium |
| Data | Data, QoS Data, Null | Transport des données utilisateur |

Les trames management sont **non chiffrées** par défaut et exploitables (deauth, beacon flood, evil twin). PMF (802.11w) corrige ce défaut.

## Types de réseaux sans fil

| Type | Portée | Application | Exemples |
|------|--------|-------------|----------|
| PAN | Quelques mètres | Remplacement de câbles | Bluetooth, NFC, Zigbee |
| LAN (WLAN) | Quelques salles | Extension Wi-Fi d'un LAN | IEEE 802.11 |
| MAN | Échelle d'une ville | Interconnexion inter-réseaux | IEEE 802.16 (WiMAX) |
| WAN | Mondial | Accès réseau mobile | LTE, 5G NR |

## Modes d'authentification

| Mode | Description | Cas d'usage |
|------|-------------|-------------|
| Open | Aucune authentification | Hotspots publics |
| Shared Key | Clé pré-partagée (WEP/WPA-PSK) | Domestique |
| 802.1X (Enterprise) | RADIUS + EAP | Entreprises, universités |
| SAE (WPA3) | Échange à mots de passe authentifié | Domestique moderne |
| OWE | Chiffrement opportuniste sans clé | Hotspots publics WPA3 |

## Protocoles de sécurité

| Protocole | Chiffrement | Authentification | Statut |
|-----------|-------------|------------------|--------|
| WEP | RC4 (40/104 bits) | Clé statique | Cassé (minutes) |
| WPA (TKIP) | RC4 + MIC | PSK / 802.1X | Vulnérable, déprécié |
| WPA2-Personal | AES-CCMP | PSK (handshake 4-way) | Vulnérable au brute-force offline |
| WPA2-Enterprise | AES-CCMP | 802.1X (EAP) | Robuste si bien configuré |
| WPA3-Personal | AES-CCMP | SAE | Résistant au brute-force offline |
| WPA3-Enterprise | AES-256-GCMP | 802.1X + PMF obligatoire | État de l'art |

## Architecture d'un réseau Wi-Fi infrastructure

```
        Internet
           |
        Routeur
           |
   +-------+-------+
   |               |
   AP1 (BSS)    AP2 (BSS)        ESS = ensemble d'APs
   /  \           |               partageant le même ESSID
 STA  STA        STA              (roaming entre BSS)
```

- **BSS** (Basic Service Set) : un AP + ses clients
- **ESS** (Extended Service Set) : plusieurs APs avec le même SSID
- **BSSID** : MAC de l'AP (identifiant unique)
- **ESSID** : nom du réseau (humain)
- **SSID** : terme générique pour le nom

## Voir aussi

- [[02 - Reconnaissance et Sniffing]]
- [[09 - WPA3 et Vulnérabilités Modernes]]
