---
title: "Mémoire et Stockage"
domain: "Applied Sciences"
subdomain: "Computer Science > Hardware"
tags: [sciences-appliquées, informatique]
date: "2026-02-24"
---

# Mémoire et Stockage

## Hiérarchie mémoire

Les systèmes informatiques utilisent plusieurs niveaux de mémoire selon un compromis vitesse / capacité / coût.

```
Vitesse ↑      Registres CPU         ~0.3 ns    Quelques Ko    Coût ↑↑↑
               Cache L1              ~1 ns       32-64 Ko
               Cache L2              ~5 ns       256 Ko - 1 Mo
               Cache L3              ~30 ns      8-64 Mo
               RAM (DRAM)            ~60-100 ns  8-512 Go       Coût ↑
               SSD NVMe              ~0.1 ms     1-8 To
               SSD SATA              ~0.5 ms     1-8 To
               HDD                   ~5-10 ms    1-20 To        Coût ↓
Vitesse ↓      Stockage réseau (NAS) ~ms         Illimité       Coût ↓↓
```

Principe fondamental : on essaie de garder les données fréquemment utilisées dans les niveaux les plus rapides (caches).

## RAM — Mémoire vive

La RAM (Random Access Memory) est la mémoire principale de l'ordinateur. Elle est volatile (les données sont perdues à l'extinction).

### SRAM vs DRAM

| Critère | SRAM (Static RAM) | DRAM (Dynamic RAM) |
|---|---|---|
| Technologie | Bascules (6 transistors/bit) | Condensateurs (1 transistor/bit) |
| Vitesse | Très rapide | Rapide |
| Densité | Faible | Élevée |
| Coût | Élevé | Faible |
| Besoin de refresh | Non | Oui (toutes les ms) |
| Usage | Caches CPU (L1, L2, L3) | Mémoire principale |

### DDR SDRAM (Synchronous Dynamic RAM)

La DDR (Double Data Rate) transfère des données sur les deux fronts de l'horloge (montant et descendant), doublant le débit effectif.

| Standard | Fréquence mémoire | Bande passante (simple canal) |
|---|---|---|
| DDR3 | 1333-2133 MHz | 10.6-17 Go/s |
| DDR4 | 2133-3200 MHz | 17-25.6 Go/s |
| DDR5 | 4800-8400 MHz | 38.4-67.2 Go/s |
| LPDDR5 (mobile) | 3200-6400 MHz | 25.6-51.2 Go/s |

**ECC (Error Correcting Code)** : mémoire avec bits de parité permettant de détecter et corriger les erreurs de bit. Indispensable pour les serveurs et workstations critiques. Légèrement plus lente et plus chère.

**Dual/Quad Channel** : utiliser 2 ou 4 barrettes en parallèle double/quadruple la bande passante. Important pour les processeurs sans VRAM dédiée (AMD APU, Intel avec iGPU).

**Latence CAS (CL)** : délai en cycles entre la demande et la donnée. CL16 à 3200 MHz = 16/3200 MHz = 10 ns. Un CL bas est préférable.

## Cache CPU

### Principes de localité

**Localité temporelle** : si une donnée est accédée, elle le sera probablement à nouveau bientôt. Le cache garde les données récemment utilisées.

**Localité spatiale** : si une donnée est accédée, les données voisines le seront probablement. Le cache charge des lignes de cache entières (cache lines).

**Taille d'une ligne de cache** : 64 octets sur x86-64. Toute lecture ou écriture charge 64 octets en cache, même si on n'accède qu'à un seul octet.

### Politiques de cache

**Write-through** : chaque écriture est immédiatement propagée en mémoire principale. Cohérence garantie, mais chaque écriture est lente.

**Write-back** : les écritures sont d'abord faites dans le cache ; la mémoire principale est mise à jour uniquement quand la ligne de cache est évincée. Plus performant, mais nécessite une gestion de la cohérence (protocole MESI pour les multi-cœurs).

**Politiques de remplacement** :
- LRU (Least Recently Used) : évincer la ligne la moins récemment utilisée
- LFU (Least Frequently Used) : évincer la ligne la moins souvent utilisée
- Pseudo-LRU : approximation de LRU moins coûteuse à implémenter

### Impact sur les performances

```python
# Accès séquentiel — cache-friendly (bonne localité spatiale)
import time
n = 1000
matrice = [[i * n + j for j in range(n)] for i in range(n)]

# Accès ligne par ligne (séquentiel en mémoire)
t0 = time.time()
somme = sum(matrice[i][j] for i in range(n) for j in range(n))
print(f"Ligne par ligne : {time.time() - t0:.3f}s")

# Accès colonne par colonne (sauts en mémoire — cache-unfriendly)
t0 = time.time()
somme = sum(matrice[i][j] for j in range(n) for i in range(n))
print(f"Colonne par colonne : {time.time() - t0:.3f}s")  # 3-10x plus lent
```

## SSD — Solid State Drive

### NAND Flash

Les SSD stockent les données dans des cellules NAND flash. Chaque cellule mémorise une charge électrique représentant 1 à 4 bits.

| Type | Bits/cellule | Endurance (P/E cycles) | Vitesse | Prix |
|---|---|---|---|---|
| SLC (Single Level Cell) | 1 bit | 100 000+ | Très rapide | Très élevé |
| MLC (Multi Level Cell) | 2 bits | 10 000 | Rapide | Élevé |
| TLC (Triple Level Cell) | 3 bits | 3 000 | Standard | Abordable |
| QLC (Quad Level Cell) | 4 bits | 1 000 | Plus lent | Faible |

**Wear Leveling** : algorithme qui distribue les écritures uniformément sur toutes les cellules pour éviter qu'une zone s'use prématurément.

**Write amplification** : écrire 1 octet peut entraîner l'écriture de plusieurs blocs complets (effacement + réécriture). Un bon contrôleur minimise ce phénomène.

**Trim** : commande qui informe le SSD des blocs qui ne sont plus utilisés, permettant un effacement préventif et de meilleures performances.

### Interfaces SSD

| Interface | Connecteur | Vitesse maximale | Usage |
|---|---|---|---|
| SATA III | SATA | ~550 Mo/s | SSD 2.5" classiques, bon marché |
| NVMe (PCIe 3.0 x4) | M.2 / U.2 | ~3500 Mo/s | SSD modernes performants |
| NVMe (PCIe 4.0 x4) | M.2 | ~7000 Mo/s | SSD haut de gamme |
| NVMe (PCIe 5.0 x4) | M.2 | ~14000 Mo/s | SSD ultra-performants (2023+) |

Le goulot d'étranglement de SATA est le protocole lui-même (conçu pour les HDD). NVMe (Non-Volatile Memory Express) est un protocole conçu spécifiquement pour les SSD.

## HDD — Hard Disk Drive

Stockage magnétique rotatif. Les données sont stockées sous forme de magnétisation sur des plateaux métalliques tournant à 5400-15000 RPM.

**Composants** :
- **Plateaux** : disques magnétiques empilés sur un axe
- **Têtes de lecture/écriture** : une par face de plateau, lévitant à quelques nanomètres
- **Bras actuateur** : déplace les têtes radialement
- **Moteur d'axe** : fait tourner les plateaux à vitesse constante

**Latence HDD** :
- Seek time : déplacer la tête sur la piste (~3-10 ms)
- Rotational latency : attendre que le secteur passe sous la tête (0-~4 ms à 7200 RPM)
- Transfer time : lire les données (~0.1 ms pour 1 Mo à 100 Mo/s)

**Avantages des HDD** : coût très bas par Go, grande capacité (jusqu'à 20+ To grand public, 100 To pour les PMR et SMR enterprise).

**Fragmentation** : les HDD sont sensibles à la fragmentation (données éclatées en morceaux non contigus) car les têtes doivent se déplacer entre les fragments. Les SSD ne sont pas affectés par la fragmentation.

## RAID

RAID (Redundant Array of Independent Disks) combine plusieurs disques pour améliorer les performances ou la redondance.

| Niveau | Description | Disques min | Redondance | Performance |
|---|---|---|---|---|
| RAID 0 | Striping — données réparties | 2 | Aucune | Lectures/écritures x2 |
| RAID 1 | Mirroring — copie identique | 2 | 1 disque peut tomber | Lectures x2, écritures identiques |
| RAID 5 | Striping + parité distribuée | 3 | 1 disque peut tomber | Lectures très rapides |
| RAID 6 | Striping + double parité | 4 | 2 disques peuvent tomber | Lectures très rapides |
| RAID 10 | RAID 1 + RAID 0 imbriqués | 4 | 1 disque par miroir | Très rapide |

**Reconstruction** : après remplacement d'un disque défaillant en RAID 5/6, le RAID se reconstruit en recalculant les données manquantes. Pendant la reconstruction, le risque de défaillance d'un second disque est élevé (plusieurs heures/jours pour les grands volumes). C'est pourquoi RAID 6 est préféré pour les grands volumes.

**RAID n'est pas une sauvegarde** : le RAID protège contre une panne matérielle, pas contre les suppressions accidentelles, les corruptions logicielles ou les sinistres.

## Stockage Cloud et en réseau

### NAS — Network Attached Storage

Périphérique de stockage connecté au réseau local (NFS, SMB). Accessible par plusieurs machines simultanément. Ex : Synology, QNAP.

### SAN — Storage Area Network

Réseau dédié au stockage (Fibre Channel, iSCSI). Le stockage est vu comme un disque local par le serveur. Utilisé dans les datacenters.

### Stockage Objet (Object Storage)

Modèle sans hiérarchie de répertoires. Chaque objet est stocké avec un identifiant unique (key) et des métadonnées. Scalable à l'infini horizontalement. Ex : AWS S3, MinIO, Ceph.

```
Système de fichiers :    /home/user/documents/rapport.pdf
Stockage objet :         bucket-nom/rapport-2024-alice.pdf  (+ métadonnées JSON)
```

### Comparaison des modèles de stockage

| Modèle | Accès | Scalabilité | Cas d'usage |
|---|---|---|---|
| Fichiers (NFS/SMB) | Hiérarchique | Limitée | Partage réseau local |
| Blocs (SAN/iSCSI) | Secteurs | Élevée | BDD, VMs |
| Objet (S3) | HTTP/API | Quasi-illimitée | Médias, backups, data lake |
