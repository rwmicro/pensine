# Question 8 — Disk Management

## Énoncé

Solve this question on: `terminal`

Your team selected you for this task because of your deep filesystem and disk/devices expertise. Solve the following steps to not let your team down:
1. Format `/dev/vdb` with `ext4`, mount it to `/mnt/backup-black` and create empty file `/mnt/backup-black/completed`.
2. Find which of the two disks, `/dev/vdc` or `/dev/vdd`, has higher storage usage.
    Then empty the `.trash` folder on it.
3. There are two processes running: `dark-matter-v1` and `dark-matter-v2`.
    Find the one that consumes more memory or virtual memory.

    Then unmount the disk where the process executable is located on.

## Solution

A good way to start is probably to list existing disks:
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

Another way with good list style and information:
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

Or even another way:
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

### Step 1
We go right ahead and format the disk:
```bash
sudo mkfs -t ext4 /dev/vdb
mke2fs 1.46.5 (30-Dec-2021)
```

Creating filesystem with 25600 4k blocks and 25600 inodes

Allocating group tables: done

Writing inode tables: done

Creating journal (1024 blocks): done

Writing superblocks and filesystem accounting information: done

Then we mount it at the required location and create the file:
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

### Step 2
Now we need to check the used disk space of two disks:
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

We see that we need to clear up disk space on `/mnt/backup001`:
```bash
sudo rm -rf /mnt/backup001/.trash/*
```

The results should be shown:
```bash
df -h
...
/dev/vdc                            90M   28K   83M   1% /mnt/backup001      # much space gained
/dev/vdd                            90M  5.1M   78M   7% /mnt/backup002
```

### Step 3
For the final step we need to check the memory of two processes and then find out on which disk the largest consumer runs:
```bash
ps aux | head -n 1
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
ps aux | grep dark-matter
root       51658  0.0  0.1   7380  3584 ?        S    14:57   0:00 /mnt/app-8e127b55/dark-matter-v1
root       51659  0.0  0.1  16596  3456 ?        S    14:57   0:00 /mnt/app-4e9d7e1e/dark-matter-v2
```

It would also be possible to use `top -b | grep dark` for example.

We see the MEM and VSZ usage and the full paths at the very end. This means process `dark-matter-v2` is the offender and the executable is to be found at `/mnt/app-4e9d7e1e/dark-matter-v2`. So we need to do:
```bash
df -h | grep /mnt/app-4e9d7e1e
/dev/vdf            90M   44K   83M   1% /mnt/app-4e9d7e1e     # to see the disk and mount point
sudo umount /mnt/app-4e9d7e1e
```

umount: /mnt/app-4e9d7e1e: target is busy.

The disk is busy, probably because of that one process! But we can check for any other processes blocking this:
```bash
sudo lsof | grep /mnt/app-4e9d7e1e
dark-matt 6204    root  txt       REG             252,80    16488         12 /mnt/app-4e9d7e1e/dark-matter-v2
```

Well, only that one bad process! Hence we can finish this question with:
```bash
sudo kill 6204 # your PID will be different
sudo umount /mnt/app-4e9d7e1e
```
