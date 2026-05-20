---
title: "Hardware et Antennes WiFi"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, hardware, alfa, chipset, antenne]
date: "2026-05-17"
---

# Hardware et Antennes WiFi

Le hardware conditionne tout : monitor mode, injection, bandes supportées, sensibilité. Un mauvais choix de carte rend la plupart des attaques impossibles.

## Critères de sélection

| Critère | Pourquoi |
|---------|----------|
| **Mode monitor** | Capture passive des trames |
| **Injection de paquets** | Deauth, fake auth, ARP replay, fragments |
| **Pilote open-source** | `mac80211` framework (Linux), pas de blobs propriétaires |
| **Bandes** | 2.4 + 5 GHz minimum, 6 GHz pour Wi-Fi 6E |
| **Puissance émission** | Régulée par pays (EU : 100 mW en 2.4, 200 mW en 5) |
| **Antenne détachable** | RP-SMA pour brancher du directif |
| **Format** | USB > miniPCIe si portabilité |

## Chipsets recommandés (Linux)

| Chipset | Carte représentative | Bandes | Monitor | Injection | Notes |
|---------|---------------------|--------|---------|-----------|-------|
| **Atheros AR9271** | Alfa AWUS036NHA, TP-Link TL-WN722N v1 | 2.4 GHz | ✓ | ✓ | Référence historique, pilote `ath9k_htc` |
| **Realtek RTL8812AU** | Alfa AWUS036ACH, Alfa AWUS036AC | 2.4 + 5 | ✓ | ✓ | Pilote `rtl8812au` (DKMS), bidouille parfois |
| **Realtek RTL8811AU** | Alfa AWUS036ACS | 2.4 + 5 | ✓ | ✓ | Compact, moins puissant |
| **Realtek RTL8814AU** | Alfa AWUS1900 | 2.4 + 5 (AC1900) | ✓ | ✓ | 4 antennes, MIMO 4x4 |
| **Mediatek MT7612U** | Alfa AWUS036ACM | 2.4 + 5 | ✓ | ✓ | Pilote mainline `mt76`, très propre |
| **Mediatek MT7921AU** | Alfa AWUS036AXML | 2.4 + 5 + 6 (Wi-Fi 6E) | ✓ | partiel | Wi-Fi 6E, support en cours |
| **Ralink RT3070** | Alfa AWUS036NH | 2.4 GHz | ✓ | ✓ | Ancien, `rt2800usb`, fiable |

### Cartes à éviter

| Chipset | Problème |
|---------|----------|
| **TP-Link TL-WN722N v2/v3** (Realtek RTL8188EUS) | Pas d'injection fiable, à confondre avec la v1 (AR9271) |
| **Intel AX200/AX210** | Excellent en client, mais injection bridée par firmware |
| **Broadcom (FullMAC)** | Drivers propriétaires, monitor limité |
| **Realtek RTL8723** | Performances et stabilité médiocres en monitor |

## Vérifier la compatibilité

```bash
# Identifier la carte
lsusb                              # Cartes USB
lspci -nnk | grep -A 2 Network     # Cartes PCIe

# Voir le pilote chargé
iw dev
iw phy

# Vérifier le support monitor + injection
iw phy phy0 info | grep -A 5 "Supported interface modes"
# Doit contenir "monitor"

# Tester l'injection une fois en monitor
ip link set wlan0 down
iw wlan0 set monitor control
ip link set wlan0 up
aireplay-ng --test wlan0
# → "Injection is working!"
```

## Installation pilotes RTL8812AU

```bash
sudo apt install dkms build-essential linux-headers-$(uname -r)
git clone https://github.com/aircrack-ng/rtl8812au
cd rtl8812au
sudo make dkms_install
sudo modprobe 8812au
```

## Cartes Alfa — comparaison rapide

| Modèle | Chipset | Prix | Bande | Cas d'usage |
|--------|---------|------|-------|-------------|
| **AWUS036NHA** | AR9271 | ~30 € | 2.4 | Apprentissage, ultra-stable |
| **AWUS036ACH** | RTL8812AU | ~55 € | 2.4 + 5 | Polyvalent, le plus utilisé |
| **AWUS036ACM** | MT7612U | ~50 € | 2.4 + 5 | Drivers mainline, recommandé |
| **AWUS1900** | RTL8814AU | ~110 € | 2.4 + 5 (4x4) | Long range, MIMO |
| **AWUS036AXML** | MT7921AU | ~80 € | 2.4 + 5 + 6 | Wi-Fi 6E, futur-proof |

## Antennes

### Types

| Type | Gain | Pattern | Usage |
|------|------|---------|-------|
| **Omnidirectionnelle** | 3-9 dBi | 360° horizontal | Scan large, audit local |
| **Panneau** (patch) | 8-14 dBi | ~60° cône | Cible directionnelle moyenne |
| **Yagi** | 10-15 dBi | ~30° cône | Longue portée précise |
| **Parabolique** (grille) | 18-24 dBi | ~10° cône | Très longue portée (km) |

### Calcul de portée

```
Signal reçu (dBm) = Puissance TX (dBm) + Gain TX (dBi) - Path Loss + Gain RX (dBi)

Path Loss (espace libre, 2.4 GHz, en dB) = 40 + 20 log10(distance_m)

Exemple :
  TX : 100 mW = 20 dBm + antenne 9 dBi = 29 dBm EIRP
  RX : sensibilité -90 dBm, antenne yagi 15 dBi
  Budget : 29 + 15 - (-90) = 134 dB
  → 40 + 20 log10(d) ≤ 134
  → d ≤ 10^((134-40)/20) ≈ 50 km (théorique, en LoS parfait)
```

En pratique : obstacles, multipath, bruit ambiant → **portée réelle ÷ 5 à 10**.

### Connecteurs

- **RP-SMA** : standard Wi-Fi (la plupart des Alfa, TP-Link)
- **N-Type** : antennes pro (yagi, parabolique) → adaptateur RP-SMA / N nécessaire
- **U.FL / IPX** : interne miniPCIe → pigtail vers RP-SMA

## GPS pour wardriving

```bash
# Récepteur GPS USB recommandé : VK-172 (~10 €, chipset u-blox)
sudo apt install gpsd gpsd-clients

# Vérifier
dmesg | grep ttyACM        # /dev/ttyACM0 souvent
gpsd /dev/ttyACM0 -F /var/run/gpsd.sock
cgps -s                    # affichage temps réel
```

Kismet pioche automatiquement gpsd quand actif.

## Setup recommandé selon le contexte

| Contexte | Setup |
|----------|-------|
| Apprentissage à la maison | AWUS036NHA + antenne omni 9 dBi |
| Audit en clientèle (mobilité) | AWUS036ACM + omni 5 dBi pliable |
| Capture longue distance | AWUS036ACH + yagi 15 dBi sur trépied |
| Wardriving | AWUS036ACM + omni magnétique sur toit + GPS VK-172 |
| Lab Wi-Fi 6E | AWUS036AXML + omni 6 dBi |
| Evil Twin (2 cartes) | AWUS036ACM (uplink) + AWUS036NHA (rogue AP) |

## Régulation et puissance

| Région | Domain | 2.4 GHz max | 5 GHz max |
|--------|--------|-------------|-----------|
| EU (FR, DE, ES) | `EU` ou pays | 100 mW (20 dBm) | 200 mW (23 dBm) indoor |
| US | `US` | 1 W (30 dBm) | 1 W indoor |
| JP | `JP` | 50 mW sur ch 1-13 | variable |

```bash
# Voir le domaine de régulation actuel
iw reg get

# Forcer un domaine (avec prudence — légalement engageant)
sudo iw reg set BO       # Bolivie : 1 W partout (souvent utilisé en lab)
sudo iw reg set US
```

**Note** : forcer un domaine plus permissif que le sien est illégal en émission. Restez en `FR`/`EU` hors lab isolé.

## Voir aussi

- [[02 - Reconnaissance et Sniffing]] — mise en monitor, tests
- [[05 - Evil Twin et Phishing]] — setup 2 cartes
- [[11 - Defense et Detection]] — WIDS hardware
