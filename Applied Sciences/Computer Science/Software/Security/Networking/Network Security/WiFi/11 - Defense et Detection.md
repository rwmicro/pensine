---
title: "Defense WiFi et Détection"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, defense, wids, mfp, hardening]
date: "2026-05-17"
---

# Defense WiFi et Détection

Tout ce qui rend les attaques [[03 - Attaques WPA2-PSK]], [[05 - Evil Twin et Phishing]], [[07 - DoS et MDK4]] inopérantes ou détectables.

## Hardening — configuration AP

### Choix du protocole

```
WPA3-Personal (SAE)            ← Domestique idéal
WPA3-Enterprise + EAP-TLS      ← Entreprise idéal
WPA2-Personal + PMF activé     ← Compromis si parc mixte
WPA2-Enterprise + EAP-TLS      ← Entreprise legacy

À bannir : WEP, WPA-TKIP, WPS, OWE en zone sensible
```

### Checklist AP domestique

- ✓ WPA3-Personal (ou WPA2 + WPA3 transition si parc mixte)
- ✓ PSK ≥ 20 caractères aléatoires (gestionnaire de mdp)
- ✓ **WPS désactivé** (souvent activé d'usine sur les box ISP)
- ✓ Réseau invité isolé (VLAN ou SSID séparé)
- ✓ Bande 5 GHz privilégiée (portée plus courte → moins de surface)
- ✓ Firmware AP à jour (patches KRACK / FragAttacks)
- ✓ Admin web : mot de passe modifié, accès LAN uniquement
- ✓ UPnP désactivé
- ✓ SSID modifié (pas `Livebox-XXXX` par défaut → moins prédictible)

### Checklist AP entreprise

- ✓ WPA3-Enterprise ou WPA2-Enterprise + **PMF obligatoire**
- ✓ **EAP-TLS** avec certificats clients (AC interne)
- ✓ Désactiver PEAP / EAP-TTLS / EAP-FAST si possible
- ✓ Si PEAP nécessaire : validation cert serveur **obligatoire côté client** (GPO)
- ✓ SSID Enterprise différent du SSID guest
- ✓ RADIUS sur réseau d'admin isolé
- ✓ Logs RADIUS centralisés (SIEM) — détection brute-force
- ✓ Rotation régulière des certificats serveur
- ✓ Segmentation : VLAN par groupe d'utilisateurs

## Management Frame Protection (PMF / 802.11w)

Signe cryptographiquement les trames management (deauth, disassoc, action).

```
Sans PMF :  attaquant injecte deauth → client se déconnecte
Avec PMF :  client vérifie le MIC → deauth non signée rejetée
```

| Mode | Comportement |
|------|--------------|
| Disabled | Aucune protection (par défaut WPA2 ancien) |
| Optional | Client peut négocier PMF (rétro-compat) |
| Required | PMF obligatoire (refuse clients sans support) |

```bash
# hostapd.conf
ieee80211w=2                  # 0=disabled, 1=optional, 2=required

# wpa_supplicant (client)
network={
    ssid="MaisonBox"
    psk="..."
    ieee80211w=2              # exiger PMF côté client
}
```

WPA3 exige `ieee80211w=2` par défaut.

### Limites PMF

- N'empêche pas Evil Twin **avec nouvel ESSID** (juste l'usurpation par deauth)
- Beacon frames non protégées (beacon flood reste possible)
- Authentification initiale (Open/SAE Commit) non protégée → DoS par auth flood toujours faisable

## Validation certificat serveur côté client (Enterprise)

**Critique** : c'est la mesure qui bloque la quasi-totalité des attaques WPA2/WPA3-Enterprise.

### Windows (GPO)

```
Computer Configuration → Policies → Windows Settings
→ Security Settings → Wireless Network (IEEE 802.11) Policies
→ New Policy → Properties → Security
   ☑ Validate server certificate
   ☑ Connect to these servers : "radius.corp.local"
   ☑ Trusted Root Certification Authorities : [AC interne uniquement]
   ☑ Don't prompt user to authorize new servers
```

### Android

`Wi-Fi → réseau → Modifier → CA certificate` → choisir le certificat de l'AC interne (pas "Use system certificates" — trop permissif).

### Linux (wpa_supplicant)

```
network={
    ssid="Corporate-WiFi"
    key_mgmt=WPA-EAP
    eap=PEAP
    identity="alice"
    password="..."
    ca_cert="/etc/ssl/corp-ca.pem"
    altsubject_match="DNS:radius.corp.local"
    phase2="auth=MSCHAPV2"
}
```

`altsubject_match` interdit qu'un autre CN soit accepté → mate eaphammer.

## Wireless Intrusion Detection System (WIDS)

Détecte deauth massives, beacon flood, rogue APs, SSID dupliqués.

### Kismet (open-source)

```bash
# Lancer en mode IDS
kismet -c wlan0

# Alertes utiles
# - DEAUTHFLOOD     : >10 deauth/s sur un AP
# - DISCONFLOOD     : disassoc flood
# - APSPOOF         : SSID connu mais nouveau BSSID
# - PROBENOJOIN     : probes massives sans association
# - BEACONFLOOD     : >100 beacons/s
# - CHANCHANGE      : AP change de canal en boucle

# Config alertes dans kismet_alerts.conf
alert=DEAUTHFLOOD,5/min,10/min
```

Interface web : `http://localhost:2501` → Alerts → vue temps réel.

### Solutions entreprise

| Produit | Approche |
|---------|----------|
| **Aruba RFProtect** | Sensors WiFi dédiés + analytics centralisé |
| **Cisco wIPS** | APs Cisco en mode monitor partiel |
| **Mojo AirTight** | Cloud, focus rogue AP / Evil Twin |
| **WatchGuard WIPS** | Sensors séparés des APs production |

Bonnes pratiques :
- **APs dédiés en mode monitor** (≠ APs production) — sinon perte de capacité
- Alimenter le SIEM (Splunk, Elastic) avec les events
- Cartographie : croiser BSSID détectés avec inventaire officiel → rogue détection automatique
- Géolocalisation triangulée (3 sensors min) pour situer un rogue

## Détection manuelle de rogue AP

```bash
# Lister tous les APs actuellement présents
airodump-ng wlan0mon --write scan --output-format csv

# Comparer avec inventaire (whitelist BSSID)
awk -F',' 'NR>1 {print $1}' scan-01.csv | sort -u > seen.txt
diff whitelist.txt seen.txt | grep '^>'   # BSSID inconnus

# Détecter des SSID dupliqués (signe d'Evil Twin)
awk -F',' 'NR>1 {print $14}' scan-01.csv | sort | uniq -c | awk '$1 > 1'
```

## Détection deauth flood

```bash
# Comptage en temps réel des deauth
tshark -i wlan0mon -Y "wlan.fc.type_subtype == 0x0c" \
  -T fields -e wlan.bssid \
  | sort | uniq -c | sort -rn

# Alerter si >50/min
tshark -i wlan0mon -Y "wlan.fc.type_subtype == 0x0c" \
  -a duration:60 -q -z io,stat,60
```

## Segmentation réseau

```
                    [Internet]
                        |
                    [Firewall]
                        |
        ┌───────────────┼───────────────┐
        |               |               |
   [VLAN 10]       [VLAN 20]       [VLAN 30]
   Employés        Invités         IoT
   ↕               ↕               ↕
   Corporate-WiFi  Guest-WiFi      IoT-WiFi
   (WPA3-Ent)      (WPA3 SAE)      (WPA2 + ACL)
```

- Aucun trafic latéral entre VLANs (sauf flux contrôlés via firewall)
- IoT en VLAN dédié (caméras, ampoules, thermostats) — souvent vulnérables, à isoler
- DHCP options 43/60 pour push de config sécurité
- Captive portal sur Guest pour accept des CGU

## Monitoring continu

| Métrique | Outil | Alerte si |
|----------|-------|-----------|
| BSSID inconnus | Kismet + diff whitelist | Nouveau BSSID stable >5 min |
| SSID dupliqués | Kismet APSPOOF | Match SSID + BSSID différent |
| Deauth /s/AP | tshark / kismet | >10/s pendant >30s |
| Échecs RADIUS | logs freeradius / NPS | >20 échecs/IP/min |
| Tentatives EAP avec faux supplicant | RADIUS detailed log | Identity inconnue répétée |
| Clients sur Guest | DHCP leases | Anormalité (heure, volume) |

## Réponse à incident

Si rogue AP détecté :
1. **Géolocaliser** (RSSI sur plusieurs sensors, ou recherche physique avec antenne directive)
2. **Isoler** (port switch correspondant si l'AP rogue est branché filaire)
3. **Identifier** (MAC vendor, ESSID, canal, durée)
4. **Logger** dans le ticket d'incident
5. **Communiquer** aux utilisateurs si phishing actif (rappel : ne jamais ressaisir la PSK)

Si Evil Twin avec captive portal détecté :
1. Diffuser une notification interne immédiate
2. Forcer reset des PSK / mdp Wi-Fi compromis si saisis
3. Si Enterprise : invalider et regénérer les comptes touchés

## Voir aussi

- [[05 - Evil Twin et Phishing]] — ce qu'on contre ici
- [[06 - Attaques WPA2-Enterprise]] — détails de la validation cert
- [[07 - DoS et MDK4]] — détection de DoS
- [[09 - WPA3 et Vulnérabilités Modernes]] — état de l'art
