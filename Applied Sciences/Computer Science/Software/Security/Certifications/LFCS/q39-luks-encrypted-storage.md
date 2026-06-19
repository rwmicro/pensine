# Question 39 — LUKS Encrypted Storage

## Notes d'apprentissage

LUKS chiffre un disque au niveau bloc : sans la passphrase (ou une clé), les données sont illisibles, même en retirant physiquement le disque. C'est le chiffrement « at rest » standard sous Linux, géré par `cryptsetup`.

**Modèle mental : une couche de déchiffrement entre le disque et le système de fichiers.**

```
/dev/vdb (chiffré, LUKS)
    │  cryptsetup luksOpen + passphrase
    ▼
/dev/mapper/secure-data (vue déchiffrée, "en clair")
    │  mkfs.ext4 / mount
    ▼
/mnt/secure (fichiers utilisables)
```

Point fondamental : on **ne formate ni ne monte jamais le périphérique chiffré directement**. On l'ouvre d'abord (`luksOpen`), ce qui crée un périphérique virtuel `/dev/mapper/<nom>` ; c'est *celui-là* qu'on formate et monte.

**Le workflow complet :**
```bash
cryptsetup luksFormat /dev/vdb            # créer le conteneur (DÉTRUIT les données)
cryptsetup luksOpen /dev/vdb secure-data  # ouvrir → /dev/mapper/secure-data
mkfs.ext4 /dev/mapper/secure-data         # formater la vue déchiffrée
mount /dev/mapper/secure-data /mnt/secure
cryptsetup luksClose secure-data          # refermer
```

**Déverrouillage au boot : `/etc/crypttab` + `/etc/fstab`** — la combinaison à comprendre.

```
/etc/crypttab :  secure-data  UUID=...  none        luks   ← quoi déverrouiller, avec quoi
/etc/fstab    :  /dev/mapper/secure-data  /mnt/secure  ext4  ← quoi monter, une fois ouvert
```
`crypttab` est consulté **avant** `fstab` : il déverrouille (demande la passphrase, ou lit un *key file*), puis `fstab` monte le `/dev/mapper/...` résultant. Mettre `none` comme source de clé = demander la passphrase au boot ; indiquer un fichier (`/root/secure.key`) = déverrouillage automatique.

**Plusieurs clés (key slots).** LUKS gère jusqu'à 8 emplacements de clés : on peut ajouter un fichier-clé *en plus* de la passphrase, pour automatiser sans perdre l'accès manuel.
```bash
cryptsetup luksAddKey /dev/vdb /root/secure.key
```

**Pièges** :
- `luksFormat` **écrase** tout : aucune récupération possible sans sauvegarde de l'en-tête (`luksHeaderBackup`).
- Confondre `/dev/vdb` (chiffré) et `/dev/mapper/...` (clair) : `fstab` doit pointer le mapper, pas le disque brut.
- Un fichier-clé en `none`/passphrase oublié = données perdues — d'où l'intérêt d'un second key slot.
- Référencer le disque par **UUID** dans `crypttab` (le nom `/dev/vdX` peut changer).

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

