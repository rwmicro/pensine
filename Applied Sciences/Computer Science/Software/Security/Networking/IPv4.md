---
title: IPv4
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [sciences-appliquées, informatique, sécurité, ipv4, réseau, protocole]
date: 2026-03-22
---

# IPv4

IPv4 (Internet Protocol version 4) est le protocole d'adressage fondamental d'Internet depuis 1981. Il fournit un système d'adressage hiérarchique et de routage pour les paquets sur les réseaux interconnectés.

## En-tête IPv4

Un paquet IP est constitué d'un en-tête (20 à 60 octets) suivi des données.

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |    DSCP   |ECN|         Total Length          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|    Fragment Offset       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Time to Live |    Protocol   |        Header Checksum        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Source Address                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Destination Address                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| Champ | Taille | Description |
|---|---|---|
| Version | 4 bits | 4 pour IPv4 |
| IHL | 4 bits | Longueur de l'en-tête (en mots de 32 bits) |
| DSCP | 6 bits | QoS / priorité des paquets |
| Total Length | 16 bits | Longueur totale (max 65 535 octets) |
| Identification | 16 bits | ID pour la fragmentation |
| Flags | 3 bits | DF (Don't Fragment), MF (More Fragments) |
| TTL | 8 bits | Décrémenté à chaque routeur (max 255) |
| Protocol | 8 bits | 6=TCP, 17=UDP, 1=ICMP, 89=OSPF |
| Source/Dest | 32 bits | Adresses IP émetteur et destinataire |

## Espace d'adressage

IPv4 utilise des adresses de 32 bits → 2³² = 4 294 967 296 adresses théoriques. En pratique, beaucoup sont réservées.

**Épuisement :** L'IANA a alloué le dernier bloc /8 en 2011. Le passage à IPv6 est la solution à long terme ; en attendant, NAT permet de conserver IPv4.

## Fragmentation

Si un paquet est trop grand pour le MTU (Maximum Transmission Unit) d'un lien intermédiaire, il est fragmenté.

```
MTU Ethernet standard : 1500 octets (payload IP)
Jumbo frames : jusqu'à 9000 octets (datacenter)

Paquet 3000 octets → fragmentation en :
Fragment 1 : 1500 octets (offset=0, MF=1)
Fragment 2 : 1500 octets (offset=185, MF=0)
```

**DF bit (Don't Fragment) :** si activé et que le paquet est trop grand → le routeur envoie ICMP "Fragmentation Needed" → base du Path MTU Discovery.

**Problèmes de sécurité :**
- Fragmentation utilisée pour contourner des IDS/pare-feux
- Attaque Teardrop : fragments avec offsets se chevauchant → crash OS anciens
- Attaque Ping of Death : paquet réassemblé > 65 535 octets

## ICMP — Internet Control Message Protocol

Protocole de diagnostic et de contrôle associé à IP (protocole 1).

```bash
# Types ICMP courants
Type 0  : Echo Reply (réponse ping)
Type 3  : Destination Unreachable (codes 0-15)
  Code 0  : Net unreachable
  Code 1  : Host unreachable
  Code 3  : Port unreachable
  Code 4  : Fragmentation needed (DF set)
Type 8  : Echo Request (ping)
Type 11 : Time Exceeded (TTL expired → traceroute)
Type 12 : Parameter Problem

# ping — test de connectivité
ping -c 4 8.8.8.8
ping -s 1400 192.168.1.1  # Taille personnalisée (test MTU)

# traceroute — chemin vers la destination
traceroute 8.8.8.8         # Linux (UDP)
tracert 8.8.8.8            # Windows (ICMP)
traceroute -T 8.8.8.8      # TCP SYN (passe mieux les firewalls)
```

**Utilisations malveillantes d'ICMP :**
```
ICMP tunneling : exfiltration de données dans les payloads ICMP
Ping flood : DDoS par saturation de requêtes Echo
Smurf attack : ICMP Echo broadcast avec source spoofée → amplification
```

## Routage IP

### Tables de routage

```bash
# Linux — afficher la table de routage
ip route show
# ou
route -n

# Exemple de table
Destination     Gateway         Interface
0.0.0.0/0       192.168.1.1     eth0    ← Route par défaut
192.168.1.0/24  0.0.0.0         eth0    ← Réseau local
10.0.0.0/8      192.168.1.254   eth0    ← Route statique

# Windows
route print
```

### Algorithme de sélection de route

```
1. Correspondance la plus longue (longest prefix match)
   Destination : 192.168.1.50
   Route A : 192.168.0.0/16 → via GW_A
   Route B : 192.168.1.0/24 → via GW_B  ← SÉLECTIONNÉE (plus spécifique)

2. En cas d'égalité de préfixe → choisir la métrique la plus faible
3. En cas d'égalité de métrique → ECMP (Equal-Cost Multi-Path)
```

## Protocoles associés

### DHCP — Dynamic Host Configuration Protocol

Attribue automatiquement les paramètres réseau (IP, masque, passerelle, DNS).

```
Client → Serveur : DISCOVER (broadcast)
Serveur → Client : OFFER (IP proposée)
Client → Serveur : REQUEST (je prends cette IP)
Serveur → Client : ACK (IP confirmée, bail de X secondes)
```

**Sécurité DHCP :**
- **DHCP Snooping** : les switches filtrent les réponses DHCP (uniquement depuis des ports approuvés) pour prévenir les faux serveurs DHCP
- **DHCP Starvation** : attaque qui remplit le pool DHCP avec de fausses demandes (Gobbler) → les vraies machines ne peuvent plus obtenir d'IP

```bash
# Wireshark — capturer les échanges DHCP
tshark -f "udp port 67 or udp port 68" -i eth0
```

### ARP — Address Resolution Protocol

Résout une adresse IP en adresse MAC sur un réseau local (voir note dédiée).

```
Qui a 192.168.1.1 ? (ARP Request — broadcast)
192.168.1.1 est à AA:BB:CC:DD:EE:FF (ARP Reply — unicast)
```

## Problèmes de sécurité IPv4

| Vulnérabilité | Description | Contre-mesure |
|---|---|---|
| IP Spoofing | Falsifier l'adresse source | BCP38, uRPF (Unicast Reverse Path Forwarding) |
| ICMP tunneling | Exfiltration via ICMP | Filtrage et inspection ICMP |
| Fragmentation attacks | Contournement IDS via fragments | Réassemblage au niveau pare-feu |
| Land attack | Src = Dst → boucle | Filtrage d'adresses invalides |
| Smurf attack | Amplification via broadcast ICMP | Désactiver directed broadcasts |
| Route injection | Injection de routes malveillantes | Authentification des protocoles de routage (MD5/SHA) |

```bash
# Activer l'anti-spoofing (uRPF strict)
# Cisco IOS
interface GigabitEthernet0/0
 ip verify unicast source reachable-via rx

# Linux — vérification RPF
echo 1 > /proc/sys/net/ipv4/conf/all/rp_filter

# Bloquer les paquets avec source dans les plages RFC 1918 (ingress depuis Internet)
iptables -A INPUT -i eth0 -s 10.0.0.0/8 -j DROP
iptables -A INPUT -i eth0 -s 172.16.0.0/12 -j DROP
iptables -A INPUT -i eth0 -s 192.168.0.0/16 -j DROP
```
