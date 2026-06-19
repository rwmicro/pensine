# Question 42 — Disk Quotas

## Notes d'apprentissage

Les quotas limitent l'espace disque (et le nombre de fichiers) qu'un utilisateur ou un groupe peut consommer sur un système de fichiers. Ils empêchent qu'un seul utilisateur sature `/home` pour tout le monde.

**Modèle mental : deux dimensions × deux seuils.**

```
                  blocs (espace)        inodes (nombre de fichiers)
soft (souple)   ┌──────────────┐      ┌──────────────┐
                │ dépassable     │      │ dépassable     │  pendant un "grace period"
hard (dur)      │ JAMAIS dépassé │      │ JAMAIS dépassé │
                └──────────────┘      └──────────────┘
```

On limite **deux ressources** (l'espace en *blocs*, et le nombre de fichiers en *inodes*) avec **deux seuils** chacune :
- **soft** : peut être dépassée temporairement, pendant un *délai de grâce* (*grace period*) ; au-delà, blocage.
- **hard** : plafond absolu, jamais franchissable.

Cette structure soft/hard est la même logique que les ulimits de [[q20-user-and-group-limits]] — l'analogie aide à mémoriser.

**Le workflow en trois temps :**
```bash
# 1. activer les quotas sur le FS : option de montage dans /etc/fstab
#    usrquota,grpquota  →  puis remonter (mount -o remount /home)
# 2. initialiser la base de comptage
quotacheck -cugm /home
quotaon /home
# 3. fixer les limites
setquota -u alice 500M 1G 1000 2000 /home   # soft/hard blocs, soft/hard inodes
edquota -u alice                            # édition interactive
```

**Inspecter :**
```bash
quota -u alice          # quotas d'un utilisateur
repquota /home          # rapport complet du système de fichiers
```

**La « technique du prototype »** : copier les quotas d'un utilisateur modèle vers les nouveaux comptes avec `edquota -p modele -u nouveau` — pratique pour appliquer un défaut commun.

**Pièges** :
- Les quotas doivent être **activés à deux endroits** : option de montage dans `/etc/fstab` (`usrquota`/`grpquota`) **et** `quotaon`. Oublier le remontage = quotas inactifs.
- `quotacheck` doit idéalement tourner FS démonté ou en lecture seule pour un comptage exact.
- Sur un FS **XFS**, les quotas se gèrent différemment (`xfs_quota`, options `uquota`/`gquota`) — pas de `quotacheck`.
- Une limite soft sans *grace period* configuré se comporte presque comme une hard.

## Énoncé

Solve this question on: `data-001`

1. Enable user and group quotas on the `/home` filesystem.
2. Set user `alice` a soft limit of `500M` and a hard limit of `1G` for blocks; soft `1000` and hard `2000` files (inodes).
3. Set the same defaults for any new user via the prototype technique.
4. Write the current quota report for `/home` into `/opt/course/42/quota-report`.

## Solution

### Install the tools

```bash
sudo apt install quota         # Debian
sudo dnf install quota         # RHEL
```

### Step 1 — Enable quotas on the filesystem

Edit `/etc/fstab` for the target filesystem:
```
UUID=...  /home  ext4  defaults,usrquota,grpquota  0 2
```

Re-mount or apply:
```bash
sudo mount -o remount /home
mount | grep /home          # confirm options
```

XFS uses **mount options at mount time** instead of `quotacheck`:
- `uquota`, `gquota`, `pquota` — enforce
- `uqnoenforce`, etc. — accounting only

For ext4 (or older filesystems) you must initialise the quota DB:
```bash
sudo quotacheck -cugm /home
# generates /home/aquota.user and /home/aquota.group
sudo quotaon -v /home
sudo quotaoff -v /home          # disable
```

### Step 2 — Set limits for a user

Interactive editor:
```bash
sudo edquota -u alice
```
Block sizes are in **KB**:
```
Filesystem  blocks  soft   hard   inodes  soft  hard
/dev/vda2   3200    512000 1048576 145     1000  2000
```

Or non-interactively with `setquota`:
```bash
sudo setquota -u alice 512000 1048576 1000 2000 /home
# soft-blk  hard-blk  soft-inode  hard-inode
```

For a group:
```bash
sudo setquota -g devs 5G 10G 0 0 /home
```

### Soft vs hard limits + grace period

- **Soft** — can be exceeded temporarily during the grace period.
- **Hard** — cannot be exceeded; writes get `EDQUOT`.
- **Grace** — time the soft limit can stay violated before it becomes hard.

```bash
sudo edquota -t                # edit grace periods
```

### Step 3 — Apply the same defaults to new users

`edquota -p` copies one user's settings to others:
```bash
sudo edquota -p alice -u bob carol dave
# or every user above UID 1000:
sudo edquota -p alice $(awk -F: '$3 >= 1000 {print $1}' /etc/passwd)
```

A common pattern: set up a template user, then in scripts that create accounts call `edquota -p template <newuser>`.

### Step 4 — Reports

```bash
sudo repquota -a > /opt/course/42/quota-report
sudo repquota /home               # one filesystem
sudo repquota -ug /home           # users + groups
quota -u alice                    # what alice is using
quota -g devs
```

### XFS-specific tools

```bash
sudo xfs_quota -x -c 'limit bsoft=500m bhard=1g alice' /home
sudo xfs_quota -x -c 'report -h'  /home
sudo xfs_quota -x -c 'state'      /home
```

XFS adds **project quotas** (per-directory) — enabled via `/etc/projects` and `/etc/projid`:
```bash
echo "10:/data/site1" | sudo tee -a /etc/projects
echo "site1:10"        | sudo tee -a /etc/projid

sudo xfs_quota -x -c 'project -s site1' /data
sudo xfs_quota -x -c 'limit -p bsoft=5g bhard=6g site1' /data
```

### Mailing users automatically when over quota

```bash
sudo warnquota                    # send mail to over-quota users
sudo warnquota -g                 # also groups
# crontab once a day:
echo '0 6 * * * root /usr/sbin/warnquota' | sudo tee /etc/cron.d/warnquota
```

Mail templates: `/etc/warnquota.conf`.

