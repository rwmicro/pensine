# Question 5 — Archives and Compression

## Notes d'apprentissage

Sous Unix, **archiver** et **compresser** sont deux opérations distinctes — c'est l'idée fondamentale qui débloque tout cet exercice.

**Modèle mental : deux couches empilées.**

```
fichiers  ──►  [ tar ]  ──►  une seule "tarball"  ──►  [ gzip/bzip2/xz ]  ──►  fichier compressé
              archivage      (.tar, non compressé)        compression          (.tar.gz, .tar.bz2)
```

- `tar` (*tape archive*) **regroupe** plusieurs fichiers en un seul flux, en préservant arborescence, permissions et propriétaires. Il ne compresse rien.
- `gzip`, `bzip2`, `xz` **compressent** un flux d'octets. Ils ne connaissent rien aux fichiers ni aux dossiers.

C'est pourquoi `.tar.gz` (= tar puis gzip) est une convention si répandue. Convertir un `.tar.bz2` en `.tar.gz` revient donc à : décompresser la couche bzip2, puis recompresser la même couche tar en gzip — sans toucher au contenu.

**Les options `tar` à connaître par cœur :**

```bash
tar -czf a.tar.gz dossier/    # Create gZip File  (créer)
tar -xzf a.tar.gz             # eXtract           (extraire)
tar -tzf a.tar.gz             # lisT              (lister sans extraire)
tar -xf a.tar.gz -C /dest     # extraire vers un répertoire précis
```

Moyen mnémotechnique : **c**reate / e**x**tract / lis**t**, **f**ichier (toujours en dernier, suivi du nom), **z**=gzip / **j**=bzip2 / **J**=xz. `tar` détecte souvent le format automatiquement à l'extraction, mais l'expliciter ne nuit pas.

**Niveau de compression :**

```bash
gzip --best fichier.tar          # -9, compression maximale (plus lent)
tar -I 'gzip -9' -cf a.tar.gz -C dossier .   # passer une commande de compression à tar
```

`bzip2` compresse mieux que `gzip` mais plus lentement ; `xz` encore mieux mais encore plus lent. Compromis classique taille/vitesse.

**Vérifier qu'une conversion a préservé le contenu :** comparer la liste triée des deux archives.

```bash
tar -tjf import001.tar.bz2 | sort > liste_bz2
tar -tzf import001.tar.gz  | sort > liste_gz
diff liste_bz2 liste_gz       # aucune différence = même contenu
```

**Pièges** :
- `bunzip2 -k` : le `-k` (*keep*) **conserve** l'original, sinon il est supprimé — crucial quand l'énoncé interdit de modifier le fichier source.
- L'ordre des lettres importe peu, mais `f` doit immédiatement précéder le nom de fichier.
- La variable `GZIP=-9` est dépréciée ; préférer `tar -I 'gzip -9'`.

## Énoncé

Solve this question on: `data-001`

There is archive `/imports/import001.tar.bz2` on server `data-001`. You're asked to create a new gzip compressed archive with its raw contents.

Store the new archive under `/imports/import001.tar.gz`. Compression should be the best possible, using gzip.

To make sure both archives contain the same files, write a list of their sorted contents into `/imports/import001.tar.bz2_list` and `/imports/import001.tar.gz_list`.

> Do not modify or delete the original archive `import001.tar.bz2`

## Solution

We connect to `data-001` and have a look at the folder:
```bash
ssh data-001
root@data-001:~$ cd /imports
root@data-001:/imports$ ls -lh
total 1.5K
-rw-r--r-- 1 root root 560 Jul 16 13:49 import001.tar.bz2
```

### Possibility 1 — (use the tar layer)
We extract the `bzip2` archive and receive an uncompressed `tar` archive:

> We can install `bzip2` via the package manager if not available
```bash
root@data-001:/imports$ bunzip2 -k import001.tar.bz2
root@data-001:/imports$ ls -lh
total 3.0K
-rw-r--r-- 1 root root 20K Jul 16 14:20 import001.tar # combination of all files without compression
-rw-r--r-- 1 root root 550 Jul 16 14:20 import001.tar.bz2
```

Every tar archive contains a "tar" data layer. This can then be further compressed with various compression algorithms. Here we can now go ahead and create a new gzip compression from the tar layer:
```bash
root@data-001:/imports$ gzip --best import001.tar
root@data-001:/imports$ ls -lh
total 2.0K
-rw-r--r-- 1 root root 550 Jul 16 14:20 import001.tar.bz2
-rw-r--r-- 1 root root 544 Jul 16 14:20 import001.tar.gz
```

### Possibility 2 — (completely extract and pack again)
We extract the files into a new subfolder:
```bash
root@data-001:/imports$ mkdir import001
root@data-001:/imports$ tar xf import001.tar.bz2 -C import001
root@data-001:/imports$ find import001/
import001/
import001/2ba047d9-a9b3-4261-a4a0-0d23447ebdcd
import001/2ba047d9-a9b3-4261-a4a0-0d23447ebdcd/e48edbdd
import001/2ba047d9-a9b3-4261-a4a0-0d23447ebdcd/fc2639f1
import001/2ba047d9-a9b3-4261-a4a0-0d23447ebdcd/8b718f8f
import001/2ba047d9-a9b3-4261-a4a0-0d23447ebdcd/5d517b37
import001/5d517b37-efd3-4872-b107-502aa4b58b4c
...
```

Now we create the new required archive
```bash
root@data-001:/imports$ GZIP=-9 tar czf import001.tar.gz -C import001 .
```

Using the GZIP env variable is deprecated, instead we could use:
```bash
root@data-001:/imports$ tar -I 'gzip -9' -cf import001.tar.gz -C import001 .
```

We should see:
```bash
root@data-001:/imports$ ls -lh
total 4.5K
drwxr-xr-x 7 ubuntu ubuntu   7 Jul 16 13:32 import001
-rw-r--r-- 1 root   root   550 Jul 16 13:57 import001.tar.bz2
-rw-r--r-- 1 root   root   531 Jul 16 14:00 import001.tar.gz
```

### Finally
We ensure that both archives contain the same files and structure:
```bash
root@data-001:/imports$ tar tf import001.tar.bz2 | sort > import001.tar.bz2_list
root@data-001:/imports$ tar tf import001.tar.gz | sort > import001.tar.gz_list
```

To compare further we could use `cat import001.tar.bz2_list | sha512sum` and compare the hashes.

To see some info about the compression ratio we can run
```bash
root@data-001:/imports$ gzip -l import001.tar.gz
```

Finally we should have these files:
```bash
root@data-001:/imports$ rm -rf import001
root@data-001:/imports$ ls -lha
total 6.0K
drwxr-xr-x 2 root root    6 Jul 16 14:07 .
drwxr-xr-x 3 root root    3 Jul 16 13:28 ..
-rw-r--r-- 1 root root  550 Jul 16 13:57 import001.tar.bz2
-rw-r--r-- 1 root root 1.2K Jul 16 14:07 import001.tar.bz2_list
-rw-r--r-- 1 root root  531 Jul 16 14:00 import001.tar.gz
-rw-r--r-- 1 root root 1.2K Jul 16 14:07 import001.tar.gz_list
```
