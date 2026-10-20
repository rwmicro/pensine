---
title: "Index — Application Security"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Application Security"
tags: [appsec, index, moc, sast, dast, sca, ci-cd, supply-chain]
date: "2026-10-20"
prerequis: ["[[Secure SDLC]]", "[[Threat Modeling]]"]
---

# Index — Application Security

L'Application Security couvre la sécurité du code, des dépendances, du pipeline et des artefacts. Elle ne se réduit pas à une liste d'outils : elle organise des points de contrôle dans le cycle de développement, depuis la conception jusqu'au déploiement et à la réponse à incident.

Cet index relie les notes du dossier `Application Security/` aux notes transverses de `Secure SDLC`, `Threat Modeling`, `Supply Chain Attacks` et `Sécurité des données`.

## Notes du dossier

| Note | Objet | Question directrice |
|---|---|---|
| [[Sécurité CI-CD et chaîne d'approvisionnement]] | Pipeline, runners, secrets, OIDC, provenance, SBOM, signatures | Peut-on prouver qu'un artefact déployé provient bien du code revu ? |
| [[SAST, DAST et SCA]] | Analyse statique, dynamique, dépendances, secrets, IaC, conteneurs | Quels défauts sont détectés, à quel stade, et avec quel taux de faux positifs ? |

## Parcours de lecture

| Étape | Contenu | Objectif |
|---|---|---|
| 1 | [[Secure SDLC]] | Situer les activités de sécurité dans le cycle de développement |
| 2 | [[Threat Modeling]] | Identifier les menaces avant d'écrire le code |
| 3 | [[SAST, DAST et SCA]] | Choisir les analyses et les intégrer au pipeline |
| 4 | [[Sécurité CI-CD et chaîne d'approvisionnement]] | Protéger le build, les artefacts et les dépendances |
| 5 | [[Supply Chain Attacks]] | Comprendre les attaques réelles et les modes de compromission |
| 6 | [[Sécurité des données]] | Protéger les données manipulées par l'application |

## Points de contrôle

- **Conception** : modèle de menace, exigences de sécurité, revue d'architecture.
- **Code** : revue sécurisée, SAST, règles propres au langage, secrets.
- **Dépendances** : SCA, lockfiles, SBOM, provenance, signatures.
- **Build** : runners éphémères, permissions minimales, OIDC, cache contrôlé.
- **Artefacts** : signature, attestation, registre privé, politique de rétention.
- **Déploiement** : environnements protégés, approbations, vérification de signature.
- **Production** : DAST, tests d'intrusion, surveillance, réponse à incident.

## Liens transverses

- [[API Security]] et [[Sécurité des API bancaires]] pour les interfaces exposées.
- [[Cloud Security]] et [[Kubernetes Security]] pour les plateformes de déploiement.
- [[Detection Engineering]] et [[SIEM (Security Information and event Management)]] pour la détection des abus.
- [[NIS2 et DORA]] pour les obligations de sécurité de la chaîne d'approvisionnement.

> [!abstract] Définition — Application Security
> L'Application Security est l'ensemble des pratiques qui réduisent le risque de vulnérabilité, de compromission et de fuite dans une application et sa chaîne de fabrication. Elle combine des contrôles préventifs (conception, code, dépendances, pipeline) et des contrôles détectifs (analyses, tests, surveillance).

> [!quiz] Pourquoi un pipeline CI/CD est-il une cible de choix pour un attaquant ?
> Parce qu'il possède les identités, les secrets et les droits nécessaires pour produire et déployer des artefacts. Compromettre le pipeline permet de modifier le code ou le binaire sans passer par une revue de code, puis de conserver un accès en production.
