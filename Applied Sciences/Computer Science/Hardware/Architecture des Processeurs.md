---
title: "Architecture des Processeurs"
domain: "Applied Sciences"
subdomain: "Computer Science > Hardware"
tags: [sciences-appliquées, informatique]
date: "2026-02-24"
---

# Architecture des Processeurs

Un processeur (CPU — Central Processing Unit) est le cerveau d'un ordinateur. Il exécute les instructions des programmes en effectuant des opérations arithmétiques, logiques et de contrôle.

## Architecture de von Neumann

Proposée en 1945, elle est la base de quasiment tous les ordinateurs modernes.

```
┌──────────────────────────────────────┐
│              Mémoire                  │
│    (instructions + données mélangées) │
└───────────────┬──────────────────────┘
                │ bus
┌───────────────▼──────────────────────┐
│                CPU                    │
│  ┌───────────┐   ┌─────────────────┐  │
│  │    ALU    │   │   Unité Ctrl    │  │
│  │ (calculs) │   │ (décodage instr)│  │
│  └───────────┘   └─────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │          Registres              │  │
│  └─────────────────────────────────┘  │
└──────────────────────────────────────┘
         │
   Périphériques E/S
```

**Limitation de von Neumann** : le goulot d'étranglement von Neumann — le bus partagé entre instructions et données limite les performances. Solutions modernes : caches séparés L1i (instructions) et L1d (données).

**Architecture Harvard** : sépare physiquement les mémoires d'instructions et de données. Utilisée dans les microcontrôleurs (Arduino, PIC) et les DSP. Permet des accès simultanés aux deux mémoires.

## Composants d'un CPU

### Unité Arithmétique et Logique (ALU)

Effectue les opérations de base : addition, soustraction, ET, OU, XOR, décalages binaires, comparaisons. Les opérations à virgule flottante sont souvent déléguées à une FPU (Floating Point Unit) séparée.

### Unité de Contrôle (Control Unit)

Décode les instructions et coordonne les autres composants. Elle lit l'instruction pointée par le registre IP (Instruction Pointer), la décode, génère les signaux de contrôle appropriés.

### Registres

Mémoire ultra-rapide intégrée au CPU. Quelques dizaines à quelques centaines de registres selon l'architecture.

Registres x86-64 principaux :

| Registre | Taille | Usage traditionnel |
|---|---|---|
| RAX | 64 bits | Accumulateur, valeur de retour |
| RBX | 64 bits | Base pointer |
| RCX | 64 bits | Compteur de boucle |
| RDX | 64 bits | Données, E/S |
| RSP | 64 bits | Stack pointer (sommet de pile) |
| RBP | 64 bits | Base pointer (frame actuel) |
| RSI | 64 bits | Source index |
| RDI | 64 bits | Destination index |
| RIP | 64 bits | Instruction pointer (PC) |
| R8-R15 | 64 bits | Usage général (x86-64 seulement) |
| RFLAGS | 64 bits | Drapeaux (zéro, retenue, signe, overflow) |

Les registres sont aussi accessibles en 32 bits (EAX), 16 bits (AX) et 8 bits (AL, AH) pour la compatibilité.

## Pipeline d'instructions

Le pipeline permet d'exécuter plusieurs instructions simultanément en les divisant en étapes.

Pipeline classique à 5 étages (RISC) :

```
Cycle :  1   2   3   4   5   6   7   8
Instr 1: IF  ID  EX  MEM WB
Instr 2:     IF  ID  EX  MEM WB
Instr 3:         IF  ID  EX  MEM WB
Instr 4:             IF  ID  EX  MEM WB

IF  = Instruction Fetch — lecture de l'instruction en mémoire
ID  = Instruction Decode — décodage et lecture des registres
EX  = Execute — exécution dans l'ALU
MEM = Memory access — lecture/écriture en mémoire
WB  = Write Back — écriture du résultat dans le registre
```

En théorie, avec 5 étages, on traite jusqu'à 5 instructions simultanément.

### Hazards (aléas)

Situations qui empêchent le pipeline de progresser normalement.

**Aléa de données (Data Hazard)** : une instruction dépend du résultat d'une instruction précédente non encore terminée.

```
ADD R1, R2, R3    # R1 = R2 + R3
SUB R4, R1, R5    # R4 = R1 - R5 → R1 pas encore disponible !
```

Solutions : stall (attendre), forwarding/bypassing (transmettre le résultat directement sans passer par WB), réordonnancement des instructions par le compilateur.

**Aléa de contrôle (Control Hazard)** : les branchements conditionnels (if, boucles) invalident les instructions déjà dans le pipeline.

Solution : prédiction de branchement. Le CPU prédit si un branchement sera pris ou non et continue à remplir le pipeline. En cas d'erreur de prédiction : flush du pipeline + pénalité de 10-20 cycles. Les CPUs modernes ont des prédicteurs avec > 95% de précision.

**Aléa structurel (Structural Hazard)** : deux instructions veulent utiliser la même ressource matérielle simultanément.

Solution : duplication des ressources (plusieurs ALUs, ports mémoire).

## RISC vs CISC

| Dimension | RISC | CISC |
|---|---|---|
| Signification | Reduced Instruction Set Computer | Complex Instruction Set Computer |
| Instructions | Peu nombreuses, taille fixe | Nombreuses, taille variable |
| Complexité | Dans le compilateur | Dans le matériel |
| Exemples | ARM, RISC-V, MIPS, PowerPC | x86, x86-64, VAX |
| Pipeline | Simple, régulier | Complexe |
| Mémoire | Load/Store uniquement | Opérations directes sur mémoire |
| Performances | Élevées par MHz sur code simple | Meilleur code dense |

Note : les CPUs x86-64 modernes (Intel, AMD) traduisent en interne les instructions CISC complexes en micro-opérations RISC-like. Le x86-64 visible est CISC, mais l'exécution interne est RISC.

## Superscalarité et Out-of-Order Execution

### Superscalarité

Un CPU superscalaire peut émettre et exécuter plusieurs instructions par cycle d'horloge en dupliquant les unités d'exécution. Un Core i9 peut émettre jusqu'à 6 micro-ops par cycle.

### Exécution hors ordre (Out-of-Order Execution)

Le CPU réordonne les instructions pour minimiser les stalls, tout en respectant les dépendances. Il maintient un pool d'instructions prêtes à être exécutées (Reorder Buffer) et les exécute dans l'ordre optimal.

### Exécution spéculative

Le CPU exécute des instructions "à l'avance" sans être sûr qu'elles seront nécessaires (prédiction de branchement, spéculation de mémoire). Si la prédiction était fausse, les résultats sont annulés. C'est à l'origine des failles Spectre et Meltdown (2018).

## Niveaux de cache

Le cache est une mémoire rapide entre le CPU et la RAM, exploitant la localité temporelle et spatiale.

| Niveau | Taille typique | Latence | Partagé |
|---|---|---|---|
| Registres | ~1 Ko | ~0.3 ns (1 cycle) | Non — par cœur |
| L1 (instructions + données) | 32-64 Ko | ~1 ns (4 cycles) | Non — par cœur |
| L2 | 256 Ko – 1 Mo | ~3-10 ns (12 cycles) | Non — par cœur |
| L3 (Last Level Cache) | 8-64 Mo | ~30-40 ns (40 cycles) | Partagé entre cœurs |
| RAM (DRAM) | 8-256 Go | ~60-100 ns (200 cycles) | Partagée |
| SSD NVMe | To | ~0.1 ms | Partagé |
| HDD | To | ~5-10 ms | Partagé |

**Localité temporelle** : si une donnée est accédée, elle le sera probablement à nouveau bientôt → garder en cache.

**Localité spatiale** : si une donnée est accédée, les données voisines le seront probablement → charger des lignes de cache entières (64 octets).

## Fréquence, IPC et TDP

**Fréquence (GHz)** : nombre de cycles par seconde. Plus de cycles = plus d'instructions potentielles. Mais augmenter la fréquence augmente la chaleur quadratiquement.

**IPC (Instructions Per Cycle)** : nombre moyen d'instructions exécutées par cycle. Dépend de l'architecture. Un Cortex-A78 exécute plus d'instructions par cycle qu'un Pentium 4 à même fréquence.

**Performances = Fréquence × IPC × Nombre de cœurs** (simplification)

**TDP (Thermal Design Power)** : puissance thermique maximale en watts. Un CPU 125W TDP dissipe jusqu'à 125W qu'il faut évacuer.

## Multi-core et Hyper-Threading

**Multi-core** : plusieurs cœurs physiques sur le même die. Chaque cœur est un CPU complet avec ses propres registres et caches L1/L2. Les cœurs se partagent le cache L3 et l'accès à la RAM.

**HyperThreading (Intel) / SMT (AMD)** : présente 2 threads logiques par cœur physique. Chaque thread a ses propres registres et un reorder buffer, mais partage les unités d'exécution. Gain de 15-30% sur les charges parallèles, perte potentielle sur les charges à thread unique intense.

## GPU vs CPU

| Critère | CPU | GPU |
|---|---|---|
| Cœurs | 8-64 cœurs puissants | Milliers de cœurs simples |
| Optimisé pour | Tâches séquentielles complexes | Calcul parallèle massif |
| Cache | Grand (L3 jusqu'à 64 Mo) | Petit mais très haute bande passante |
| Mémoire | RAM (DDR5) | VRAM (GDDR6, HBM) |
| Usage | Logique générale, OS, BDD | Rendu 3D, ML, calcul scientifique |
| Architecture | Quelques threads très rapides | Milliers de threads modestes (SIMD) |

## Architectures récentes

| Architecture | Entreprise | Usage | Points clés |
|---|---|---|---|
| x86-64 (Zen 5) | AMD | Desktop/Serveur | Haute performance, IPC élevé |
| x86-64 (Core Ultra) | Intel | Desktop/Laptop | Hybride Performance+Efficiency cores |
| ARMv9 (Cortex-X4) | ARM | Mobile, Apple Silicon | Excellent rapport perf/watt |
| Apple M4 | Apple | Mac, iPad | Architecture unifiée CPU+GPU+NPU |
| RISC-V | Open Source | Embarqué, IoT | ISA libre, croissance forte |
