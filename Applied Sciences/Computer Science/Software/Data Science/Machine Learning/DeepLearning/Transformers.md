---
title: "Transformers"
domain: "Applied Sciences"
subdomain: "Computer Science > Data Science > Machine Learning > DeepLearning"
tags: [sciences-appliquées, informatique, data-science, machine-learning, deep-learning]
date: "2026-02-22"
---

# Transformers

Les **Transformers** sont une architecture de réseau de neurones introduite en 2017 dans l'article *"Attention Is All You Need"*. Ils ont **révolutionné** le traitement du langage naturel (NLP) et sont aujourd'hui la base des modèles les plus performants (GPT, BERT, Claude, LLaMA, etc.).

## Pourquoi les Transformers ?

Avant les Transformers, les modèles de séquences (RNN, LSTM) avaient deux problèmes majeurs :
1. **Traitement séquentiel** : les tokens sont traités un par un, impossible de paralléliser
2. **Mémoire limitée** : difficulté à capturer les dépendances à longue distance

Les Transformers résolvent ces deux problèmes grâce au mécanisme d'**attention**.

```mermaid
graph LR
    subgraph "RNN / LSTM"
        direction LR
        R1["Token 1"] --> R2["Token 2"] --> R3["Token 3"] --> R4["Token 4"]
    end

    subgraph "Transformer"
        direction LR
        T1["Token 1"] ~~~ T2["Token 2"] ~~~ T3["Token 3"] ~~~ T4["Token 4"]
        T1 <--> T2
        T1 <--> T3
        T1 <--> T4
        T2 <--> T3
        T2 <--> T4
        T3 <--> T4
    end

    style R4 fill:#F44336,color:#fff
    style T1 fill:#4CAF50,color:#fff
    style T2 fill:#4CAF50,color:#fff
    style T3 fill:#4CAF50,color:#fff
    style T4 fill:#4CAF50,color:#fff
```

| | RNN / LSTM | Transformer |
|---|---|---|
| **Traitement** | Séquentiel | Parallèle |
| **Dépendances longues** | Difficile | Facile (attention) |
| **Vitesse d'entraînement** | Lent | Rapide (GPU) |
| **Scalabilité** | Limitée | Excellente |

## Le mécanisme d'attention (Self-Attention)

L'idée clé : pour comprendre un mot, le modèle **regarde tous les autres mots** de la phrase et décide lesquels sont importants.

### Queries, Keys, Values (Q, K, V)

Chaque token est projeté en trois vecteurs :
- **Query (Q)** : "Que cherche ce token ?"
- **Key (K)** : "Que contient ce token ?"
- **Value (V)** : "Quelle information transmettre ?"

**Formule de l'attention :**

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$

- $QK^T$ : score de similarité entre chaque paire de tokens
- $\sqrt{d_k}$ : facteur de normalisation (dimension des clés)
- $\text{softmax}$ : transforme les scores en probabilités
- Multiplication par $V$ : pondérer les valeurs par l'attention

```mermaid
graph TB
    INPUT["Entrée (tokens)"] --> Q["Projection Q<br/>(Query)"]
    INPUT --> K["Projection K<br/>(Key)"]
    INPUT --> V["Projection V<br/>(Value)"]

    Q --> MATMUL1["Q × Kᵀ"]
    K --> MATMUL1
    MATMUL1 --> SCALE["÷ √dₖ"]
    SCALE --> SOFT["Softmax"]
    SOFT --> MATMUL2["× V"]
    V --> MATMUL2
    MATMUL2 --> OUT["Sortie<br/>(représentation contextualisée)"]

    style INPUT fill:#2196F3,color:#fff
    style SOFT fill:#FF9800,color:#fff
    style OUT fill:#4CAF50,color:#fff
```

### Multi-Head Attention

Plutôt qu'une seule attention, on en fait **plusieurs en parallèle** (les "heads"), chacune capturant des **relations différentes** :

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \dots, \text{head}_h) W^O$$

- Chaque head capture un type de relation différent (syntaxe, sémantique, coréférence...)
- Les résultats sont concaténés puis projetés

## Architecture complète

```mermaid
graph TB
    subgraph "Encodeur (x N)"
        direction TB
        IN_E["Embeddings<br/>+ Position"] --> MHA_E["Multi-Head<br/>Self-Attention"]
        MHA_E --> AN1["Add & Norm"]
        AN1 --> FFN_E["Feed-Forward<br/>Network"]
        FFN_E --> AN2["Add & Norm"]
    end

    subgraph "Décodeur (x N)"
        direction TB
        IN_D["Embeddings<br/>+ Position"] --> MMHA["Masked Multi-Head<br/>Self-Attention"]
        MMHA --> AN3["Add & Norm"]
        AN3 --> CROSS["Cross-Attention<br/>(attend à l'encodeur)"]
        CROSS --> AN4["Add & Norm"]
        AN4 --> FFN_D["Feed-Forward<br/>Network"]
        FFN_D --> AN5["Add & Norm"]
    end

    AN2 --> CROSS
    AN5 --> LINEAR["Linear + Softmax"]
    LINEAR --> OUTPUT["Prédiction<br/>du prochain token"]

    style IN_E fill:#2196F3,color:#fff
    style IN_D fill:#4CAF50,color:#fff
    style OUTPUT fill:#FF5722,color:#fff
```

### Composants clés

| Composant | Rôle |
|-----------|------|
| **Embeddings** | Convertir les tokens en vecteurs numériques |
| **Positional Encoding** | Encoder la position des tokens (le Transformer n'a pas de notion d'ordre) |
| **Self-Attention** | Permettre à chaque token de regarder tous les autres |
| **Masked Attention** | Empêcher le décodeur de "tricher" en regardant les tokens futurs |
| **Cross-Attention** | Le décodeur regarde la sortie de l'encodeur |
| **Feed-Forward** | Réseau dense appliqué indépendamment à chaque position |
| **Add & Norm** | Connexion résiduelle + normalisation (stabilise l'entraînement) |

### Positional Encoding

Les Transformers n'ayant pas de récurrence, il faut **injecter l'information de position** :

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d}}\right)$$
$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d}}\right)$$

Les modèles modernes utilisent souvent des **positional embeddings apprenables** ou **RoPE** (Rotary Position Embedding).

## Les trois familles de Transformers

```mermaid
graph TB
    TRANS["Transformer"] --> ENC["Encoder-only<br/>(Compréhension)"]
    TRANS --> DEC["Decoder-only<br/>(Génération)"]
    TRANS --> ED["Encoder-Decoder<br/>(Séquence → Séquence)"]

    ENC --> BERT2["BERT"]
    ENC --> ROBERTA["RoBERTa"]

    DEC --> GPT2["GPT"]
    DEC --> LLAMA["LLaMA"]
    DEC --> CLAUDE["Claude"]

    ED --> T5["T5"]
    ED --> BART["BART"]

    style TRANS fill:#673AB7,color:#fff
    style ENC fill:#2196F3,color:#fff
    style DEC fill:#4CAF50,color:#fff
    style ED fill:#FF9800,color:#fff
```

| Famille | Principe | Tâches typiques | Exemples |
|---------|---------|-----------------|----------|
| **Encoder-only** | Voit toute la séquence en même temps (bidirectionnel) | Classification, NER, recherche sémantique | BERT, RoBERTa |
| **Decoder-only** | Génère token par token (autorégressif) | Génération de texte, chatbots, code | GPT-4, Claude, LLaMA |
| **Encoder-Decoder** | Encode l'entrée, décode la sortie | Traduction, résumé | T5, BART |

## Les modèles marquants

### BERT (2018)
- **Bidirectional Encoder Representations from Transformers**
- Pré-entraîné avec **Masked Language Modeling** (MLM) : masquer 15% des tokens et prédire les manquants
- Excelle en **compréhension** de texte (classification, QA, NER)
- Bidirectionnel : voit le contexte à gauche ET à droite

### GPT (2018 → GPT-4)
- **Generative Pre-trained Transformer**
- Autorégressif : prédit le **prochain token** à partir des précédents
- Chaque version plus grande et plus performante
- Base des chatbots modernes (ChatGPT)

### LLaMA (2023)
- Modèle **open-source** de Meta
- Performances comparables à GPT-3 avec moins de paramètres
- A lancé l'écosystème des LLM open-source (Mistral, Vicuna, etc.)

## Scaling Laws

Les Transformers suivent des **lois d'échelle** prévisibles :
- Plus de **paramètres** = meilleures performances
- Plus de **données** = meilleures performances
- Plus de **calcul** = meilleures performances

La relation est logarithmique : doubler les performances nécessite ~10x plus de ressources.

## Au-delà du NLP

Les Transformers ne sont plus limités au texte :

| Domaine | Application | Modèle |
|---------|-------------|--------|
| **Vision** | Classification d'images | ViT (Vision Transformer) |
| **Audio** | Transcription | Whisper |
| **Multimodal** | Texte + Image | GPT-4V, LLaVA |
| **Protéines** | Prédiction de structure | AlphaFold 2 |
| **Code** | Génération de code | Codex, StarCoder |
| **Musique** | Génération musicale | MusicLM |
