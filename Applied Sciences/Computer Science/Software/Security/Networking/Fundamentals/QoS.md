---
title: "QoS — Quality of Service"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals"
tags: [sciences-appliquées, informatique, réseau, qos]
date: "2026-04-07"
---

# QoS — Quality of Service

La QoS (Quality of Service) est un mécanisme permettant de gérer le trafic réseau de façon à garantir des performances minimales pour certains types de flux, notamment lors de la congestion.

## Problématiques réseau

**Bande passante** : mesure du nombre de bits pouvant transiter par seconde sur un lien.

**Congestion** : situation où le débit entrant dépasse la capacité du lien (ex : flux 150 Mbps sur un lien 100 Mbps). La QoS devient indispensable lors de la congestion.

**Délai** : temps supplémentaire nécessaire à un paquet pour atteindre sa destination.

Sources de délai :
- Délai de codage (code delay)
- Délai de mise en paquets (packetization delay)
- Délai de file d'attente (queuing delay)
- Délai de sérialisation (serialization delay)
- Délai de propagation (propagation delay)
- Délai de désynchronisation (de-jitter delay)

**Gigue (Jitter)** : variation du délai entre les paquets successifs. Particulièrement dommageable pour la voix et la vidéo.

## Types de trafic

| Type | Sensibilité | Caractéristiques |
|------|-------------|-----------------|
| Voix (VoIP) | Délai et perte (très sensible) | Volume faible, temps réel, priorité maximale |
| Vidéo | Délai et gigue | Volume élevé, tolérant aux pertes occasionnelles |
| Données | Perte (très sensible) | TCP retransmet automatiquement les paquets perdus |

## Algorithmes de file d'attente (Queuing)

Le queuing est le mécanisme central de la QoS : gérer les paquets en attente lors de la congestion.

### FIFO (First In First Out)

Le plus simple : les paquets sont transmis dans l'ordre d'arrivée. Pas de priorité, traitement équitable. Efficace sur des liens rapides avec peu de congestion.

```
Paquet A → Paquet B → Paquet C → ...
           (ordre d'arrivée)
```

### WFQ (Weighted Fair Queuing)

Garantit une distribution équitable de la bande passante entre les flux. Attribue des poids selon le type de trafic. Faible performance pour le trafic temps réel.

### CBWFQ (Class-Based WFQ)

Étend WFQ en permettant de définir des classes de trafic avec des bandes passantes garanties. Combiné avec LLQ pour la voix.

### LLQ (Low-Latency Queuing)

Combine CBWFQ avec une file de priorité stricte pour le trafic temps réel (voix, vidéo). Le trafic prioritaire est toujours traité en premier.

### WRED (Weighted Random Early Detection)

Élimine aléatoirement des paquets TCP avant la saturation complète de la file pour prévenir la congestion. Préférence pour les paquets à faible priorité.

## Modèles QoS

### Best-Effort (pas de QoS)

Tous les paquets sont traités de façon identique. Aucune garantie de délai ou de bande passante.

### IntServ (Integrated Services)

Réserve des ressources sur le chemin complet source-destination pour chaque flux (via RSVP — Resource Reservation Protocol). Modèle par circuit. Problème de scalabilité sur les grands réseaux.

### DiffServ (Differentiated Services)

Classe le trafic en groupes (classes) et applique des politiques de traitement par classe. Plus scalable qu'IntServ. Standard actuel en entreprise.

**DSCP (Differentiated Services Code Point)** : champ 6 bits dans l'en-tête IP (anciennement ToS) indiquant la classe de service.

| Classe | DSCP | Usage |
|--------|------|-------|
| EF (Expedited Forwarding) | 46 | Voix, trafic temps réel |
| AF (Assured Forwarding) | 10,12,14,18,20,22,26,28,30,34,36,38 | Vidéo, données importantes |
| CS (Class Selector) | 0,8,16,24,32,40,48,56 | Compatibilité avec les anciens TOS |
| BE (Best Effort) | 0 | Trafic par défaut |

## Configuration QoS Cisco (exemple)

```cisco
! Définir les classes de trafic
class-map match-all VOIX
 match dscp ef

class-map match-all VIDEO
 match dscp af41

! Définir la politique
policy-map QOS_WAN
 class VOIX
  priority 256          ! LLQ — file de priorité stricte (256 kbps)
 class VIDEO
  bandwidth 512         ! CBWFQ — bande passante garantie
 class class-default
  fair-queue            ! WFQ pour le reste

! Appliquer sur une interface
interface Serial0/1/0
 service-policy output QOS_WAN
```

## Marquage du trafic (Traffic Marking)

Le trafic doit être marqué (DSCP, CoS) aussi près de la source que possible, généralement sur les switches d'accès.

```cisco
! Marquer le trafic VoIP entrant
class-map MARQUER_VOIP
 match protocol sip
 match protocol rtp

policy-map MARQUAGE_ENTREE
 class MARQUER_VOIP
  set dscp ef

interface GigabitEthernet0/0
 service-policy input MARQUAGE_ENTREE
```

## Policing vs Shaping

| Mécanisme | Comportement | Usage |
|-----------|-------------|-------|
| Policing | Abandonne ou re-marque les paquets dépassant le débit | Côté réseau (FAI) |
| Shaping | Retarde les paquets dépassant le débit (file d'attente) | Côté client |
