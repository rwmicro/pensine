---
title: "WPA3 et Vulnérabilités Modernes"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, wpa3, sae, krack, dragonblood, fragattacks, owe, kr00k, ocv, twt]
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

### Kr00k (2019) — la clé qui tombe à zéro

**CVE-2019-15126** — découverte par ESET. Touche les puces Wi-Fi **Broadcom et Cypress**, présentes dans énormément d'appareils : iPhone, iPad, Samsung Galaxy, Raspberry Pi 3, Amazon Echo, et même certains points d'accès Asus/Huawei.

**Image simple** : imagine que ton téléphone est en train d'écrire une lettre chiffrée pendant qu'il se déconnecte du Wi-Fi. Sur ces puces bugguées, au moment de la déconnexion, la puce **efface la clé de chiffrement avant d'avoir fini d'envoyer** — du coup les derniers mots de la lettre partent chiffrés avec une clé "vide" (que tout le monde connaît), donc lisibles par n'importe qui à l'écoute.

**Comment un attaquant en profite** : il force une déconnexion (par exemple avec du deauth, cf. [[07 - DoS et MDK4]]), puis écoute juste après — ces quelques paquets "de fin" sont récupérables en clair.

```bash
# PoC (nécessite carte en mode monitor + injection)
git clone https://github.com/hexway/krook_poc
python3 kr00k_poc.py -i wlan0mon -b AA:BB:CC:DD:EE:FF -c CLIENT_MAC
# Force une déassociation puis capture les paquets "post-déassoc" chiffrés en clé nulle
```

**Ce qu'on récupère** : pas grand-chose à chaque fois (quelques dizaines à centaines d'octets), mais en répétant la déconnexion en boucle, ça peut suffire à fuiter des bouts de requêtes DNS ou HTTP.

**Point important** : ce n'est **pas un défaut de WPA2 ou WPA3** — le protocole est correct. C'est un bug dans la puce elle-même. Donc le correctif ne dépend pas du protocole Wi-Fi utilisé, mais d'une mise à jour du firmware de la puce (faite par Apple, Samsung, Google... en 2019-2020).

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

### Multi-channel MitM (bypass OCV) — l'espion qui change de fréquence

**Image simple** : imagine deux personnes qui se parlent par talkie-walkie sur le canal 6. Un attaquant avec deux talkie-walkies se met au milieu : il capte ce qui est dit sur le canal 6, et le retransmet en vrai sur le canal 11 vers l'AP. Chacun des deux pense parler directement à l'autre sur "son" canal — en réalité tout passe par l'attaquant, qui peut lire (et modifier) le message au passage.

**Pourquoi ça marche** : avant WPA3, ni le client ni l'AP ne vérifient **sur quel canal une trame a vraiment été reçue**. Le chiffrement protège le contenu, mais pas le fait qu'on ait changé de canal en cours de route. PMF ne détecte rien non plus, puisque les trames elles-mêmes sont valides.

**La correction** : **OCV (Operating Channel Validation)**, ajoutée dans WPA3. L'AP et le client se mettent d'accord sur le canal utilisé et vérifient ensuite que chaque trame vient bien de ce canal — une trame relayée depuis un autre canal est rejetée.

```
# hostapd.conf — activer OCV
ocv=1
ieee80211w=2      # PMF requis, prérequis d'OCV
```

C'est le même genre de problème que le contournement d'isolation client vu dans [[12 - Contournement Isolation Client (AirSnitch)]] : une vérification qu'on pensait implicite (ici, le canal ; là-bas, l'identité du client) n'était en fait jamais faite.

### TWT Sleep Deprivation (Wi-Fi 6/6E) — empêcher le client de dormir

**Contexte** : le **Target Wake Time** (802.11ax / Wi-Fi 6) permet à un appareil de dire à l'AP "je me rendors, réveille-moi dans X secondes" pour économiser sa batterie — utile pour les objets connectés sur batterie.

**L'attaque** : un attaquant qui falsifie ou rejoue ces négociations peut soit empêcher l'appareil de dormir (batterie vidée en continu), soit au contraire décaler son réveil pour qu'il rate des données. Aucune trame deauth ou disassoc n'est utilisée — donc les systèmes de détection classiques, calibrés pour repérer des floods de deauth, ne voient rien passer.

**État actuel** : pas de correctif standardisé. En pratique, il faut ajouter la surveillance des négociations TWT anormalement fréquentes aux métriques déjà suivies (cf. [[11 - Defense et Detection#Monitoring continu]]).

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
