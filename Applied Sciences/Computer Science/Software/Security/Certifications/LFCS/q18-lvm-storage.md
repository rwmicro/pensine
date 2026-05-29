# Question 18 — LVM Storage

## Énoncé

Solve this question on: `terminal`

You're required to perform changes on LVM volumes:
1. Reduce the volume group `vol1` by removing disk `/dev/vdh` from it
2. Create a new volume group named `vol2` which uses disk `/dev/vdh`
3. Create a `50M` logical volume named `p1` for volume group `vol2`
4. Format that new logical volume with `ext4`

## Solution

Some helpful abbreviations when working with LVM, because command names usually start with those:

PV = Physical Volume

VG = Volume Group

LV = Logical Volume

Start by having a look at PVs:
```bash
sudo pvs
  PV         VG        Fmt  Attr PSize    PFree
  /dev/vda3  ubuntu-vg lvm2 a--  <126.00g 63.00g
  /dev/vdg   vol1      lvm2 a--    96.00m 84.00m
  /dev/vdh   vol1      lvm2 a--    96.00m 96.00m
```

In the output above we can see that the VG `vol1` uses two disks `/dev/vdg` and `/dev/vdh`. We can also get an overview over all system disks and their LVM usage:
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

The existing PV `/dev/vda3` with VG `ubuntu-vg` is created by the main operating system and shouldn't be touched.

### Step 1
We want to remove disk `/dev/vdh` from the existing VG `vol1`:
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

That should do it. We can also verify this by listing all PVs:
```bash
sudo pvs
  PV         VG        Fmt  Attr PSize    PFree
  /dev/vda3  ubuntu-vg lvm2 a--  <126.00g  63.00g
  /dev/vdg   vol1      lvm2 a--    96.00m  84.00m
  /dev/vdh             lvm2 ---   100.00m 100.00m # not assigned to a VG any longer
```

### Step 2
Now we're going to create a new `PV` using that now free disk:
```bash
sudo vgcreate vol2 /dev/vdh
  Volume group "vol2" successfully created
sudo pvs
  PV         VG        Fmt  Attr PSize    PFree
  /dev/vda3  ubuntu-vg lvm2 a--  <126.00g 63.00g
  /dev/vdg   vol1      lvm2 a--    96.00m 84.00m
  /dev/vdh   vol2      lvm2 a--    96.00m 96.00m # assigned to the VG
```

### Step 3
We continue by creating a LV for our new VG:
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

### Step 4
We can access LVM partitions or LVs in the usual way once we know the path:
```bash
sudo mkfs -t ext4 /dev/vol2/p1
mke2fs 1.46.5 (30-Dec-2021)
```

Creating filesystem with 13312 4k blocks and 13312 inodes

Allocating group tables: done

Writing inode tables: done

Creating journal (1024 blocks): done

Writing superblocks and filesystem accounting information: done

We could now go ahead and mount and use `/dev/vol2/p1` as we're used to.

**Extending a LV**

Also interesting and could also be part of the exam is extending a mounted LV:
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

