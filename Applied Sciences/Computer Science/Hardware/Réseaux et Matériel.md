---
title: "Réseaux et Matériel"
domain: "Applied Sciences"
subdomain: "Computer Science > Hardware"
tags: [sciences-appliquées, informatique]
date: "2026-02-25"
---

# Réseaux et Matériel

## Interfaces réseau

### NIC — Network Interface Card

La carte réseau est l'interface entre l'ordinateur et le réseau. Elle convertit les données numériques en signaux physiques (électriques, optiques, radio).

**Adresse MAC** : identifiant physique unique gravé dans la NIC. 48 bits (6 octets) en hexadécimal : `AA:BB:CC:DD:EE:FF`. Les 3 premiers octets identifient le fabricant (OUI — Organizationally Unique Identifier). Utilisée uniquement au niveau Ethernet (couche 2 OSI).

```bash
# Linux : voir les interfaces réseau
ip link show
ip addr show
# eth0, ens3, enp2s0 : ethernet câblé
# wlan0, wlp3s0 : WiFi
# lo : loopback (127.0.0.1)
```

### Bus interne

Les périphériques communiquent avec le CPU et la RAM via des bus internes.

**PCIe (PCI Express)** : bus point-à-point sériel haute vitesse. Remplace PCI depuis 2004. Organisé en lanes (x1, x4, x8, x16). Chaque lane PCIe 4.0 = ~2 Go/s dans chaque direction.

| Génération | Bande passante par lane | Bande passante x16 |
|---|---|---|
| PCIe 3.0 | ~1 Go/s | ~16 Go/s |
| PCIe 4.0 | ~2 Go/s | ~32 Go/s |
| PCIe 5.0 | ~4 Go/s | ~64 Go/s |
| PCIe 6.0 | ~8 Go/s | ~128 Go/s |

**USB (Universal Serial Bus)** : bus série pour périphériques externes.

| Standard | Vitesse max | Alimentation |
|---|---|---|
| USB 2.0 | 480 Mbit/s | 2.5W |
| USB 3.2 Gen 1 | 5 Gbit/s | 4.5W |
| USB 3.2 Gen 2 | 10 Gbit/s | 18W |
| USB4 Gen 3×2 | 40 Gbit/s | 100W |
| Thunderbolt 4 | 40 Gbit/s | 100W |

**SATA III** : ~600 Mo/s, pour HDD et SSD 2.5". Interface vieillissante mais omniprésente.

**NVMe (via M.2 ou U.2)** : PCIe direct vers le SSD, 3-14 Go/s selon la génération.

## Cartes mères

La carte mère (motherboard) est le circuit imprimé principal qui connecte tous les composants.

**Chipset** : circuit qui gère la communication entre le CPU, la RAM, les périphériques. Exemples : Intel Z790, AMD B650. Le chipset détermine les fonctionnalités supportées (PCIe lanes, USB générations, overclocking).

**BIOS/UEFI** : firmware stocké dans une puce flash sur la carte mère. Initialise le matériel au démarrage, charge le bootloader.

- **BIOS (Basic Input/Output System)** : ancien firmware 16 bits, limité à 2.2 To de disque bootable (MBR), interface texte.
- **UEFI (Unified Extensible Firmware Interface)** : remplaçant moderne, 64 bits, supporte les disques > 2.2 To (GPT), interface graphique, Secure Boot, PXE boot, UEFI Shell.

**Form Factors** : ATX (305×244 mm), Micro-ATX (244×244 mm), Mini-ITX (170×170 mm). Détermine la taille du boîtier requis.

**Slots** : emplacement pour les composants.
- **DIMM** : slots RAM. DDR4 et DDR5 ne sont pas interchangeables.
- **PCIe x16** : GPU, cartes de capture
- **M.2** : SSD NVMe (ou SATA selon le slot)
- **PCIe x1** : cartes réseau, son, contrôleurs

## Alimentation (PSU)

La PSU (Power Supply Unit) convertit le courant alternatif (220V/50Hz en Europe) en courant continu 3.3V, 5V, 12V pour les composants.

**Rails principaux** :
- 12V : CPU, GPU (la majorité de la puissance)
- 5V : USB, SATA, mémoire
- 3.3V : RAM DDR, certains périphériques

**Efficacité 80 PLUS** : certification indiquant le rendement de la PSU.

| Certification | Rendement à 50% de charge |
|---|---|
| 80 PLUS Bronze | 85% |
| 80 PLUS Silver | 88% |
| 80 PLUS Gold | 92% |
| 80 PLUS Platinum | 94% |
| 80 PLUS Titanium | 96% |

Une PSU 80% efficace consomme 125W pour fournir 100W au système — les 25W sont dissipés en chaleur.

## GPU — Graphics Processing Unit

Le GPU est un processeur massivement parallèle, initialement conçu pour le rendu 3D, maintenant utilisé pour le calcul scientifique et l'IA.

**Architecture** :
- Milliers de cœurs simples (CUDA cores chez NVIDIA, Compute Units chez AMD) vs quelques dizaines de cœurs puissants dans un CPU
- Exécution SIMD (Single Instruction, Multiple Data) : la même instruction appliquée à des milliers de données en parallèle
- Mémoire VRAM (GDDR6, HBM) : très haute bande passante (500 Go/s à 3 To/s pour NVIDIA H100) mais plus petite capacité que la RAM principale

**Modèle de programmation GPU (CUDA/OpenCL)** :

```c
// Exemple CUDA — addition de vecteurs sur GPU
__global__ void additionner(float* a, float* b, float* c, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) c[idx] = a[idx] + b[idx];
}

// Lancement avec 1024 threads par bloc, n/1024 blocs
additionner<<<(n+1023)/1024, 1024>>>(d_a, d_b, d_c, n);
```

**Usage machine learning** : les matrices utilisées dans les réseaux de neurones (multiplication matricielle) sont massivement parallèles → GPU 100-1000x plus rapide que CPU pour l'entraînement.

**Cartes spécialisées IA** : NVIDIA A100/H100/B200, Google TPU (Tensor Processing Unit), AWS Inferentia, AMD MI300X.

## Interconnexion haute performance (Datacenter)

### InfiniBand

Réseau haute performance utilisé dans les clusters HPC et les datacenters IA. Latence < 1 µs, bande passante jusqu'à 400 Gbit/s (HDR200). NVLink de NVIDIA est similaire mais propriétaire, reliant les GPUs directement.

### Fibre Channel

Réseau de stockage dédié (SAN) utilisant la fibre optique. Jusqu'à 64 Gbit/s. Séparé du réseau Ethernet de données.

### RoCE et iWARP

RDMA (Remote Direct Memory Access) over Converged Ethernet : accès direct à la mémoire d'un autre serveur sur le réseau Ethernet, sans impliquer le CPU de la destination. Utilisé dans les clusters de calcul et les systèmes de stockage haute performance.

## Topologies réseau

| Topologie | Description | Avantages | Inconvénients |
|---|---|---|---|
| Bus | Tous reliés à un câble commun | Simple, économique | Collisions, panne = tout le réseau |
| Étoile | Tous reliés à un switch central | Facile de dépanner, isolation | Dépendance au switch central |
| Anneau | Chaque nœud relié aux deux voisins | Pas de collision (token ring) | Panne d'un nœud coupe l'anneau |
| Maillage complet | Chaque nœud relié à tous | Redondance maximale | Coût exponentiel en câblage |
| Maillage partiel | Redondance sur les liens critiques | Compromis coût/redondance | Complexité de routage |
| Arbre | Hiérarchie de switches | Scalable, simple | Goulots d'étranglement en haut |

En pratique, les datacenters utilisent une topologie Spine-Leaf (deux couches de switches) pour garantir la même latence entre n'importe quelles deux machines.

## Équipements réseau

### Switch (commutateur)

Opère au niveau 2 (Ethernet). Apprend les adresses MAC et transfère les trames uniquement vers le port destinataire. Réduit les collisions par rapport aux hubs.

```bash
# Voir la table MAC d'un switch Linux (bridge)
bridge fdb show
```

**VLAN (Virtual LAN)** : segmentation logique du réseau physique. Plusieurs VLANs sur les mêmes câbles physiques, isolés logiquement (802.1Q tagging).

### Routeur

Opère au niveau 3 (IP). Relie des réseaux différents, prend des décisions de routage basées sur les adresses IP. Maintient des tables de routage.

### Firewall matériel

Filtrage de paquets au niveau réseau. Inspecte les en-têtes IP/TCP/UDP selon des règles. Peut opérer au niveau 3 (filtrage par IP), niveau 4 (par port), ou niveau 7 (Deep Packet Inspection).

## ASICs et FPGAs

**ASIC (Application-Specific Integrated Circuit)** : circuit conçu pour une tâche spécifique. Performance maximale, faible consommation, mais coût de design énorme (~10-100 M$ pour les gros ASICs) et non reprogrammable.

Exemples : chips Bitcoin mining, Google TPU, Apple Neural Engine, processeurs réseau (Broadcom Tomahawk pour les switches datacenter).

**FPGA (Field-Programmable Gate Array)** : circuit reconfigurable. Des centaines de milliers de cellules logiques interconnectées via une matrice programmable.

Avantages : programmable après fabrication, prototypage rapide d'ASICs, utilisé quand les volumes ne justifient pas un ASIC.

Usage : télécommunications, trading haute fréquence, accélération algorithmique, prototypage de processeurs.

```vhdl
-- Exemple VHDL — demi-additionneur
entity demi_add is
  Port (A : in  STD_LOGIC;
        B : in  STD_LOGIC;
        S : out STD_LOGIC;  -- Somme
        C : out STD_LOGIC); -- Retenue
end demi_add;

architecture Behavioral of demi_add is
begin
  S <= A XOR B;
  C <= A AND B;
end Behavioral;
```

## Edge Computing

Traitement des données au plus près de leur source (IoT, capteurs) plutôt que dans un datacenter centralisé.

**Motivations** : latence (autonomie des véhicules, chirurgie robotique), bande passante (ne pas tout envoyer vers le cloud), confidentialité (données qui ne quittent pas le site), résilience (fonctionner hors connexion).

**Matériel edge** : NVIDIA Jetson (IA embarquée), Raspberry Pi, Intel NUC, routeurs avec capacité de calcul (AWS Outposts, Azure Stack Edge).
