---
title: "Pyramid Attention Module (PAM)"
domain: "Applied Sciences"
subdomain: "Computer Science > Data Science > Machine Learning > DeepLearning"
tags: [sciences-appliquées, informatique, data-science, machine-learning, deep-learning]
date: "2026-02-22"
---

# Pyramid Attention Module (PAM)

Le **Pyramid Attention Network** (PAN) est une architecture de réseau de neurones conçue pour la **segmentation sémantique**. Son composant clé, le **Pyramid Attention Module**, combine des informations à **différentes échelles** grâce à des mécanismes d'attention, permettant de capturer à la fois les détails fins et le contexte global.

## Le problème : capturer le contexte multi-échelle

En segmentation sémantique, il faut comprendre une image à **plusieurs niveaux** :
- **Niveau local** : textures, contours, petits détails
- **Niveau global** : structure de la scène, relations entre objets

Les CNN classiques perdent progressivement les détails fins en empilant les couches. Le PAM résout ce problème.

```mermaid
graph TB
    subgraph "Le défi de la segmentation sémantique"
        IMG["Image d'entrée"] --> LOCAL["Détails locaux<br/>(contours, textures)"]
        IMG --> GLOBAL["Contexte global<br/>(structure de la scène)"]
        LOCAL --> COMBINE["Comment combiner<br/>les deux ?"]
        GLOBAL --> COMBINE
        COMBINE --> SEG["Segmentation<br/>pixel par pixel"]
    end

    style IMG fill:#2196F3,color:#fff
    style COMBINE fill:#FF9800,color:#fff
    style SEG fill:#4CAF50,color:#fff
```

## Qu'est-ce que l'attention ?

Le mécanisme d'**attention** permet au réseau de se **concentrer** sur les parties les plus pertinentes de l'entrée, plutôt que de traiter toutes les informations de manière égale.

**Analogie :** quand vous lisez une phrase, votre regard se concentre sur certains mots clés plutôt que de traiter chaque mot uniformément. L'attention fait la même chose dans un réseau de neurones.

### Types d'attention

| Type | Description | Où elle opère |
|------|-------------|--------------|
| **Attention spatiale** | Quelles **régions** de l'image sont importantes ? | Sur les positions (H x W) |
| **Attention par canal** | Quelles **feature maps** sont importantes ? | Sur les canaux (C) |
| **Self-attention** | Quelles parties de l'entrée sont liées entre elles ? | Relations globales |

## Architecture du Pyramid Attention Network

![Architecture du Pyramid Attention Network](https://ars.els-cdn.com/content/image/1-s2.0-S2589004222002036-fx1_lrg.jpg)

Le PAN combine deux modules principaux :

```mermaid
graph TB
    INPUT["Image d'entrée"] --> ENCODER["Encodeur<br/>(Feature Pyramid)"]

    ENCODER --> F1["Features haute résolution<br/>(détails fins)"]
    ENCODER --> F2["Features moyenne résolution"]
    ENCODER --> F3["Features basse résolution<br/>(contexte global)"]

    F1 --> FPA["Feature Pyramid<br/>Attention Module"]
    F2 --> FPA
    F3 --> FPA

    F1 --> GAU["Global Attention<br/>Upsample Module"]
    F2 --> GAU
    F3 --> GAU

    FPA --> MERGE["Fusion"]
    GAU --> MERGE
    MERGE --> OUTPUT["Segmentation"]

    style INPUT fill:#2196F3,color:#fff
    style FPA fill:#FF9800,color:#fff
    style GAU fill:#E91E63,color:#fff
    style OUTPUT fill:#4CAF50,color:#fff
```

### Feature Pyramid Attention (FPA)

Le module FPA extrait des informations contextuelles à **plusieurs échelles** en utilisant une structure pyramidale :

1. L'image passe par des branches à **différentes résolutions** (comme une pyramide)
2. Chaque branche capture un **niveau de contexte** différent
3. Un mécanisme d'**attention** pondère l'importance de chaque échelle
4. Les résultats sont **fusionnés** pour produire une représentation riche

### Global Attention Upsample (GAU)

Le module GAU utilise l'attention globale pour guider le **sur-échantillonnage** (upsampling) :

1. Les features de **haut niveau** (basse résolution, riche en sémantique) sont utilisées pour générer des poids d'attention
2. Ces poids guident le **sur-échantillonnage** des features de bas niveau
3. Cela permet de récupérer les **détails spatiaux** tout en conservant la compréhension sémantique

## Comparaison avec d'autres approches

| Architecture | Approche multi-échelle | Points forts | Points faibles |
|---|---|---|---|
| **FCN** | Pas de multi-échelle | Simple | Perd les détails fins |
| **U-Net** | Skip connections | Bon pour les détails | Pas d'attention |
| **PSPNet** | Pyramid Pooling | Bon contexte global | Attention limitée |
| **DeepLab** | Atrous convolutions | Flexible | Coûteux en calcul |
| **PAN** | Pyramid Attention | Contexte + détails + attention | Plus complexe |

## Segmentation sémantique : rappel

La segmentation sémantique consiste à attribuer une **classe** à **chaque pixel** d'une image :

| Tâche | Entrée | Sortie |
|-------|--------|--------|
| Classification | Image entière | 1 étiquette ("chat") |
| Détection d'objets | Image entière | Boîtes englobantes + étiquettes |
| **Segmentation sémantique** | Image entière | 1 étiquette **par pixel** |
| Segmentation d'instances | Image entière | 1 étiquette par pixel + distinction entre instances |

## Ressources

- [Repo GitHub — Pyramid Attention Networks](https://github.com/SHI-Labs/Pyramid-Attention-Networks)
- [Review: PAN — Pyramid Attention Network for Semantic Segmentation](https://sh-tsang.medium.com/review-pan-pyramid-attention-network-for-semantic-segmentation-semantic-segmentation-8d94101ba24a)
