---
title: "WAN et Protocoles de Liaison"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking"
tags: [sciences-appliquées, informatique, réseau, wan, ppp, frame-relay]
date: "2026-04-07"
---

# WAN et Protocoles de Liaison

Les réseaux étendus (WAN — Wide Area Network) interconnectent des sites distants via des infrastructures de télécommunications. Contrairement aux LAN, les liaisons WAN sont généralement louées à des opérateurs et présentent des débits et des latences très variables.

## Caractéristiques des WAN

| Critère | LAN | WAN |
|---------|-----|-----|
| Portée | Bâtiment / campus | Villes, pays, continents |
| Débit | 100 Mbps – 100 Gbps | 64 kbps – 10 Gbps |
| Propriété | Entreprise / utilisateur | Opérateurs télécom |
| Latence | < 1 ms | 10 ms – 300 ms |
| Coût | Faible | Élevé |

### Types de liaisons WAN

| Type | Description | Exemples |
|------|-------------|---------|
| Ligne dédiée (leased line) | Liaison point-à-point permanente | T1 (1,544 Mbps), E1 (2,048 Mbps), T3 |
| Circuit commuté | Connexion établie à la demande | RTC, RNIS/ISDN |
| Paquet commuté | Réseau partagé avec commutation par paquets | Frame Relay, ATM, MPLS |
| Internet VPN | Tunnel chiffré sur Internet public | IPsec VPN, SSL VPN |
| Cellulaire | 4G LTE, 5G pour sites distants | Sites de secours, kiosques |

## PPP — Point-to-Point Protocol

PPP (RFC 1661) est le protocole WAN le plus courant pour les liaisons point-à-point. Il remplace HDLC (propriétaire Cisco) et fonctionne sur tout support série.

### Architecture PPP

PPP encapsule plusieurs protocoles dans une même liaison via une architecture en sous-protocoles :

```
┌──────────────────────────────────┐
│       Protocoles réseau          │
│   (IP, IPX, AppleTalk, ...)      │
├──────────────────────────────────┤
│     NCP — Network Control        │
│   Protocol (un par protocole     │
│       réseau : IPCP, IPXCP...)   │
├──────────────────────────────────┤
│     LCP — Link Control Protocol  │
│  (négociation, authentification, │
│      compression, multilink)     │
├──────────────────────────────────┤
│   Support physique (série, ISDN, │
│       analogique, Ethernet)      │
└──────────────────────────────────┘
```

### Établissement d'une session PPP

1. **Link Dead** : pas de support physique
2. **Link Establishment** : LCP négocie les paramètres (MRU, authentification, compression)
3. **Authentication** : PAP ou CHAP (optionnel)
4. **Network Layer Protocol** : NCP configure les protocoles de couche 3 (IPCP attribue les adresses IP)
5. **Link Open** : données échangées
6. **Link Termination** : LCP envoie Terminate-Request

### Authentification PPP

#### PAP — Password Authentication Protocol

- Authentification en deux messages (Request + ACK/NAK)
- **Mots de passe envoyés en clair** — non sécurisé
- Utilisé uniquement si CHAP non supporté

```cisco
! Configuration PAP
Router(config-if)#ppp authentication pap
Router(config)#username RemoteRouter password MotDePasse
```

#### CHAP — Challenge Handshake Authentication Protocol

- Authentification en trois messages : Challenge → Response → Success/Failure
- Le mot de passe **n'est jamais transmis** — seul un hash MD5 est échangé
- Ré-authentification périodique possible pendant la session

```
Authenticator → Peer : Challenge (nombre aléatoire)
Peer → Authenticator : Response = MD5(ID + Secret + Challenge)
Authenticator → Peer : Success ou Failure
```

```cisco
! Configuration CHAP
Router(config-if)#ppp authentication chap
Router(config)#username PeerHostname password SecretPartagé
! Note : les noms d'hôtes doivent correspondre exactement
```

### Compression PPP

```cisco
! Compression Stac LZS
Router(config-if)#ppp compress stac

! Compression Predictor
Router(config-if)#ppp compress predictor
```

### Multilink PPP (MLPPP)

Agrège plusieurs liaisons série en un seul canal logique de plus grande capacité.

```cisco
! Créer une interface Multilink
Router(config)#interface Multilink1
Router(config-if)#ip address 10.1.1.1 255.255.255.252
Router(config-if)#ppp multilink
Router(config-if)#ppp multilink group 1

! Assigner des interfaces physiques au groupe
Router(config)#interface Serial0/0
Router(config-if)#encapsulation ppp
Router(config-if)#ppp multilink
Router(config-if)#ppp multilink group 1
```

### Configuration PPP de base

```cisco
! Configuration sur interface série
Router(config)#interface Serial0/0
Router(config-if)#ip address 10.0.0.1 255.255.255.252
Router(config-if)#encapsulation ppp
Router(config-if)#ppp authentication chap
Router(config-if)#no shutdown

! Vérification
Router#show interfaces Serial0/0
Router#show ppp all
Router#debug ppp authentication
```

## Frame Relay

Frame Relay est un protocole WAN de commutation par paquets opérant à la couche 2 (liaison). Il était très répandu dans les années 1990-2000, largement remplacé aujourd'hui par MPLS et les VPN.

### Concepts fondamentaux

**DLCI — Data-Link Connection Identifier** : identifiant local (10 bits, significatif seulement entre le routeur et le switch Frame Relay) qui identifie un circuit virtuel.

**PVC — Permanent Virtual Circuit** : circuit virtuel permanent configuré par l'opérateur. Pas d'établissement de connexion dynamique.

**SVC — Switched Virtual Circuit** : circuit établi à la demande (rare en Frame Relay).

**Frame Relay Switch** : équipement de l'opérateur qui commute les trames entre DLCI.

```
Site A                    Nuage Frame Relay                Site B
RouterA ──── DLCI 102 ──── Switch ──── DLCI 201 ──── RouterB
             (local)                   (local)
```

### En-tête Frame Relay

```
 0               1
 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    DLCI (6)   |C/R|EA|DLCI(4)|FECN|BECN|DE|EA|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| Champ | Description |
|-------|-------------|
| DLCI | Identifiant du circuit virtuel (10 bits répartis) |
| FECN | Forward Explicit Congestion Notification — congestion vers destination |
| BECN | Backward Explicit Congestion Notification — congestion vers source |
| DE | Discard Eligibility — trame éligible au rejet en cas de congestion |
| EA | Extended Address — indique la fin de l'en-tête |

### CIR — Committed Information Rate

Le débit garanti par l'opérateur. Le trafic au-delà du CIR est marqué DE=1 et peut être rejeté en cas de congestion.

| Paramètre | Description |
|-----------|-------------|
| CIR | Débit garanti (bits/s) |
| Bc | Burst Committed — volume de données à débit CIR par période Tc |
| Be | Burst Excess — volume dépassant Bc, toléré mais non garanti |
| Tc | Période de mesure (Bc/CIR) |

### Configuration Frame Relay (hub-and-spoke)

```cisco
! Routeur Hub
Router(config)#interface Serial0/0
Router(config-if)#encapsulation frame-relay
Router(config-if)#no shutdown

! Sous-interface point-à-point (recommandé)
Router(config)#interface Serial0/0.101 point-to-point
Router(config-subif)#ip address 10.1.1.1 255.255.255.252
Router(config-subif)#frame-relay interface-dlci 101

Router(config)#interface Serial0/0.102 point-to-point
Router(config-subif)#ip address 10.1.2.1 255.255.255.252
Router(config-subif)#frame-relay interface-dlci 102

! Vérification
Router#show frame-relay pvc
Router#show frame-relay map
Router#show frame-relay lmi
```

### LMI — Local Management Interface

Protocole de signalisation entre le routeur et le switch Frame Relay. Fournit des informations sur l'état des PVC.

| Type LMI | Norme |
|----------|-------|
| Cisco (défaut) | Propriétaire Cisco |
| ANSI | T1.617 Annexe D |
| Q933A | ITU-T Q.933 |

```cisco
! Définir le type LMI (normalement auto-négocié)
Router(config-if)#frame-relay lmi-type ansi
```

### Frame Relay vs MPLS

| Critère | Frame Relay | MPLS |
|---------|-------------|------|
| Couche | 2 (Data Link) | 2,5 (entre L2 et L3) |
| QoS | Basique (FECN/BECN/DE) | Avancée (Traffic Engineering) |
| Protocoles | IP principalement | Multi-protocoles |
| Convergence | Lente | Rapide (50 ms) |
| Statut | Obsolète | Déployé en entreprise |

## HDLC — High-Level Data Link Control

Protocole de liaison point-à-point de niveau 2. Standard ISO, mais Cisco utilise une version propriétaire ajoutant un champ type (pour supporter plusieurs protocoles réseau).

```cisco
! HDLC est l'encapsulation par défaut sur les interfaces série Cisco
interface Serial0/0
 encapsulation hdlc     ! Encapsulation par défaut

! Vérifier l'encapsulation
show interfaces Serial0/0 | include encapsulation
```

## MPLS — Multiprotocol Label Switching

MPLS (RFC 3031) est le successeur de Frame Relay dans les réseaux opérateurs. Il commute les paquets en se basant sur des **labels** plutôt que sur des adresses IP, permettant une plus grande flexibilité et des performances supérieures.

### Fonctionnement

```
Paquet IP → [Label Imposition] → Trame MPLS → [Label Switching] → [Label Disposition] → Paquet IP

CE Router → PE Router ─────── P Router ─────── PE Router → CE Router
  (client)   (provider edge)   (provider)   (provider edge)   (client)
```

| Composant | Rôle |
|-----------|------|
| CE (Customer Edge) | Routeur côté client |
| PE (Provider Edge) | Routeur opérateur qui impose/retire les labels |
| P (Provider) | Routeur opérateur qui commute uniquement par label |
| LSP | Label Switched Path — chemin préétabli dans le réseau MPLS |
| LDP | Label Distribution Protocol — distribue les labels entre routeurs |
| RSVP-TE | Réserve des ressources pour le Traffic Engineering |

### Services MPLS

**L3 VPN (RFC 2547)** : extension des tables de routage par client via VRF (Virtual Routing and Forwarding). Isolation des réseaux clients, chaque CE voit un réseau privé.

**L2 VPN / VPLS** : connectivité de niveau 2 entre sites distants — le client voit un seul LAN étendu.

**Traffic Engineering** : routes explicites indépendantes du plus court chemin IGP, avec réservation de bande passante.

## Comparaison des technologies WAN

| Technologie | Couche | Statut | Usage actuel |
|-------------|--------|--------|-------------|
| PPP | 2 | Utilisé | Accès DSL/câble, liaisons série |
| Frame Relay | 2 | Obsolète | Remplacement par MPLS |
| ATM | 2 | Quasi-obsolète | Backbones opérateurs |
| HDLC | 2 | Utilisé (Cisco) | Liaisons série point-à-point |
| MPLS | 2,5 | Courant | Réseaux opérateurs, entreprise |
| SD-WAN | Overlay | Croissance | Remplacement progressif MPLS |

## SD-WAN — Software-Defined WAN

Approche moderne qui abstrait le lien WAN physique. Les décisions de routage sont centralisées dans un contrôleur logiciel.

**Avantages** :
- Utilisation de n'importe quel lien (MPLS, Internet, LTE)
- Routage intelligent basé sur l'application et la qualité du lien
- Déploiement simplifié (zero-touch provisioning)
- Réduction des coûts (Internet moins cher que MPLS)

**Exemples** : Cisco Viptela, VMware Velocloud, Silver Peak, Fortinet SD-WAN.
