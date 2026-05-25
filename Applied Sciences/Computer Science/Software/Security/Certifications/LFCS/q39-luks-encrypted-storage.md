# Question 39 — LUKS Encrypted Storage

## Énoncé

Solve this question on: `terminal`

1. Create a LUKS-encrypted volume on `/dev/vdb` with passphrase `lfcs-pass`.
2. Open it as `secure-data`, format it with `ext4` and mount it at `/mnt/secure`.
3. Configure the system to **prompt for the passphrase at boot** and mount the volume automatically.
4. Add a key file at `/root/secure.key` so the volume can also unlock without typing the passphrase.

## Solution

### Step 1 — Create the LUKS container

```bash
sudo cryptsetup luksFormat /dev/vdb
# answer YES, then enter the passphrase twice

sudo cryptsetup luksDump /dev/vdb           # inspect: cipher, key slots
```

LUKS2 is the default on modern distros. To force a version: `--type luks1` / `--type luks2`.

### Step 2 — Open, format and mount

```bash
sudo cryptsetup open /dev/vdb secure-data
# mapped device appears at /dev/mapper/secure-data

sudo mkfs.ext4 -L secure /dev/mapper/secure-data
sudo mkdir -p /mnt/secure
sudo mount /dev/mapper/secure-data /mnt/secure
```

Close cleanly:
```bash
sudo umount /mnt/secure
sudo cryptsetup close secure-data
```

### Step 3 — Persistent unlock at boot (`crypttab`)

Get the UUID of the LUKS container (the **physical** device, not the mapping):
```bash
sudo blkid /dev/vdb
# /dev/vdb: UUID="abcd-..." TYPE="crypto_LUKS"
```

Add to `/etc/crypttab`:
```
# name        source-device                       key-file  options
secure-data   UUID=abcd-...                       none      luks
```

- `none` → prompt at boot
- `/root/secure.key` → unlock from key file (see step 4)
- options: `luks`, `discard` (TRIM on SSD), `tries=3`, `timeout=30`

Add the **mapper** device to `/etc/fstab`:
```
/dev/mapper/secure-data  /mnt/secure  ext4  defaults,noatime  0 2
```

Apply now and verify:
```bash
sudo systemctl daemon-reload
sudo systemctl restart cryptsetup.target          # may need reboot to fully test
sudo cryptdisks_start secure-data                 # Debian helper
mount /mnt/secure
```

### Step 4 — Unlock via key file

Generate a strong random key:
```bash
sudo dd if=/dev/urandom of=/root/secure.key bs=1 count=4096
sudo chmod 600 /root/secure.key

sudo cryptsetup luksAddKey /dev/vdb /root/secure.key
sudo cryptsetup luksDump /dev/vdb | grep -i "key slot"
```

Update `/etc/crypttab`:
```
secure-data  UUID=abcd-...  /root/secure.key  luks
```

Remove a key slot later:
```bash
sudo cryptsetup luksRemoveKey /dev/vdb          # prompts for the passphrase to remove
sudo cryptsetup luksKillSlot /dev/vdb 1
```

### Backup the LUKS header (critical!)

If the header is corrupted, the data is lost forever:
```bash
sudo cryptsetup luksHeaderBackup /dev/vdb --header-backup-file /root/vdb.luks-header
sudo cryptsetup luksHeaderRestore /dev/vdb --header-backup-file /root/vdb.luks-header
```

Store the backup off-machine.

### Resize a LUKS volume on LVM

Order matters when shrinking — always: filesystem → LUKS → LV. When growing: LV → LUKS → filesystem.
```bash
# growing
sudo lvextend -L +5G vgdata/lvsecure
sudo cryptsetup resize secure-data
sudo resize2fs /dev/mapper/secure-data
```

### Verify which key slot was used

```bash
sudo cryptsetup --debug open /dev/vdb test 2>&1 | grep slot
```

---

[← Question 38](q38-kvm-virtualization.md) · [Index](Certifications/LFCS/notes.md) · [Question 40 →](q40-swap-configuration.md)
