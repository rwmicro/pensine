---
title: "Contournement Isolation Client (AirSnitch)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, isolation-client, airsnitch, gtk, mitm]
date: "2026-09-10"
---

# Contournement Isolation Client (AirSnitch)

L'isolation client (AP/Client Isolation, "PSPF") empêche les appareils connectés au même point d'accès de communiquer entre eux — fonctionnalité standard sur les réseaux invités, hotspots publics, et de plus en plus en entreprise. Problème : l'**isolation client n'est pas standardisée par IEEE 802.11**. Chaque fabricant l'implémente à sa façon (souvent en filtrant au niveau du pont/bridge de l'AP), ce qui crée des angles morts que la recherche **AirSnitch** (suite de [[03 - Attaques WPA2-PSK|Hole196]] et de MacStealer, USENIX Security '23) systématise et étend. Constat des auteurs : *chaque routeur et réseau testé était vulnérable à au moins une des techniques ci-dessous*.

## Les 3 couches de défaillance

L'isolation peut être appliquée (ou pas) indépendamment à trois niveaux — il suffit qu'une seule soit trouée pour que l'isolation tombe :

| Couche | Domaine | Ce qui doit être vérifié |
|--------|---------|---------------------------|
| A | Chiffrement Wi-Fi | Gestion des clés de groupe GTK/IGTK, unicité par client |
| B | Routage IP (L3) | Règles de forwarding entre clients au niveau de la passerelle |
| C | Commutation L2 | Tables MAC-vers-port de l'AP (apprentissage du pont) |

> [!important] Idée clé
> Cette table à trois couches est la raison pour laquelle "l'isolation client est activée" ne veut souvent rien dire de précis : un AP peut parfaitement bloquer la couche C (commutation) sans jamais filtrer la couche A (GTK partagée) ou la B (routage IP), ce qui suffit à un attaquant qui vise la bonne couche. D'où le constat des chercheurs — chaque routeur testé était troué sur au moins une des trois.

## Techniques d'attaque

### 1. Abus de GTK (Group Temporal Key)

Tous les clients d'un même BSSID partagent la **GTK**, utilisée pour chiffrer le trafic broadcast/multicast. L'attaquant encapsule un paquet unicast destiné à la victime dans une trame **broadcast chiffrée avec la GTK**, en usurpant l'adresse MAC source du point d'accès. La victime déchiffre normalement (elle possède la GTK) et traite le paquet comme légitime. Affecte toutes les versions de WPA/WPA2/WPA3-Personal tant que la GTK est partagée.

```bash
./airsnitch.py wlan2 --check-gtk-shared wlan3 --no-ssid-check
```

### 2. Contournement Passpoint

Passpoint (Hotspot 2.0) devait corriger Hole196 en randomisant la GTK **par client**. Mais la spécification a omis d'exiger cette randomisation lors des **renouvellements** de clé (handshake de groupe périodique, FILS, Fast Transition/FT). Pire : l'**IGTK** (protection des trames de management, cf. [[11 - Defense et Detection#Management Frame Protection (PMF / 802.11w)|PMF]]) n'est **jamais** randomisée par client, quel que soit le mécanisme.

### 3. Contournement MitM classique (insider)

Un attaquant possédant simplement le mot de passe WPA2-PSK partagé (réseau invité typique) capture le 4-way handshake de la victime au moment de son association et en dérive la **PTK** de la victime. Il peut alors déchiffrer/forger son trafic unicast directement — l'isolation au niveau AP ne protège pas contre un pair qui a les clés.

### 4. Faux point d'accès (rogue AP)

L'attaquant clone le SSID et les identifiants (PSK partagé) de l'AP légitime. L'isolation étant une politique appliquée **uniquement par le vrai AP**, le faux AP — auquel la victime peut être basculée (cf. [[05 - Evil Twin et Phishing]]) — n'a simplement aucune isolation configurée.

### 5. Gateway Bouncing (bypass L3, sans casser la crypto)

L'attaquant adresse un paquet avec le **MAC de la passerelle** (couche 2) mais une **IP destination = la victime** (couche 3). L'AP forward normalement vers la passerelle (l'adresse L2 est correcte, l'isolation L2 n'intervient pas), puis la passerelle route le paquet vers la victime (l'IP est valide). Le contournement se fait **sans connaître aucune clé**, en exploitant simplement l'incohérence entre la vérification L2 et le routage L3.

```bash
./airsnitch.py wlan2 --c2c-ip wlan3 --no-ssid-check
```

### 6. Vol de port (Port Stealing)

L'attaquant se connecte à un BSSID (potentiellement différent de celui de la victime) mais émet en usurpant l'**adresse MAC de la victime**. Le processus d'apprentissage L2 de l'AP (table MAC-vers-port) remappe alors le port associé à la victime vers celui de l'attaquant — tout le trafic downlink destiné à la victime part chez l'attaquant.

Variante **uplink** : usurper l'adresse MAC de la **passerelle** pour intercepter le trafic sortant des clients vers Internet.

```bash
./airsnitch.py wlan2 --c2c-port-steal wlan3 --no-ssid-check --other-bss
./airsnitch.py wlan2 --c2c-port-steal-uplink wlan3 --no-ssid-check
```

### 7. Broadcast Reflection

L'attaquant construit une trame avec `ToDS=1` et l'**adresse 3 en broadcast**. L'AP la rechiffre automatiquement avec la GTK avant de la diffuser à tous les clients — l'attaquant n'a besoin de connaître ni la GTK ni la PTK d'un tiers, il détourne le comportement de retransmission de l'AP lui-même.

```bash
./airsnitch.py wlan2 --c2c-broadcast --no-ssid-check
```

### 8. Restauration de port

Pour maintenir l'interception dans le temps malgré le trafic légitime de la victime (qui re-déclenche l'apprentissage L2 en sa faveur), l'attaquant réinitialise régulièrement le mapping MAC-vers-port en sa faveur — déclenché côté serveur (rejouer le vol de port en boucle) ou côté client (forcer un réapprentissage via ICMP).

### 9. Relayage inter-NIC

Sur les réseaux d'entreprise multi-AP, l'attaquant utilise deux interfaces radio connectées au **même AP physique** pour relayer le trafic intercepté d'un client à l'autre à travers l'infrastructure distribuée, étendant les techniques ci-dessus au-delà d'un seul BSSID.

## Chaînage pour un MitM bidirectionnel complet

1. **Interception downlink** — Vol de port (technique 6) : MAC de la victime injectée sur un BSSID différent
2. **Réinjection downlink** — Gateway Bouncing, abus GTK ou Broadcast Reflection (techniques 5, 1, 7) pour que le trafic intercepté atteigne quand même la victime
3. **Interception uplink** — Vol de port variante uplink (MAC de la passerelle usurpée côté radio)
4. **Relayage uplink** — Restauration de port + relayage inter-NIC (techniques 8, 9)

Résultat mesuré par les chercheurs : MitM bidirectionnel établi en **~2 secondes**, avec seulement **1,7 % de perte de paquets** à 10 Mbps en conditions idéales.

> [!tip] Méthode
> Le chaînage illustre pourquoi corriger une seule des 9 techniques ne suffit jamais : le MitM complet combine une technique différente pour chaque direction (downlink/uplink) et chaque étape (interception/réinjection), donc bloquer le vol de port (technique 6) laisse le Gateway Bouncing (technique 5) et l'abus GTK (technique 1) disponibles pour construire une chaîne alternative.

## Défenses et mitigations

1. **Documenter les garanties d'isolation** — actuellement absent des specs AP grand public comme entreprise
2. **Randomiser les clés de groupe par client et par handshake** (4-way, groupe, FILS, FT) — pas seulement à l'association initiale
3. **Filtrer l'unicast IP encapsulé dans du broadcast L2** :
   ```bash
   # Linux bridge — rejette le contournement par abus de GTK / broadcast reflection
   echo 1 > /sys/class/net/br0/bridge/drop_unicast_in_l2_multicast
   ```
4. **VLANs et règles firewall aux deux couches** (MAC et IP) plutôt qu'une isolation appliquée à une seule couche — cf. segmentation dans [[11 - Defense et Detection#Segmentation réseau]]
5. **Prévention d'usurpation MAC** — bloquer les adresses MAC internes déjà associées, interdire les associations simultanées d'une même MAC sur plusieurs BSSID
6. **Prévention d'usurpation IP** (anti-spoofing côté passerelle) — complique directement le Gateway Bouncing
7. **Déchiffrement centralisé** — architecture entreprise où l'isolation est appliquée après déchiffrement complet côté contrôleur, pas au niveau de chaque AP
8. **Avertir explicitement** quand l'isolation est activée sur une config non sécurisée (ex. réseau ouvert / OWE sans PSK, cf. [[09 - WPA3 et Vulnérabilités Modernes#OWE — Opportunistic Wireless Encryption]])

## Outils

Outil de référence : `airsnitch.py` (dépôt `vanhoefm/airsnitch`). Étend MacStealer (USENIX Security '23), qui ne couvrait que le vol de port downlink au sein d'un même BSSID, en ajoutant : abus GTK, gateway bouncing, vol de port cross-BSSID, interception uplink, et broadcast reflection. Intégration prévue dans **RF Swift v0.1.4**.

## Voir aussi

- [[03 - Attaques WPA2-PSK]] — dérivation PTK/PMK exploitée par le MitM classique (technique 3)
- [[09 - WPA3 et Vulnérabilités Modernes]] — FragAttacks permet déjà un bypass d'isolation sans récupération de clé, même famille de problème
- [[11 - Defense et Detection]] — segmentation VLAN, PMF, et durcissement complémentaires
- [[05 - Evil Twin et Phishing]] — vecteur d'accès pour la technique 4 (faux AP sans isolation)
