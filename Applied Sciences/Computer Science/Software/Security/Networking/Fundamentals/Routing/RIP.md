---
title: "RIP — Routing Information Protocol"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals > Routing"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2025-05-04"
---

# RIP — Routing Information Protocol

**RIP** est l'un des premiers protocoles de routage dynamique. Il permet aux routeurs d'échanger automatiquement leurs tables de routage pour se mettre d'accord sur les chemins disponibles dans un réseau.


## Principe de fonctionnement

RIP utilise l'algorithme de **Bellman-Ford** (vecteur de distance) :

- Chaque routeur connaît ses voisins directs et leur distance
- Il partage périodiquement sa table de routage à tous ses voisins (toutes les **30 secondes**)
- Chaque routeur met à jour sa propre table en choisissant le chemin avec le moins de **sauts** (hops)

```
Routeur A → Routeur B → Routeur C → Destination
  0 hop       1 hop       2 hops       3 hops
```

La **métrique** de RIP = nombre de sauts. Maximum : **15 hops**. À 16 = destination considérée inaccessible.


## Versions

| Version | Caractéristiques |
|---------|-----------------|
| **RIPv1** | Sans classe (classful), pas d'authentification, broadcast |
| **RIPv2** | Avec masque de sous-réseau (CIDR), authentification MD5, multicast (224.0.0.9) |
| **RIPng** | Version pour IPv6 |


## Avantages

- **Simple à configurer** — idéal pour les petits réseaux ou l'apprentissage
- Supporté par tous les équipements réseau
- Convergence automatique (le réseau se reconfigure en cas de panne)


## Limites

| Problème | Détail |
|----------|--------|
| **15 hops max** | Inutilisable sur les grands réseaux |
| **Convergence lente** | Jusqu'à plusieurs minutes pour propager un changement |
| **Bande passante** | Envoie toute la table toutes les 30s, même si rien n'a changé |
| **Boucles de routage** | Risque de compter à l'infini (*count to infinity*) |
| **Pas de topologie** | Ne connaît que les distances, pas la carte du réseau |


## Comparaison avec OSPF

| | RIP | OSPF |
|--|-----|------|
| Algorithme | Vecteur de distance | État de lien (Dijkstra) |
| Métrique | Sauts | Bande passante |
| Limite | 15 hops | Illimité |
| Convergence | Lente | Rapide |
| Usage | Petits réseaux / labs | Réseaux d'entreprise |


## Configuration Cisco (exemple)

```cisco
router rip
 version 2
 network 192.168.1.0
 network 10.0.0.0
 no auto-summary
```

### Configuration RIPng (IPv6)

```cisco
ipv6 router rip RIP-PROCESS
 !
interface GigabitEthernet0/0
 ipv6 rip RIP-PROCESS enable
```

### Vérification

```cisco
show ip route rip
show ip rip database
show ip protocols
debug ip rip
```

## Méthodes de transmission en routage

| Méthode | Description |
|---------|-------------|
| Unicast | Envoi d'un paquet d'une source vers une destination unique |
| Multicast | Envoi d'un paquet d'une source vers plusieurs destinations |
| Broadcast | Envoi d'un paquet d'une source vers toutes les destinations |
| Anycast | Envoi vers plusieurs destinations, généralement la plus proche |
| Geocast | Envoi vers plusieurs destinations dans une zone géographique |

## Routing statique vs dynamique

Le routing statique est configuré manuellement par l'administrateur réseau. Il ne s'adapte pas automatiquement aux changements de topologie. Adapté aux petits réseaux stables.

Le routing dynamique (RIP, OSPF, EIGRP) met à jour automatiquement les tables de routage lorsque la topologie change.

### Configuration de routage statique (Cisco)

```cisco
! Via next-hop address
ip route 192.168.2.0 255.255.255.0 10.0.0.2

! Via exit interface
ip route 192.168.2.0 255.255.255.0 Serial0/1/0

! Route par défaut
ip route 0.0.0.0 0.0.0.0 10.0.0.1
```
