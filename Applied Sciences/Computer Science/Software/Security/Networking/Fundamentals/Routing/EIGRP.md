---
title: "EIGRP — Enhanced Interior Gateway Routing Protocol"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals > Routing"
tags: [sciences-appliquées, informatique, sécurité, réseau, routage]
date: "2026-04-07"
---

# EIGRP — Enhanced Interior Gateway Routing Protocol

EIGRP est un protocole de routage dynamique avancé développé par Cisco. Il est qualifié de protocole "hybride" car il combine des caractéristiques des protocoles à vecteur de distance et à état de lien.

## Caractéristiques

- Publié en 1992 comme protocole propriétaire Cisco (partiellement ouvert en 2013 via RFC 7868)
- Protocole de routage à vecteur de distance avancé (Advanced Distance Vector)
- Utilise l'algorithme **DUAL** (Diffusing Update Algorithm) pour calculer le meilleur chemin
- Forme des **adjacences de voisinage** (Neighbor Adjacencies)
- Utilise un transport fiable pour l'envoi des paquets EIGRP
- **Mises à jour partielles et bornées** : n'envoie des mises à jour que lors d'un changement de route, uniquement aux routeurs concernés
- Prend en charge l'**équilibrage de charge à coût égal et inégal** (Equal and Unequal Cost Load Balancing)

## DUAL — Diffusing Update Algorithm

DUAL est l'algorithme qui permet à EIGRP de trouver le meilleur chemin et un chemin alternatif sans boucle. Il garantit des chemins sans boucle à chaque instant.

### Terminologie DUAL

| Terme | Définition |
|-------|-----------|
| Successor | Routeur voisin offrant le meilleur chemin (plus faible coût) vers la destination |
| Feasible Successor (FS) | Routeur voisin offrant un chemin alternatif sans boucle |
| Feasible Distance (FD) | Coût total du meilleur chemin vers la destination |
| Reported Distance (RD) | Coût annoncé par un voisin pour atteindre la destination |
| Condition de faisabilité | RD du FS < FD du Successor actuel |

## Métrique EIGRP

La métrique EIGRP est un composite de plusieurs paramètres :

```
Métrique = [K1 × Bande_passante + (K2 × Bande_passante)/(256 - Charge) + K3 × Délai] × [K5/(Fiabilité + K4)]
```

Par défaut, seuls K1 (bande passante) et K3 (délai) sont utilisés (K2=K4=K5=0) :

```
Métrique = (10^7 / Bande_passante_min_kbps) × 256 + (Délai_total_μs / 10) × 256
```

| Paramètre | Description |
|-----------|-------------|
| Bande passante (Bandwidth) | Bande passante minimale sur le chemin (kbps) |
| Délai (Delay) | Délai cumulé sur tous les liens (μs) |
| Fiabilité (Reliability) | Fiabilité de l'interface (255 = 100 %) |
| Charge (Load) | Charge de l'interface (1-255) |

## Types de paquets EIGRP

| Type | Description |
|------|-------------|
| Hello | Découverte et maintien des voisins |
| Update | Mises à jour de routage |
| Query | Demande de route alternative lors d'une panne |
| Reply | Réponse à un Query |
| ACK | Accusé de réception |

## Configuration Cisco

### Configuration de base

```cisco
! Activer EIGRP (numéro de système autonome identique sur tous les routeurs)
Router(config)#router eigrp 10

! Déclarer les réseaux
Router(config-router)#network 192.168.1.0
Router(config-router)#network 10.0.0.0

! Désactiver la summarisation automatique
Router(config-router)#no auto-summary

! Identifier le routeur
Router(config-router)#eigrp router-id 1.1.1.1
```

### Configuration de l'équilibrage de charge inégal

```cisco
! Variance : permet l'équilibrage sur des chemins dont la métrique est jusqu'à N fois le chemin optimal
Router(config-router)#variance 2
```

### Passive interface

```cisco
! Empêcher EIGRP d'envoyer des Hello sur une interface (ex: interface vers les utilisateurs)
Router(config-router)#passive-interface GigabitEthernet0/1
```

### Configuration IPv6 (EIGRPv6)

```cisco
ipv6 router eigrp 10
 eigrp router-id 1.1.1.1
 no shutdown
!
interface GigabitEthernet0/0
 ipv6 eigrp 10
```

## Vérification

```cisco
show ip eigrp neighbors        ! Voisins EIGRP
show ip eigrp topology         ! Table topologique (Successors et FS)
show ip route eigrp            ! Routes EIGRP dans la table de routage
show ip eigrp interfaces       ! Interfaces EIGRP
show ip eigrp traffic          ! Statistiques de paquets EIGRP
debug eigrp packets            ! Débogage (attention en production)
```

## Comparaison EIGRP vs OSPF vs RIP

| Critère | RIP | OSPF | EIGRP |
|---------|-----|------|-------|
| Algorithme | Bellman-Ford | Dijkstra | DUAL |
| Type | Vecteur de distance | État de lien | Hybride |
| Métrique | Sauts (max 15) | Coût (bande passante) | Composite (bw + délai) |
| Convergence | Lente (minutes) | Rapide (secondes) | Très rapide |
| Scalabilité | Petits réseaux | Grands réseaux | Réseaux Cisco |
| Standard | Ouvert | Ouvert (RFC 2328) | Cisco (RFC 7868) |
| Load balancing | Égal seulement | Égal seulement | Égal et inégal |
| Complexité | Simple | Moyenne | Moyenne |
