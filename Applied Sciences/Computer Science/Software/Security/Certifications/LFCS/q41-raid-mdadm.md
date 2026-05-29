# Question 41 — Software RAID with mdadm

## Énoncé

Solve this question on: `terminal`

1. Build a RAID-1 array `/dev/md0` from `/dev/vdd` and `/dev/vde`.
2. Format it with `xfs` and mount it persistently at `/mnt/raid1`.
3. Simulate a failure of `/dev/vdd`, then replace it with `/dev/vdf`.
4. Write the contents of `/proc/mdstat` into `/opt/course/41/mdstat`.

## Solution

### RAID levels worth knowing

| Level | Min disks | Capacity | Fault tolerance | Notes |
|---|---|---|---|---|
| 0 | 2 | N × disk | none | stripe, fastest, risky |
| 1 | 2 | 1 × disk | N-1 | mirror |
| 5 | 3 | (N-1) × disk | 1 | parity striped |
| 6 | 4 | (N-2) × disk | 2 | double parity |
| 10 | 4 | N/2 × disk | depends | mirror of stripes |

### Install

```bash
sudo apt install mdadm
sudo dnf install mdadm
```

### Step 1 — Create the array

Wipe any old signatures first (otherwise mdadm refuses):
```bash
sudo wipefs -a /dev/vdd /dev/vde
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/vdd /dev/vde
# answer 'y' to the prompt
```

Watch the initial sync:
```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0
```

Save the array definition (so it reassembles after reboot):
```bash
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf       # Debian
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm.conf             # RHEL
sudo update-initramfs -u                                              # Debian
sudo dracut -f                                                        # RHEL
```

### Step 2 — Filesystem and mount

```bash
sudo mkfs.xfs /dev/md0
sudo mkdir -p /mnt/raid1
sudo blkid /dev/md0
# UUID=xxxxx-xxxx ... TYPE="xfs"

echo 'UUID=xxxxx-xxxx  /mnt/raid1  xfs  defaults  0 2' | sudo tee -a /etc/fstab
sudo mount -a
```

### Step 3 — Fail and replace a disk

Mark `/dev/vdd` as failed:
```bash
sudo mdadm --manage /dev/md0 --fail /dev/vdd
sudo mdadm --detail /dev/md0          # state: degraded
```

Remove it from the array:
```bash
sudo mdadm --manage /dev/md0 --remove /dev/vdd
```

Add the replacement disk:
```bash
sudo wipefs -a /dev/vdf
sudo mdadm --manage /dev/md0 --add /dev/vdf
```

Watch the resync:
```bash
watch -n 1 cat /proc/mdstat
sudo mdadm --detail /dev/md0
```

Update the conf if the device list changed:
```bash
sudo sed -i '/^ARRAY \/dev\/md0/d' /etc/mdadm/mdadm.conf
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf
```

### Step 4 — Snapshot of state

```bash
cat /proc/mdstat > /opt/course/41/mdstat
```

### Spare disks and hot spares

Create with a hot spare:
```bash
sudo mdadm --create /dev/md0 --level=5 --raid-devices=3 --spare-devices=1 \
           /dev/vdd /dev/vde /dev/vdf /dev/vdg
```

Convert a member to spare or back:
```bash
sudo mdadm --manage /dev/md0 --add-spare /dev/vdg
```

### Grow an array (add a disk to a RAID 5)

```bash
sudo mdadm --add /dev/md0 /dev/vdh
sudo mdadm --grow /dev/md0 --raid-devices=4
sudo xfs_growfs /mnt/raid1
```

### Stop and reassemble

```bash
sudo umount /mnt/raid1
sudo mdadm --stop /dev/md0
sudo mdadm --assemble /dev/md0 /dev/vd[ef]
sudo mdadm --assemble --scan        # auto-discover from mdadm.conf
```

### Monitor + email alerts

```bash
sudo mdadm --monitor --daemonise --mail root@localhost --delay=300 /dev/md0
# or via systemd unit mdmonitor.service (already shipped)
```

### Check / repair (data scrub)

```bash
echo check  | sudo tee /sys/block/md0/md/sync_action
echo repair | sudo tee /sys/block/md0/md/sync_action
cat /sys/block/md0/md/mismatch_cnt
```
