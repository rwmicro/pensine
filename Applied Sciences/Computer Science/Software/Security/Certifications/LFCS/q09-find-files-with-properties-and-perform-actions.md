# Question 9 — Find files with properties and perform actions

## Notes d'apprentissage

`find` est l'un des outils les plus puissants d'Unix : il parcourt une arborescence, **filtre** par critères, puis **agit** sur chaque résultat. Le maîtriser fait gagner un temps énorme à l'examen comme en production.

**Modèle mental : `find [où] [critères] [action]`.**

```bash
find /var/backup  -type f -size +10k  -exec mv {} ./large \;
     └─ où ────┘  └──── critères ───┘ └──── action ─────┘
```

Les critères s'enchaînent par un **ET implicite** : un fichier doit satisfaire tous les tests pour être retenu. `!` ou `-not` inverse un test ; `-o` est le OU.

**Les critères fréquents :**

| Critère | Signification |
|---|---|
| `-type f` / `-type d` | fichier / répertoire |
| `-size +10k` / `-size -3k` | plus grand / plus petit que (k=Kio, M=Mio) |
| `-perm 777` | permissions **exactement** 777 (`-perm -777` = au moins ces bits) |
| `-name "*.log"` | nom (avec motif glob) |
| `-mtime +30` | modifié il y a plus de 30 jours |
| `! -newermt "01/01/2020"` | **pas** plus récent qu'une date = plus ancien |
| `-maxdepth 1` | ne pas descendre dans les sous-dossiers |

**Le `+` et le `-` devant les nombres** sont la source d'erreur classique : `+10k` = strictement plus grand, `-3k` = strictement plus petit, `10k` = exactement. Idem pour `-mtime`/`-perm`.

**Deux formes d'`-exec` :**
```bash
find ... -exec rm {} \;     # lance la commande UNE FOIS PAR fichier  ({} = le fichier)
find ... -exec rm {} +      # regroupe : UN SEUL appel avec tous les fichiers (plus rapide)
```
Le `\;` (point-virgule échappé) termine la commande dans la première forme.

**Réflexe de sécurité : tester avant d'agir.** Lancer d'abord le `find` **sans** `-exec` (ou avec `-exec echo {} \;`) pour voir ce qui sera touché, vérifier le nombre avec `| wc -l`, puis seulement ajouter `rm`/`mv`. Une fois la suppression faite, c'est irréversible.

**Pièges** :
- `-maxdepth` doit venir **avant** les autres tests, sinon `find` avertit.
- `-perm 777` (exact) ≠ `-perm -777` (contient au moins ces bits) ≠ `-perm /777` (au moins un de ces bits).
- Les noms de fichiers avec espaces cassent les pipes ; `-exec` (qui ne passe pas par le shell) les gère correctement, contrairement à `... | xargs`.
- `find ! -newermt "DATE"` cible les fichiers **plus anciens** que la date — relire l'énoncé pour le sens.

## Énoncé

Solve this question on: `data-001`

There is a backup folder on server `data-001` at `/var/backup/backup-015`, it needs to be cleaned up.

First:
- Delete all files modified before `01/01/2020`
Then for the remaining:
- Find all files smaller than `3KiB` and move these to `/var/backup/backup-015/small/`
- Find all files larger than `10KiB` and move these to `/var/backup/backup-015/large/`
- Find all files with permission `777` and move these to `/var/backup/backup-015/compromised/`

## Solution

First we find the backup location:
```bash
ssh data-001
root@data-001:~$ cd /var/backup/backup-015
root@data-001:/var/backup/backup-015$ ls | grep backup | wc -l
300
```

Seems to contain good amount of files! Now we need to clean it up. A good way for this is to use `find` with arguments and a command to execute, like:

find -exec echo {} \; # will find all files and runs "echo FILE" for each

find -exec echo {} +  # will find all files and runs "echo FILE1 FILE2 FILE3 ..."

man find # search for "exec" to see info and explanation

man find # search for "-newerXY" to find files "newer than date"

**Delete files before date**

Using this we can delete all files created before 2020. Always "debug" a command first by just listing without executing a command:
```bash
root@data-001:/var/backup/backup-015$ find ! -newermt "01/01/2020" -type f
...
root@data-001:/var/backup/backup-015$ find ! -newermt "01/01/2020" -type f | wc -l
21
root@data-001:/var/backup/backup-015$ find ! -newermt "01/01/2020" -type f -exec rm {} \;
root@data-001:/var/backup/backup-015$ ls | grep backup | wc -l
279 # 21 deleted
```

**Move small files**

Now we move all small files into the subfolder:
```bash
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size -3k -type f # find
...
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size -3k -type f | wc -l
24
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size -3k -type f -exec mv {} ./small \; # move
```

**Move large files**

Next we move all larger files into the subfolder:
```bash
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size +10k -type f # find
...
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size +10k -type f | wc -l
11
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size +10k -type f -exec mv {} ./large \; # move
```

**Move open permission files**

And finally we move all files with too open permissions into the subfolder:
```bash
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -perm 777 -type f # find
...
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -perm 777 -type f | wc -l
12
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -perm 777 -type f -exec mv {} ./compromised \; # move
```

### Result
```bash
root@data-001:/var/backup/backup-015$ ls | grep backup | wc -l
232
root@data-001:/var/backup/backup-015$ ls small/ | wc -l
24
root@data-001:/var/backup/backup-015$ ls large/ | wc -l
11
root@data-001:/var/backup/backup-015$ ls compromised/ | wc -l
12
```
