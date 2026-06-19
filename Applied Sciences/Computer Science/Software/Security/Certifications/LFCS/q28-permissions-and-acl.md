# Question 28 — Permissions, SUID/SGID and ACL

## Notes d'apprentissage

Le modèle de permissions Unix repose sur **trois classes × trois droits**, plus des bits spéciaux, et peut être affiné par les ACL. C'est le mécanisme central de sécurité du système de fichiers.

**Modèle mental : qui × quoi.**

```
-rwxr-x---
│└┬┘└┬┘└┬┘
│ │  │  └ others (autres)        : ---
│ │  └ group (groupe)            : r-x
│ └ user (propriétaire)          : rwx
└ type (- fichier, d dossier, l lien)

valeurs : r=4  w=2  x=1   →   rwx=7  rw-=6  r-x=5  r--=4
```

**Les bits spéciaux (le chiffre de tête)** — souvent oubliés, ils sont décisifs :

| Bit | Valeur | Sur un fichier | Sur un dossier |
|---|---|---|---|
| SUID | 4 | s'exécute avec les droits du **propriétaire** | — |
| SGID | 2 | s'exécute avec les droits du **groupe** | nouveaux fichiers **héritent du groupe** |
| Sticky | 1 | — | seul le propriétaire peut supprimer (ex. `/tmp`) |

Le **SGID sur un dossier** est la clé de l'exercice « les nouveaux fichiers héritent du groupe `dev` » : `chmod 2770`. Sans lui, un fichier prend le groupe principal de son créateur.

**Quand le modèle classique ne suffit pas : les ACL.** Le modèle propriétaire/groupe/autres ne permet qu'**un** propriétaire et **un** groupe. Pour donner un droit à un utilisateur supplémentaire précis (« alice peut lire ce fichier »), on utilise les ACL POSIX :
```bash
setfacl -m u:alice:rw fichier      # ajouter un droit pour alice
getfacl fichier                    # voir les ACL
setfacl -d -m u:alice:rwx dossier  # ACL par défaut (héritée par les nouveaux fichiers)
```
Un `+` à la fin du mode dans `ls -l` (`-rw-rw----+`) signale la présence d'ACL.

**Le piège SUID/sécurité.** Un binaire SUID root mal choisi = élévation de privilèges. `find / -perm -4000 -type f` liste les SUID — réflexe d'audit aussi bien offensif que défensif.

**`umask`** définit les bits *retirés* des permissions par défaut (666 fichiers / 777 dossiers). `umask 027` → fichiers 640, dossiers 750.

**Pièges** :
- `-perm 644` (exact) ≠ `-perm -644` (au moins ces bits) ≠ `-perm /644` (au moins un) — voir [[q09-find-files-with-properties-and-perform-actions]].
- `chmod -R g+rwX` : le **X majuscule** ne met le bit exécutable que sur les dossiers et fichiers déjà exécutables — évite de rendre tous les fichiers exécutables.
- Les ACL exigent un système de fichiers monté avec l'option `acl` (par défaut sur ext4/xfs modernes).
- Le « mask » ACL plafonne les droits effectifs des utilisateurs/groupes nommés — un droit ACL peut être bridé par le mask.

## Énoncé

Solve this question on: `data-001`

1. On directory `/srv/shared`, set group ownership to `dev` and ensure new files inherit that group.
2. Make `/srv/shared` writable by `dev`, with files unreadable by `others`.
3. Grant user `alice` read+write access to `/srv/shared/report.txt` via ACL.
4. Find all files with the SUID bit set under `/usr/bin` and write them into `/opt/course/28/suid`.

## Solution

### Step 1 — Group ownership and SGID

```bash
sudo chgrp dev /srv/shared
sudo chmod 2770 /srv/shared          # leading 2 = setgid on directory
ls -ld /srv/shared
# drwxrws--- 2 root dev ... /srv/shared
```

With SGID on a directory, every new file or subdir inside inherits the `dev` group — without it, files take the creator's primary group.

### Step 2 — Numeric and symbolic modes

Permission digits:

| Digit | r | w | x |
|---|---|---|---|
| 7 | 1 | 1 | 1 |
| 6 | 1 | 1 | 0 |
| 5 | 1 | 0 | 1 |
| 4 | 1 | 0 | 0 |

Special bits (leading digit):

| Bit | Value | Effect on file | Effect on directory |
|---|---|---|---|
| SUID | 4 | run as owner | — |
| SGID | 2 | run as group | new entries inherit group |
| Sticky | 1 | — | only owner can delete (e.g. `/tmp`) |

```bash
chmod 770 file                       # rwxrwx---
chmod u+x,g-w,o= file                # symbolic
chmod -R g+rwX /srv/shared           # capital X = exec only on dirs / already-exec files
chmod u+s /usr/local/bin/tool        # set SUID
chmod g+s /srv/shared                # set SGID on dir
chmod +t /srv/incoming               # sticky
```

### Step 3 — POSIX ACLs

Required: filesystem mounted with `acl` (default on most modern distros).

```bash
getfacl /srv/shared/report.txt
sudo setfacl -m u:alice:rw /srv/shared/report.txt        # add user ACL
sudo setfacl -m g:audit:r /srv/shared/report.txt         # add group ACL
sudo setfacl -x u:alice /srv/shared/report.txt           # remove ACL entry
sudo setfacl -b /srv/shared/report.txt                   # strip all ACLs
```

Default ACLs on directories (inherited by new entries):
```bash
sudo setfacl -d -m u:alice:rwx /srv/shared
```

A `+` after the mode in `ls -l` indicates extra ACL entries:
```
-rw-rw----+ 1 root dev 0 May 24 19:00 report.txt
```

The "mask" sets the maximum effective permission for named users/groups:
```bash
sudo setfacl -m m:rx /srv/shared/report.txt
```

### Step 4 — Find files by permission bits

```bash
sudo find /usr/bin -perm -4000 -type f > /opt/course/28/suid
sudo find / -perm -2000 -type f         # SGID
sudo find /tmp -perm -1000 -type d      # sticky directories
sudo find / -perm 777 -type f           # world rwx (exact)
```

`-perm` semantics:
- `-perm 644` — **exactly** 644
- `-perm -644` — at least these bits set
- `-perm /644` — any of these bits set

### umask

Defines bits **removed** from default 666 (files) / 777 (dirs):
```bash
umask                                   # show current
umask 027                               # files 640, dirs 750
```

Persistent in `/etc/profile`, `/etc/login.defs` (UMASK), or `~/.bashrc`.

### Ownership

```bash
sudo chown alice:dev file
sudo chown -R alice /srv/alice          # recursive
sudo chown --reference=template.txt file
```
