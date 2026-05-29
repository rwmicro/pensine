# Question 40 — Swap Configuration

## Énoncé

Solve this question on: `data-002`

1. Add a `1G` swap **file** at `/swapfile`, persistent across reboots.
2. Add a swap **partition** on `/dev/vdc1` with `priority=10`, also persistent.
3. Set `vm.swappiness` to `20`.
4. Write the total amount of swap (in MB) into `/opt/course/40/swap-mb`.

## Solution

### Step 1 — Swap file

```bash
sudo fallocate -l 1G /swapfile          # fast, sparse-ish
# or, more portable:
sudo dd if=/dev/zero of=/swapfile bs=1M count=1024 status=progress

sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
swapon --show
```

Persist in `/etc/fstab`:
```
/swapfile  none  swap  sw  0 0
```

### Step 2 — Swap partition

Create the partition (use `fdisk`, `parted`, or `cfdisk`; type `82` = Linux swap on MBR, `19` in `parted`):
```bash
sudo fdisk /dev/vdc        # n -> partition, t -> type 82, w -> write
sudo partprobe /dev/vdc
```

Format + activate with a priority:
```bash
sudo mkswap -L bigswap /dev/vdc1
sudo swapon --priority 10 /dev/vdc1
swapon --show
# NAME       TYPE      SIZE USED PRIO
# /dev/vdc1  partition   2G   0B   10
# /swapfile  file        1G   0B   -2
```

Higher priority is used first. With equal priorities, swap is striped (parallel).

Persist (use UUID for stability):
```bash
sudo blkid /dev/vdc1
echo 'UUID=...  none  swap  sw,pri=10  0 0' | sudo tee -a /etc/fstab
```

### Step 3 — Swappiness

```bash
sudo sysctl -w vm.swappiness=20

# persistent: see [[q25-sysctl-kernel-parameters]]
echo "vm.swappiness = 20" | sudo tee /etc/sysctl.d/99-swap.conf
sudo sysctl --system
```

- `0` → swap only to avoid OOM
- `60` → distro default on many systems
- `100` → swap as eagerly as possible

Companion: `vm.vfs_cache_pressure` (default 100) controls reclaim of inode/dentry cache.

### Step 4 — Total swap in MB

```bash
free -m | awk '/Swap:/ {print $2}' > /opt/course/40/swap-mb
# alternative:
awk '/SwapTotal/ {print $2/1024}' /proc/meminfo
```

### Day-to-day commands

```bash
swapon --show                          # active swaps
free -h                                # mem + swap
cat /proc/swaps
sudo swapoff /swapfile                 # deactivate
sudo swapoff -a                        # all
sudo swapon -a                         # everything in fstab
```

### Memory pressure observation

```bash
vmstat 1                               # si / so columns = swap in/out per sec
sar -W 1                               # paging stats
top                                    # press 'M' to sort by mem
```

### zram (RAM-compressed swap) — alternative

Useful on RAM-constrained systems:
```bash
sudo apt install zram-tools
sudo systemctl enable --now zramswap
zramctl
```

### Sizing rule of thumb

Modern Linux Foundation guidance (LFCS-ish):
- ≤ 2 GB RAM → swap = 2× RAM
- 2–8 GB RAM → swap = RAM
- 8–64 GB RAM → swap = RAM / 2 (min 4 GB)
- 64 GB RAM → 4 GB swap suffices

If hibernation is required, swap must be **at least** RAM size.
