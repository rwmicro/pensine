---
title: "Reconnaissance et Sniffing WiFi"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, recon, kismet, airodump, wardriving]
date: "2026-05-17"
---

# Reconnaissance et Sniffing WiFi

Préalable à toute attaque : passer la carte en mode monitor, scanner les APs et clients, identifier les protocoles.

## Mise en mode monitor

```bash
# Identifier la carte WiFi
iwconfig
iw dev

# Vérifier le support monitor + injection
iw phy | grep -A 8 "Supported interface modes"
# → cherche "monitor" dans la liste

# Méthode 1 : iw (recommandé, ne renomme pas l'interface)
ip link set wlan0 down
iw wlan0 set monitor control
ip link set wlan0 up

# Méthode 2 : airmon-ng (crée wlan0mon)
airmon-ng check kill          # Tue NetworkManager, wpa_supplicant
airmon-ng start wlan0         # → wlan0mon

# Vérifier
iwconfig wlan0mon             # Mode: Monitor

# Tester l'injection
aireplay-ng --test wlan0mon   # → "Injection is working!"
```

## MAC spoofing

```bash
# Changer la MAC (utile pour contourner un filtrage ou rester anonyme)
ip link set wlan0 down
macchanger -r wlan0           # MAC aléatoire
macchanger -m 00:11:22:33:44:55 wlan0  # MAC précise
macchanger -p wlan0           # Restaurer la MAC d'origine
ip link set wlan0 up

# Voir la MAC actuelle vs permanente
macchanger -s wlan0
```

## Scan passif avec airodump-ng

```bash
# Scanner toutes les bandes (channel hopping auto)
airodump-ng wlan0mon

# Scanner uniquement 5 GHz
airodump-ng --band a wlan0mon

# Scanner toutes les bandes (2.4 + 5 + 6 GHz)
airodump-ng --band abg wlan0mon

# Cibler un canal fixe
airodump-ng -c 6 wlan0mon

# Sauvegarder vers fichier
airodump-ng -w scan --output-format pcap,csv wlan0mon
```

**Colonnes clés** :

| Colonne | Signification |
|---------|---------------|
| BSSID | MAC de l'AP |
| PWR | Puissance reçue (plus -50 dBm = proche) |
| Beacons | Beacons reçus |
| #Data | Paquets data capturés |
| CH | Canal |
| MB | Débit max |
| ENC | Chiffrement (WPA2, WPA3, OPN, WEP) |
| CIPHER | CCMP, TKIP, GCMP |
| AUTH | PSK, MGT (Enterprise), SAE |
| ESSID | Nom du réseau (caché = `<length:0>`) |

## Découverte de SSID cachés

```bash
# SSID caché = l'AP ne diffuse pas son nom dans les beacons
# Mais il apparaît dans les Probe Response quand un client se connecte

# Forcer une deauth → le client va se réassocier → ESSID révélé
aireplay-ng --deauth 5 -a AA:BB:CC:DD:EE:FF wlan0mon

# Ou attendre une nouvelle connexion légitime
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF wlan0mon
```

## Probe request sniffing

Les clients émettent en permanence des **probe requests** pour leurs réseaux préférés (PNL = Preferred Network List). Permet de tracer des appareils et d'identifier des SSIDs maison.

```bash
# Avec tcpdump
tcpdump -i wlan0mon -e -s 256 type mgt subtype probe-req

# Avec airodump-ng (les clients sans BSSID apparaissent en bas)
airodump-ng wlan0mon
# Colonne "Probes" : liste des SSIDs recherchés

# Avec hcxdumptool (filtrage propre)
hcxdumptool -i wlan0mon -o probes.pcapng --enable_status=3

# Analyser
tshark -r probes.pcapng -Y "wlan.fc.type_subtype == 4" \
  -T fields -e wlan.sa -e wlan_mgt.ssid
```

Cas d'usage : récupérer un nom de réseau domestique d'une cible (utile pour préparer un Evil Twin).

## Kismet — sniffer/IDS sans fil

```bash
# Lancer kismet (interface web sur http://localhost:2501)
kismet -c wlan0

# Configuration source dans /etc/kismet/kismet_site.conf
source=wlan0:name=carte_alfa

# Channel hopping personnalisé
source=wlan0:name=alfa,channel_hop=true,channel_list=1,6,11,36,40,44,48
```

Avantages de kismet vs airodump :
- Détection automatique des **rogue APs** (mêmes SSID, BSSID différents)
- Logging structuré (pcap, json, kismetdb)
- Plugins (GPS, alerts WIDS)
- Détection de probes flood, deauth flood

## Wardriving

```bash
# Kismet + GPS
gpsd /dev/ttyUSB0                     # Démarrer gpsd
kismet -c wlan0                       # Kismet récupère la position auto

# Export vers WiGLE (cartographie collaborative)
# Kismet → Data → Export → WiGLE CSV
# Upload sur https://wigle.net (compte requis)

# Wigle CLI
wiglecli --upload kismet.csv
```

Alternative légère : **wardriver** (Python), ou apps Android **WiGLE WiFi Wardriving**.

## Visualisation Wireshark

```bash
# Filtres utiles
wlan.fc.type_subtype == 0x08          # Beacons
wlan.fc.type_subtype == 0x04          # Probe requests
wlan.fc.type_subtype == 0x0c          # Deauth
eapol                                  # 4-way handshake
wlan.addr == AA:BB:CC:DD:EE:FF        # Trafic d'une MAC

# Décrypter du WPA2 (si on a la PSK)
# Edit → Preferences → Protocols → IEEE 802.11
# Decryption keys : wpa-pwd → "monpassword:MonSSID"
```

## Énumération des clients connectés

Dans la sortie `airodump-ng`, la partie basse liste les **STATION** :

```
BSSID              STATION            PWR   Rate    Lost  Frames  Probes
AA:BB:...:FF       CC:DD:...:11       -45   1e- 1   0     320     MaisonSSID
(not associated)   EE:FF:...:22       -60   0 - 1   0     5       FreeWiFi,HotelXYZ
```

- `(not associated)` = client en cours de scan, non rattaché à un AP
- `Probes` = SSIDs que le client a déjà recherchés (utile pour Karma)

## Voir aussi

- [[03 - Attaques WPA2-PSK]] — capture du handshake après recon
- [[06 - Attaques WPA2-Enterprise]] — Karma exploite les probes
- [[10 - Hardware et Antennes]] — cartes supportant injection/monitor
