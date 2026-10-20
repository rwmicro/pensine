---
title: "LFCS Q18 — Stockage LVM"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, storage]
date: "2026-08-09"
---

# Question 18 — Stockage LVM

## Notes d'apprentissage

LVM (*Logical Volume Manager*) ajoute une couche d'abstraction entre les disques physiques et les systèmes de fichiers. Au lieu de partitions rigides, on obtient des volumes redimensionnables à chaud, répartis sur plusieurs disques.

> [!tip] Modèle mental : les trois étages de LVM
> ```
> disques physiques        PV          VG              LV
> /dev/vdg, /dev/vdh  ──► Physical ──► Volume    ──►  Logical
>                         Volumes      Group           Volumes
>                         (pvcreate)   (vgcreate :     (lvcreate :
>                                       un "pool"        des "tranches"
>                                       d'espace)        formatables)
> ```

1. **PV** (Physical Volume) : un disque/partition initialisé pour LVM (`pvcreate`).
2. **VG** (Volume Group) : un réservoir d'espace agrégeant un ou plusieurs PV (`vgcreate`).
3. **LV** (Logical Volume) : une « partition » virtuelle taillée dans le VG, qu'on formate et monte (`lvcreate`).

L'intérêt : un LV peut grandir tant que le VG a de l'espace libre, sans dépendre des frontières physiques d'un disque.

**La règle des préfixes** — les commandes suivent les initiales :
```
pv* → Physical Volume   vg* → Volume Group   lv* → Logical Volume
   pvs / pvdisplay         vgs / vgdisplay       lvs / lvdisplay   (afficher)
   pvcreate                vgcreate              lvcreate          (créer)
   pvremove                vgreduce/vgextend     lvremove/lvextend (modifier)
```

**Opérations de cet exercice :**
```bash
pvs ; vgs ; lvs                       # état actuel des trois niveaux
vgreduce vol1 /dev/vdh                 # retirer un disque d'un VG
pvremove /dev/vdh                      # (si on retire le PV de LVM)
vgcreate vol2 /dev/vdh                 # nouveau VG sur ce disque
lvcreate -L 50M -n p1 vol2             # LV de 50M nommé p1 dans vol2
mkfs.ext4 /dev/vol2/p1                 # formater le LV
```
Un LV est accessible via `/dev/<VG>/<LV>` (ici `/dev/vol2/p1`).

**Agrandir un volume** (cas fréquent en prod) se fait en deux temps : étendre le LV **puis** le système de fichiers.
```bash
lvextend -L +1G /dev/vol2/p1
resize2fs /dev/vol2/p1        # ext4 ; xfs_growfs pour XFS
```

> [!warning] Pièges
> - Avant `vgreduce`, le disque ne doit plus contenir de données actives (déplacer avec `pvmove` si nécessaire).
> - Agrandir le LV ne suffit pas : sans `resize2fs`/`xfs_growfs`, le système de fichiers ignore l'espace ajouté.
> - `-L 50M` = taille absolue ; `-L +50M` = ajout relatif. Confondre les deux est classique.
> - XFS ne peut **que grandir**, pas rétrécir — choix de système de fichiers à anticiper.

## Énoncé

Résolvez cette question sur : `terminal`

Vous devez effectuer des modifications sur des volumes LVM :
1. Réduisez le groupe de volumes `vol1` en en retirant le disque `/dev/vdh`
2. Créez un nouveau groupe de volumes nommé `vol2` qui utilise le disque `/dev/vdh`
3. Créez un volume logique de `50M` nommé `p1` pour le groupe de volumes `vol2`
4. Formatez ce nouveau volume logique en `ext4`

## Solution

Quelques abréviations utiles pour travailler avec LVM, car les noms de commandes commencent généralement par celles-ci :

PV = Physical Volume

VG = Volume Group

LV = Logical Volume

Commencez par jeter un œil aux PV :
```bash
sudo pvs
  PV         VG        Fmt  Attr PSize    PFree
  /dev/vda3  ubuntu-vg lvm2 a--  <126.00g 63.00g
  /dev/vdg   vol1      lvm2 a--    96.00m 84.00m
  /dev/vdh   vol1      lvm2 a--    96.00m 96.00m
```

Dans la sortie ci-dessus, nous voyons que le VG `vol1` utilise deux disques, `/dev/vdg` et `/dev/vdh`. Nous pouvons aussi obtenir une vue d'ensemble de tous les disques système et de leur usage LVM :
```bash
sudo lvmdiskscan
  /dev/loop0 [     <49.84 MiB]
  /dev/loop1 [      63.28 MiB]
  /dev/loop2 [    <111.95 MiB]
  /dev/vda2  [       2.00 GiB]
  /dev/loop3 [     <53.26 MiB]
  /dev/vda3  [    <126.00 GiB] LVM physical volume
  /dev/loop4 [      63.45 MiB]
  /dev/vdb   [     100.00 MiB]
  /dev/vdc   [     100.00 MiB]
  /dev/vdd   [     100.00 MiB]
  /dev/vde   [     100.00 MiB]
  /dev/vdf   [     100.00 MiB]
  /dev/vdg   [     100.00 MiB] LVM physical volume # disk 1
  /dev/vdh   [     100.00 MiB] LVM physical volume # disk 2
  5 disks
  6 partitions
  2 LVM physical volume whole disks
  1 LVM physical volume
```

Le PV existant `/dev/vda3` avec le VG `ubuntu-vg` est créé par le système d'exploitation principal et ne doit pas être touché.

### Étape 1
Nous voulons retirer le disque `/dev/vdh` du VG existant `vol1` :
```bash
sudo vgs # list all VGs
  VG         PV  LV  SN Attr   VSize    VFree
  ubuntu-vg   1   1   0 wz--n- <126.00g  63.00g
  vol1        2   1   0 wz--n-  192.00m 180.00m # two PVs
sudo vgreduce vol1 /dev/vdh
  Removed "/dev/vdh" from volume group "vol1"
sudo vgs
  VG         PV  LV  SN Attr   VSize    VFree
  ubuntu-vg   1   1   0 wz--n- <126.00g 63.00g
  vol1        1   1   0 wz--n-   96.00m 84.00m  # one PV
```

Cela devrait suffire. Nous pouvons aussi le vérifier en listant tous les PV :
```bash
sudo pvs
  PV         VG        Fmt  Attr PSize    PFree
  /dev/vda3  ubuntu-vg lvm2 a--  <126.00g  63.00g
  /dev/vdg   vol1      lvm2 a--    96.00m  84.00m
  /dev/vdh             lvm2 ---   100.00m 100.00m # not assigned to a VG any longer
```

### Étape 2
Nous allons maintenant créer un nouveau `PV` à partir de ce disque désormais libre :
```bash
sudo vgcreate vol2 /dev/vdh
  Volume group "vol2" successfully created
sudo pvs
  PV         VG        Fmt  Attr PSize    PFree
  /dev/vda3  ubuntu-vg lvm2 a--  <126.00g 63.00g
  /dev/vdg   vol1      lvm2 a--    96.00m 84.00m
  /dev/vdh   vol2      lvm2 a--    96.00m 96.00m # assigned to the VG
```

### Étape 3
Nous continuons en créant un LV pour notre nouveau VG :
```bash
sudo lvs # no LV yet for vol2
  LV        VG        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  ubuntu-lv ubuntu-vg -wi-ao---- <63.00g
  p1        vol1      -wi-a-----  12.00m
sudo lvcreate --size 50M --name p1 vol2
  Rounding up size to full physical extent 52.00 MiB
  Logical volume "p1" created.
sudo lvs
  LV        VG        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  ubuntu-lv ubuntu-vg -wi-ao---- <63.00g
  p1        vol1      -wi-a-----  12.00m
  p1        vol2      -wi-a-----  52.00m  # there we go
```

### Étape 4
Nous pouvons accéder aux partitions LVM ou aux LV de la manière habituelle une fois le chemin connu :
```bash
sudo mkfs -t ext4 /dev/vol2/p1
mke2fs 1.46.5 (30-Dec-2021)
```

Creating filesystem with 13312 4k blocks and 13312 inodes

Allocating group tables: done

Writing inode tables: done

Creating journal (1024 blocks): done

Writing superblocks and filesystem accounting information: done

Nous pourrions maintenant monter et utiliser `/dev/vol2/p1` comme à notre habitude.

**Agrandir un LV**

Également intéressant et pouvant aussi faire partie de l'examen : agrandir un LV monté :
```bash
sudo mkdir /mnt/vol2_p1
sudo mount /dev/vol2/p1 /mnt/vol2_p1
sudo fdisk -l
...
```

Disk /dev/mapper/vol2-p1: 52 MiB, 54525952 bytes, 106496 sectors # ~50M

Units: sectors of 1 * 512 = 512 bytes

Sector size (logical/physical): 512 bytes / 512 bytes

I/O size (minimum/optimal): 512 bytes / 512 bytes
```bash
sudo lvs
  LV        VG        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  ubuntu-lv ubuntu-vg -wi-ao---- <63.00g
  p1        vol1      -wi-a-----  12.00m
  p1        vol2      -wi-ao----  52.00m
sudo lvresize vol2/p1 --size 70M # raise to 70M
```

  Rounding size to boundary between physical extents: 72.00 MiB.

  Size of logical volume vol2/p1 changed from 52.00 MiB (13 extents) to 72.00 MiB (18 extents).

  Logical volume vol2/p1 successfully resized.
```bash
sudo fdisk -l
...
```

Disk /dev/mapper/vol2-p1: 72 MiB, 75497472 bytes, 147456 sectors # ~70M

Units: sectors of 1 * 512 = 512 bytes

Sector size (logical/physical): 512 bytes / 512 bytes

I/O size (minimum/optimal): 512 bytes / 512 bytes

