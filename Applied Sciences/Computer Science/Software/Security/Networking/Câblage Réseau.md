---
title: "Câblage Réseau"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking"
tags: [sciences-appliquées, informatique, réseau, câblage, physique]
date: "2026-04-07"
---

# Câblage Réseau

Le câblage est le support de transmission physique des données dans un réseau filaire. Le choix du type de câble influence directement la vitesse de transmission, la fiabilité et la scalabilité du réseau.

## Types de câbles

### Câble coaxial

Composé de quatre couches concentriques :
1. Conducteur central en cuivre (transmission de données)
2. Isolant en plastique
3. Tresse en cuivre (conducteur secondaire et blindage)
4. Gaine extérieure (protection physique)

Anciennement utilisé comme câble réseau principal. Aujourd'hui largement remplacé par la fibre optique et les câbles UTP/STP dans les infrastructures modernes.

### Câble UTP (Unshielded Twisted Pair)

4 paires de fils torsadés (8 fils au total) avec code couleur, à raison de 6 torsades par pouce pour réduire les interférences électromagnétiques.

**Avantages** : peu coûteux, facile à installer, adapté aux réseaux de petite à moyenne taille.

### Câble STP (Shielded Twisted Pair)

Similaire à l'UTP mais avec une gaine de blindage supplémentaire pour réduire les interférences électromagnétiques dans des environnements perturbés.

### Câble fibre optique

Transmet les données sous forme d'impulsions lumineuses. Très rapide, très fiable et peu sensible aux interférences électromagnétiques.

**Avantages** :
- Débit le plus élevé (jusqu'à des Tbps)
- Immunité aux interférences électromagnétiques
- Grande distance de transmission
- Plus fin et plus léger que le cuivre

## Types de câblage Ethernet

### Câble droit (Straight-Through)

Connecte des équipements de types différents : ordinateur vers switch, switch vers routeur.

Configuration :
- Les deux extrémités ont le même câblage (568A ou 568B)
- Pin 1 → Pin 1, Pin 2 → Pin 2, etc.

### Câble croisé (Crossover)

Connecte des équipements de même type : switch vers switch, PC vers PC.

Configuration :
- Une extrémité en 568A, l'autre en 568B
- Les paires émission/réception sont inversées

**Remarque** : les équipements modernes avec Auto-MDIX détectent automatiquement et ajustent, rendant le câble croisé souvent inutile.

### Câble console (Rollover)

Câble série utilisé pour accéder à la console de configuration des équipements Cisco (routeurs, switches). Configuration inversée d'une extrémité à l'autre.

## Comparaison Hub vs Switch

| Critère | Hub | Switch |
|---------|-----|--------|
| Couche OSI | Couche 1 (Physique) | Couche 2 (Liaison) |
| Domaine de collision | Unique (partagé) | Séparé par port |
| Adressage | Broadcast vers tous les ports | Unicast vers le port cible |
| Table MAC | Non | Oui (CAM table) |
| Bande passante | Partagée | Dédiée par port |
| Performance | Diminue avec le nombre d'équipements | Stable |
| Usage actuel | Quasi-disparu | Standard |

## Catégories de câbles UTP

| Catégorie | Bande passante | Débit max | Usage |
|-----------|---------------|-----------|-------|
| Cat 5 | 100 MHz | 100 Mbps | Ethernet 100Base-TX (obsolète) |
| Cat 5e | 100 MHz | 1 Gbps | Gigabit Ethernet (courant) |
| Cat 6 | 250 MHz | 10 Gbps (jusqu'à 55 m) | Gigabit et 10GbE courts |
| Cat 6a | 500 MHz | 10 Gbps (jusqu'à 100 m) | 10GbE |
| Cat 7 | 600 MHz | 10 Gbps | Data centers |
| Cat 8 | 2000 MHz | 25-40 Gbps | Data centers haute densité |
