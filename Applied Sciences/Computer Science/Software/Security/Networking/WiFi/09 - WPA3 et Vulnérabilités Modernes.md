---
title: "WPA3 et Vulnérabilités Modernes"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, wpa3, sae, krack, dragonblood, fragattacks, owe]
date: "2026-05-17"
---

# WPA3 et Vulnérabilités Modernes

WPA3 (2018) corrige plusieurs faiblesses de WPA2 : brute-force offline, absence de forward secrecy, hotspots non chiffrés. Mais le standard a lui-même connu des CVE majeures (Dragonblood, FragAttacks).

## WPA3-Personal — SAE (Dragonfly handshake)

SAE = **Simultaneous Authentication of Equals**. Échange de clé à mot de passe authentifié, basé sur l'élément `password element` dérivé du PSK.

### Différence clé avec WPA2

| Aspect | WPA2-PSK | WPA3-SAE |
|--------|----------|----------|
| Capture d'un échange | Suffit à brute-forcer offline | Inutile (pas de matériel exploitable hors ligne) |
| Brute-force | Offline, illimité (GPU) | Online uniquement (rate-limited par l'AP) |
| Forward secrecy | Non | Oui (clés éphémères) |
| Protection trame management | PMF optionnel | PMF obligatoire |

### Le handshake SAE simplifié

```
Client                              AP
  │                                  │
  │ ── Commit (scalar, element) ──→  │
  │                                  │
  │ ←── Commit (scalar, element) ──  │
  │                                  │
  │ ── Confirm (PMK derived) ────→   │
  │                                  │
  │ ←── Confirm (PMK derived) ───    │
  │                                  │
  │ ────── 4-way handshake ──────→   │  (comme WPA2 ensuite)
```

Chaque échange dépend d'un secret éphémère → impossible de rejouer ou bruteforcer hors ligne sans nouvelles interactions.

## WPA3-Enterprise

- AES-256-GCMP (au lieu de CCMP)
- 802.1X + PMF **obligatoire**
- Suite-B (192 bits) en option pour les environnements critiques
- Mêmes attaques EAP applicables que WPA2-Ent ([[06 - Attaques WPA2-Enterprise]]) si validation cert serveur absente

## OWE — Opportunistic Wireless Encryption

Remplace les hotspots "Open" non chiffrés. Diffie-Hellman entre client et AP pour chiffrer la session **sans authentification**.

- ✓ Protège contre le sniff passif
- ✗ Vulnérable au MITM (Evil Twin avec OWE possible)
- ✗ Pas d'authentification mutuelle

## CVE majeures

### KRACK — Key Reinstallation Attack (2017)

**CVE-2017-13077 à 13088** — Mathy Vanhoef.

**Principe** : pendant le 4-way handshake WPA2, si l'attaquant rejoue le message 3, le client **réinstalle la même clé** mais avec un compteur de nonce réinitialisé → réutilisation de nonce → décryption partielle possible.

**Impact** :
- Décrypter du trafic chiffré (TKIP : injection possible)
- Forcer la réutilisation de clés (Android < 6, Linux wpa_supplicant ≤ 2.4 : réinstallation d'une clé toute-à-zéro → décryption complète)

```bash
# PoC officielle Vanhoef
git clone https://github.com/vanhoefm/krackattacks-scripts
cd krackattacks-poc-zerokey
sudo ./krack-test-client.py wlan0
# Teste si le client cible est vulnérable
```

**Patch** : maj `wpa_supplicant` ≥ 2.7, maj iOS ≥ 11.1, Android ≥ patch Nov 2017.

### Dragonblood (2019) — WPA3 / SAE

**CVE-2019-9494 à 9499** — Vanhoef & Ronen.

Plusieurs failles dans l'implémentation SAE :

| CVE | Type | Effet |
|-----|------|-------|
| 9494 | Cache-based side-channel | Récupération du password par observation des accès cache |
| 9496 | Downgrade WPA3 → WPA2 | Forcer un client WPA3 à utiliser WPA2 sur un AP en mode transition |
| 9497 | Resource exhaustion | DoS sur l'AP (CPU épuisé par commit floods) |
| 9498 | Timing side-channel | Récupération password par mesure du temps de réponse |

```bash
# Outil dédié
git clone https://github.com/vanhoefm/dragondrain-and-time
# Permet de tester :
# - dragondrain : DoS par flood de Commit
# - dragontime  : extraction par timing
# - dragonforce : brute-force après partitioning attack
```

**Patch** : hostapd/wpa_supplicant ≥ 2.10, mises à jour vendor (Apple, Samsung, Cisco).

### Downgrade Transition (WPA3-Transition)

En mode transition (WPA2 + WPA3 simultanément), un Evil Twin **WPA2-only** avec le même SSID peut forcer un client à se rabattre sur WPA2.

```bash
# Imitations sans WPA3
hostapd /tmp/wpa2-only.conf
# La victime se connecte → handshake WPA2 capturable → crack offline
```

**Mitigation** : passer en **WPA3-only** dès que tout le parc est compatible.

### FragAttacks (2021)

**CVE-2020-24586 à 24588 et 26139 à 26147** — Vanhoef.

12 vulnérabilités touchant la **fragmentation et l'agrégation** des trames 802.11. Présentes dans **presque tous les appareils** WiFi depuis 1997.

| CVE | Type |
|-----|------|
| 24586 | Cache de fragments non purgé → mélange de trames cross-network |
| 24587 | Fragments chiffrés avec clés différentes assemblés |
| 24588 | A-MSDU avec EAPOL injection |
| 26139 | Forwarding EAPOL avant authentification |
| 26144-26147 | Injection de trames en clair via traitement A-MSDU |

**Impact** :
- Injection de paquets arbitraires (DNS poisoning, redirection)
- Exfiltration de données
- Pas de récupération de clé (mais bypass de l'isolation)

```bash
# Outil de test fragattack
git clone https://github.com/vanhoefm/fragattacks
cd fragattacks/research
sudo ./fragattack.py wlan0 ping
# Teste 45 variantes sur le client/AP
```

**Patch** : Linux kernel ≥ 5.12, iOS ≥ 14.6, Windows updates 2021-05, firmware AP vendor.

## SAE-PT (Hash-to-Element)

Pour mitiger Dragonblood, **SAE-PT** (Hash-to-Element, RFC 9380) remplace la dérivation hash-to-curve par une version sans branchement → élimine les side-channels de timing/cache.

Activé par défaut sur Wi-Fi 6E et au-delà. Vérifier dans `hostapd.conf` :
```
sae_pwe=2          # 0=hunting-and-pecking, 1=H2E, 2=both
```

## Quel est l'état de l'art aujourd'hui ?

| Niveau | Recommandation |
|--------|---------------|
| Domestique | WPA3-Personal SAE (PSK longue), PMF, désactiver WPS |
| Entreprise | WPA3-Enterprise + EAP-TLS, AC interne, validation cert obligatoire |
| Public | OWE (au minimum), VPN systématique côté client |
| Critique | WPA3-Enterprise Suite-B 192 bits, certificats clients HSM-backed |

## Voir aussi

- [[01 - Fondamentaux 802.11]] — SAE et PMF en théorie
- [[05 - Evil Twin et Phishing]] — downgrade transition en pratique
- [[06 - Attaques WPA2-Enterprise]] — applicable à WPA3-Ent
- [[11 - Defense et Detection]] — configurations durcies
