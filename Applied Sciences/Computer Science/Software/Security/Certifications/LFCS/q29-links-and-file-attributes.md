# Question 29 — Links and File Attributes

## Notes d'apprentissage

Pour comprendre les liens, il faut d'abord comprendre l'**inode** : la structure qui contient les métadonnées d'un fichier (permissions, propriétaire, taille, pointeurs vers les blocs de données). Le nom du fichier n'est qu'une **étiquette** dans un répertoire qui pointe vers un inode.

**Modèle mental : nom → inode → données.**

```
répertoire           inode (n°1234)          blocs de données
"passwd"  ─────────► [ métadonnées +  ─────► [ contenu réel ]
"hard-passwd" ─────►   nb de liens ]
                       (2 noms → même inode)
```

**Lien dur (hard link) vs lien symbolique (symlink)** — la distinction fondamentale :

| | Lien dur | Lien symbolique |
|---|---|---|
| Pointe vers | le **même inode** | un **chemin** (texte) |
| `ln` | `ln cible nom` | `ln -s cible nom` |
| Traverse les systèmes de fichiers | non | oui |
| Peut viser un dossier | non | oui |
| Survit si l'original est supprimé | oui (les données restent tant qu'un lien existe) | non (devient cassé) |

Un lien dur est un **second nom** pour les mêmes données : supprimer l'original ne détruit rien tant qu'il reste un lien (le compteur de liens de l'inode). Un symlink n'est qu'un panneau indicateur : si la cible disparaît, il pointe dans le vide.

**Les attributs étendus avec `chattr`** vont au-delà des permissions : ils modifient le comportement du système de fichiers lui-même.
```bash
chattr +i fichier      # immuable : même root ne peut PAS modifier/supprimer/renommer
chattr -i fichier      # retirer
lsattr fichier         # afficher les attributs
```
L'attribut `i` (immuable) protège un fichier critique (`/etc/resolv.conf` régénéré sans cesse) : il faut explicitement retirer `+i` avant toute modification, même en root. `a` (append-only) est utile pour des logs inviolables.

**Pièges** :
- `+i` bloque **tout**, y compris root — d'où l'intérêt (et le piège : « pourquoi je ne peux pas éditer ce fichier ? » → `lsattr`).
- Un lien dur ne peut pas franchir une frontière de système de fichiers (inodes propres à chaque FS) ni viser un dossier.
- `ls -l` affiche un symlink cassé en rouge ; `readlink -f` résout le chemin réel.
- Inode ≠ contenu : copier un fichier crée un **nouvel** inode ; le déplacer dans le même FS le conserve.

## Énoncé

Solve this question on: `terminal`

1. Create a hard link `/opt/course/29/hard-passwd` pointing to `/etc/passwd`.
2. Create a symbolic link `/opt/course/29/soft-passwd` pointing to `/etc/passwd`.
3. Make `/etc/resolv.conf` immutable so even root cannot edit it without removing the attribute.
4. Write the inode number of `/etc/hostname` into `/opt/course/29/inode`.

## Solution

### Step 1 — Hard link

```bash
sudo ln /etc/passwd /opt/course/29/hard-passwd
ls -li /etc/passwd /opt/course/29/hard-passwd
# both entries share the same inode and link count goes up
```

Hard link properties:
- Points to the **same inode** as the original.
- Cannot cross filesystems.
- Cannot point to a directory (kernel protection).
- The file is only deleted when **all** hard links are removed.

### Step 2 — Symbolic link

```bash
ln -s /etc/passwd /opt/course/29/soft-passwd
ls -l /opt/course/29/soft-passwd
# lrwxrwxrwx ... soft-passwd -> /etc/passwd
```

Symbolic link properties:
- Stores a **path** (not an inode reference).
- Can cross filesystems and link directories.
- Broken if the target moves or is deleted (`ls -l` shows red).

Useful flags:
- `ln -sf target name` — force replace existing link
- `ln -sr target name` — make the symlink relative
- `readlink -f link` — resolve to absolute path
- `stat file` — show inode, links, size, timestamps

### Step 3 — File attributes with chattr

```bash
sudo chattr +i /etc/resolv.conf       # immutable
lsattr /etc/resolv.conf
# ----i---------e----- /etc/resolv.conf
sudo chattr -i /etc/resolv.conf       # remove
```

Common attributes:

| Attr | Meaning |
|---|---|
| `i` | immutable — no edit, rename, delete, link |
| `a` | append-only — only appends, no rewrite/delete |
| `A` | no atime updates |
| `c` | compressed (filesystem dependent) |
| `d` | excluded from `dump` |
| `e` | extent format (informational, ext4) |
| `j` | data journaling |
| `s` | secure deletion (zeroed on delete) |
| `S` | synchronous writes |
| `u` | undeletable — content kept after `rm` |

### Step 4 — Inode number

```bash
stat -c %i /etc/hostname > /opt/course/29/inode
# or:
ls -i /etc/hostname | awk '{print $1}' > /opt/course/29/inode
```

### Extended attributes (xattr)

Separate from `chattr`; used by SELinux, ACLs, custom metadata:
```bash
getfattr -d -m '.*' file              # show all
setfattr -n user.note -v "hello" file
setfattr -x user.note file
```

