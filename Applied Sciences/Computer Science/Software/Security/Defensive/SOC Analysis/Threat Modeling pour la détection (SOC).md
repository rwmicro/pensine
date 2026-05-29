---
title: "Threat Modeling pour la détection (SOC)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc, threat-modeling, detection]
date: "2026-05-29"
---

# Threat Modeling pour la détection (SOC)

> Pour le cadre général (4 questions de Shostack, DFD, STRIDE, DREAD, PASTA, arbres d'attaque, CVSS, intégration SDLC), voir la note canonique `[[Threat Modeling]]`. Cette note se concentre sur l'**usage défensif** du threat modeling côté SOC : transformer un modèle de menace en couverture de détection.

Côté SOC, le threat modeling ne sert pas à concevoir un système sécurisé mais à répondre à une question opérationnelle : **« contre quelles techniques d'attaque sommes-nous capables de détecter, et où sont nos angles morts ? »**

## De STRIDE/DFD vers la détection

1. Partir des **trust boundaries** du DFD (cf. `[[Threat Modeling]]`) : ce sont les points où une attaque devient observable (entrée utilisateur → backend, internet → DMZ).
2. Pour chaque menace STRIDE identifiée, se demander **quel artefact de log elle produirait** (event Windows, log proxy, NetFlow, télémétrie EDR).
3. Vérifier qu'une **règle de détection** existe pour cet artefact — sinon, c'est un angle mort à combler. Voir `[[Detection Engineering]]` et `[[Sigma]]`.

## MITRE ATT&CK Navigator comme carte de couverture

C'est l'outil central du threat modeling défensif (`mitre-attack.github.io/attack-navigator/`) :

- Cartographier en **heatmap** les techniques (TTP) que l'on sait détecter aujourd'hui.
- Superposer le **profil d'un acteur de menace** pertinent (cf. `[[APT et Acteurs de la Menace]]` et `[[Threat Intelligence]]`) pour prioriser : on couvre d'abord les techniques des adversaires qui nous ciblent réellement.
- Le différentiel entre « ce que fait l'adversaire » et « ce qu'on détecte » donne la **feuille de route de détection**.

## Priorisation par le risque

Le SOC priorise ses efforts de détection avec les mêmes outils que la note canonique — **CVSS**, **matrice probabilité × impact**, et les **stratégies de traitement** (mitigate / transfer / accept / avoid) — mais appliqués à la *capacité de détection* plutôt qu'à la vulnérabilité elle-même : une technique à fort impact et fréquemment utilisée par les APT du secteur passe en tête du backlog de detection engineering.

## Voir aussi

- `[[Threat Modeling]]` — cadre général (conception sécurisée, frameworks)
- `[[Detection Engineering]]`, `[[Sigma]]`, `[[Threat Hunting]]`
- `[[Threat Intelligence]]`, `[[APT et Acteurs de la Menace]]`
