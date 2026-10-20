---
title: "LFCS Q08 — Gestion des disques"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, disk, management]
date: "2026-08-09"
---

# Question 8 — Gestion des disques

## Notes d'apprentissage

Cet exercice mélange trois compétences distinctes : préparer un disque, lire l'occupation disque, et relier un processus au disque qui porte son exécutable. Le fil conducteur est le **chemin du périphérique au point de montage**.

**Modèle mental : du bloc au répertoire.**

```
disque brut        partition/      système de        point de
/dev/vdb     ──►   formatage    ──► fichiers     ──►  montage
                   mkfs.ext4        (ext4, xfs...)    /mnt/backup-black
```

Un disque (`/dev/vdb`) n'est qu'un tableau d'octets. Pour y stocker des fichiers, il faut un **système de fichiers** (`mkfs.ext4`), puis le **monter** dans l'arborescence (`mount`). Tant qu'il n'est pas monté, son contenu est inaccessible.

> [!important] Idée clé
> Le point de montage n'est qu'une indirection : monter un disque sur un répertoire qui contient déjà des fichiers ne les supprime pas, il les rend juste invisibles tant que le montage est actif. C'est une source de confusion classique en prod (« où sont passés mes fichiers ? ») — toujours vérifier qu'un point de montage est vide avant d'y monter quoi que ce soit.

**Inventaire des disques :**
```bash
lsblk                 # arbre clair : disques, partitions, points de montage, tailles
sudo fdisk -l         # détails bas niveau (secteurs, table de partition)
blkid                 # UUID et type de système de fichiers de chaque périphérique
```

**Formater et monter :**
```bash
sudo mkfs.ext4 /dev/vdb                     # créer un système de fichiers ext4
sudo mkdir -p /mnt/backup-black             # le point de montage doit exister
sudo mount /dev/vdb /mnt/backup-black       # monter (temporaire, perdu au reboot)
mount | grep vdb                            # vérifier
```
Pour un montage **persistant**, ajouter une ligne dans `/etc/fstab` (de préférence via l'UUID, pas le nom `/dev/vdX` qui peut changer).

**Mesurer l'occupation — deux outils à ne pas confondre :**
```bash
df -h /point/de/montage    # espace LIBRE/utilisé d'un système de fichiers MONTÉ (disk free)
du -sh /chemin             # taille RÉELLE d'un dossier en parcourant son contenu (disk usage)
```
`df` répond « combien reste-t-il sur ce disque » ; `du` répond « combien pèse ce dossier ».

**Relier un processus à son disque** (étape 3) :
```bash
ps aux --sort=-%mem | head        # processus triés par mémoire décroissante
ls -l /proc/<PID>/exe             # lien vers l'exécutable réel du processus
df /proc/<PID>/exe                # sur quel système de fichiers il se trouve
```
On ne peut **démonter** (`umount`) un disque que si aucun fichier ouvert ne s'y trouve. `lsof /mnt/x` ou `fuser -m /mnt/x` listent ce qui bloque le démontage.

> [!warning] Pièges
> - `umount` échoue avec *target is busy* si un processus a un fichier ouvert dessus (y compris un shell positionné dans le dossier — sortir d'abord avec `cd`).
> - Formater **efface tout** : vérifier le bon `/dev/vdX` avant `mkfs`.
> - Un montage `mount` sans `/etc/fstab` ne survit pas au redémarrage.

## Énoncé

Résolvez cette question sur : `terminal`

Votre équipe vous a choisi pour cette tâche en raison de votre expertise approfondie des systèmes de fichiers et des disques/périphériques. Réalisez les étapes suivantes pour ne pas décevoir votre équipe :
1. Formatez `/dev/vdb` en `ext4`, montez-le sur `/mnt/backup-black` et créez le fichier vide `/mnt/backup-black/completed`.
2. Trouvez lequel des deux disques, `/dev/vdc` ou `/dev/vdd`, a l'occupation de stockage la plus élevée.
    Videz ensuite le dossier `.trash` de celui-ci.
3. Deux processus sont en cours d'exécution : `dark-matter-v1` et `dark-matter-v2`.
    Trouvez celui qui consomme le plus de mémoire ou de mémoire virtuelle.

    Démontez ensuite le disque sur lequel se trouve l'exécutable du processus.

## Solution

Un bon point de départ est probablement de lister les disques existants :
```bash
sudo fdisk -l

```

Disk /dev/vdb: 100 MiB, 104857600 bytes, 204800 sectors

Units: sectors of 1 * 512 = 512 bytes

Sector size (logical/physical): 512 bytes / 512 bytes

I/O size (minimum/optimal): 512 bytes / 512 bytes

Disk /dev/vdc: 100 MiB, 104857600 bytes, 204800 sectors

Units: sectors of 1 * 512 = 512 bytes

Sector size (logical/physical): 512 bytes / 512 bytes

I/O size (minimum/optimal): 512 bytes / 512 bytes

Disk /dev/vdd: 100 MiB, 104857600 bytes, 204800 sectors

Units: sectors of 1 * 512 = 512 bytes

Sector size (logical/physical): 512 bytes / 512 bytes

I/O size (minimum/optimal): 512 bytes / 512 bytes

Disk /dev/vde: 100 MiB, 104857600 bytes, 204800 sectors

Units: sectors of 1 * 512 = 512 bytes

Sector size (logical/physical): 512 bytes / 512 bytes

I/O size (minimum/optimal): 512 bytes / 512 bytes

Disk /dev/vdf: 100 MiB, 104857600 bytes, 204800 sectors

Units: sectors of 1 * 512 = 512 bytes

Sector size (logical/physical): 512 bytes / 512 bytes

I/O size (minimum/optimal): 512 bytes / 512 bytes

Une autre méthode, avec une belle présentation et de bonnes informations :
```bash
lsblk -f
NAME                      FSTYPE      FSVER    LABEL ...  FSAVAIL FSUSE% MOUNTPOINTS
...
vdb
vdc                       ext4        1.0            ...        0    98% /mnt/backup001
vdd                       ext4        1.0            ...    77.7M     6% /mnt/backup002
vde                       ext4        1.0            ...    82.6M     0% /mnt/app-8e127b55
vdf                       ext4        1.0            ...    82.6M     0% /mnt/app-4e9d7e1e
...
```

Ou encore une autre :
```bash
df -h
Filesystem                         Size  Used Avail Use% Mounted on
tmpfs                              198M  1.1M  197M   1% /run
/dev/mapper/ubuntu--vg-ubuntu--lv   62G  5.6G   54G  10% /
tmpfs                              988M     0  988M   0% /dev/shm
tmpfs                              5.0M     0  5.0M   0% /run/lock
/dev/vda2                          2.0G  130M  1.7G   8% /boot
tmpfs                              198M  4.0K  198M   1% /run/user/1000
/dev/vdc                            90M   51M   33M  61% /mnt/backup001
/dev/vdd                            90M  5.1M   78M   7% /mnt/backup002
/dev/vde                            90M   44K   83M   1% /mnt/app-8e127b55
/dev/vdf                            90M   44K   83M   1% /mnt/app-4e9d7e1e
```

### Étape 1
Nous formatons directement le disque :
```bash
sudo mkfs -t ext4 /dev/vdb
mke2fs 1.46.5 (30-Dec-2021)
```

Creating filesystem with 25600 4k blocks and 25600 inodes

Allocating group tables: done

Writing inode tables: done

Creating journal (1024 blocks): done

Writing superblocks and filesystem accounting information: done

Nous le montons ensuite à l'emplacement demandé et créons le fichier :
```bash
sudo mkdir /mnt/backup-black
sudo mount /dev/vdb /mnt/backup-black
sudo touch /mnt/backup-black/completed
df -h
Filesystem                         Size  Used Avail Use% Mounted on
tmpfs                              198M  1.4M  197M   1% /run
/dev/mapper/ubuntu--vg-ubuntu--lv   62G  7.5G   52G  13% /
tmpfs                              988M     0  988M   0% /dev/shm
tmpfs                              5.0M     0  5.0M   0% /run/lock
/dev/vda2                          2.0G  130M  1.7G   8% /boot
tmpfs                              198M  4.0K  198M   1% /run/user/1000
tmpfs                              1.0M     0  1.0M   0% /var/snap/lxd/common/ns
/dev/vdc                            90M   51M   33M  61% /mnt/backup001
/dev/vdd                            90M  5.1M   78M   7% /mnt/backup002
/dev/vde                            90M   44K   83M   1% /mnt/app-8e127b55
/dev/vdf                            90M   44K   83M   1% /mnt/app-4e9d7e1e
/dev/vdb                            90M   24K   83M   1% /mnt/backup-black # this is us
tmpfs                              198M  4.0K  198M   1% /run/user/0
```

### Étape 2
Nous devons maintenant vérifier l'espace disque utilisé sur deux disques :
```bash
df -h
Filesystem                         Size  Used Avail Use% Mounted on
tmpfs                              198M  1.4M  197M   1% /run
/dev/mapper/ubuntu--vg-ubuntu--lv   62G  7.5G   52G  13% /
tmpfs                              988M     0  988M   0% /dev/shm
tmpfs                              5.0M     0  5.0M   0% /run/lock
/dev/vda2                          2.0G  130M  1.7G   8% /boot
tmpfs                              198M  4.0K  198M   1% /run/user/1000
tmpfs                              1.0M     0  1.0M   0% /var/snap/lxd/common/ns
/dev/vdc                            90M   51M   33M  61% /mnt/backup001 # compare
/dev/vdd                            90M  5.1M   78M   7% /mnt/backup002 # compare
/dev/vde                            90M   44K   83M   1% /mnt/app-8e127b55
/dev/vdf                            90M   44K   83M   1% /mnt/app-4e9d7e1e
/dev/vdb                            90M   24K   83M   1% /mnt/backup-black
```

Nous constatons qu'il faut libérer de l'espace disque sur `/mnt/backup001` :
```bash
sudo rm -rf /mnt/backup001/.trash/*
```

Le résultat devrait s'afficher :
```bash
df -h
...
/dev/vdc                            90M   28K   83M   1% /mnt/backup001      # much space gained
/dev/vdd                            90M  5.1M   78M   7% /mnt/backup002
```

### Étape 3
Pour la dernière étape, nous devons vérifier la mémoire de deux processus puis déterminer sur quel disque tourne le plus gros consommateur :
```bash
ps aux | head -n 1
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
ps aux | grep dark-matter
root       51658  0.0  0.1   7380  3584 ?        S    14:57   0:00 /mnt/app-8e127b55/dark-matter-v1
root       51659  0.0  0.1  16596  3456 ?        S    14:57   0:00 /mnt/app-4e9d7e1e/dark-matter-v2
```

Il serait également possible d'utiliser `top -b | grep dark` par exemple.

Nous voyons l'utilisation MEM et VSZ ainsi que les chemins complets tout à la fin. Cela signifie que le processus `dark-matter-v2` est le coupable et que son exécutable se trouve dans `/mnt/app-4e9d7e1e/dark-matter-v2`. Nous devons donc faire :
```bash
df -h | grep /mnt/app-4e9d7e1e
/dev/vdf            90M   44K   83M   1% /mnt/app-4e9d7e1e     # to see the disk and mount point
sudo umount /mnt/app-4e9d7e1e
```

umount: /mnt/app-4e9d7e1e: target is busy.

Le disque est occupé, probablement à cause de ce processus ! Mais nous pouvons vérifier si d'autres processus le bloquent :
```bash
sudo lsof | grep /mnt/app-4e9d7e1e
dark-matt 6204    root  txt       REG             252,80    16488         12 /mnt/app-4e9d7e1e/dark-matter-v2
```

Eh bien, seulement ce mauvais processus ! Nous pouvons donc terminer cette question avec :
```bash
sudo kill 6204 # your PID will be different
sudo umount /mnt/app-4e9d7e1e
```
