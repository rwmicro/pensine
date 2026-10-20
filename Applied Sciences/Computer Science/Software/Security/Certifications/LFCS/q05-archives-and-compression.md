---
title: "LFCS Q05 — Archives et compression"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, archives, compression]
date: "2026-08-09"
---

# Question 5 — Archives et compression

## Notes d'apprentissage

Sous Unix, **archiver** et **compresser** sont deux opérations distinctes — c'est l'idée fondamentale qui débloque tout cet exercice.

> [!tip] Modèle mental : deux couches empilées
> ```
> fichiers  ──►  [ tar ]  ──►  une seule "tarball"  ──►  [ gzip/bzip2/xz ]  ──►  fichier compressé
>               archivage      (.tar, non compressé)        compression          (.tar.gz, .tar.bz2)
> ```

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

> [!warning] Pièges
> - `bunzip2 -k` : le `-k` (*keep*) **conserve** l'original, sinon il est supprimé — crucial quand l'énoncé interdit de modifier le fichier source.
> - L'ordre des lettres importe peu, mais `f` doit immédiatement précéder le nom de fichier.
> - La variable `GZIP=-9` est dépréciée ; préférer `tar -I 'gzip -9'`.

## Énoncé

Résolvez cette question sur : `data-001`

Le serveur `data-001` héberge l'archive `/imports/import001.tar.bz2`. Il vous est demandé de créer une nouvelle archive compressée avec gzip à partir de son contenu brut.

Stockez la nouvelle archive sous `/imports/import001.tar.gz`. La compression doit être la meilleure possible, avec gzip.

Pour vous assurer que les deux archives contiennent les mêmes fichiers, écrivez la liste triée de leur contenu dans `/imports/import001.tar.bz2_list` et `/imports/import001.tar.gz_list`.

> Ne modifiez pas et ne supprimez pas l'archive d'origine `import001.tar.bz2`

## Solution

Nous nous connectons à `data-001` et jetons un œil au dossier :
```bash
ssh data-001
root@data-001:~$ cd /imports
root@data-001:/imports$ ls -lh
total 1.5K
-rw-r--r-- 1 root root 560 Jul 16 13:49 import001.tar.bz2
```

### Possibilité 1 — (utiliser la couche tar)
Nous décompressons l'archive `bzip2` et obtenons une archive `tar` non compressée :

> Nous pouvons installer `bzip2` via le gestionnaire de paquets s'il n'est pas disponible
```bash
root@data-001:/imports$ bunzip2 -k import001.tar.bz2
root@data-001:/imports$ ls -lh
total 3.0K
-rw-r--r-- 1 root root 20K Jul 16 14:20 import001.tar # combination of all files without compression
-rw-r--r-- 1 root root 550 Jul 16 14:20 import001.tar.bz2
```

Toute archive tar contient une couche de données « tar ». Celle-ci peut ensuite être compressée avec différents algorithmes de compression. Ici, nous pouvons maintenant créer une nouvelle compression gzip à partir de la couche tar :
```bash
root@data-001:/imports$ gzip --best import001.tar
root@data-001:/imports$ ls -lh
total 2.0K
-rw-r--r-- 1 root root 550 Jul 16 14:20 import001.tar.bz2
-rw-r--r-- 1 root root 544 Jul 16 14:20 import001.tar.gz
```

### Possibilité 2 — (tout extraire puis tout recompresser)
Nous extrayons les fichiers dans un nouveau sous-dossier :
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

Nous créons maintenant la nouvelle archive demandée
```bash
root@data-001:/imports$ GZIP=-9 tar czf import001.tar.gz -C import001 .
```

L'utilisation de la variable d'environnement GZIP est dépréciée ; nous pourrions plutôt utiliser :
```bash
root@data-001:/imports$ tar -I 'gzip -9' -cf import001.tar.gz -C import001 .
```

Nous devrions voir :
```bash
root@data-001:/imports$ ls -lh
total 4.5K
drwxr-xr-x 7 ubuntu ubuntu   7 Jul 16 13:32 import001
-rw-r--r-- 1 root   root   550 Jul 16 13:57 import001.tar.bz2
-rw-r--r-- 1 root   root   531 Jul 16 14:00 import001.tar.gz
```

### Pour finir
Nous vérifions que les deux archives contiennent bien les mêmes fichiers et la même structure :
```bash
root@data-001:/imports$ tar tf import001.tar.bz2 | sort > import001.tar.bz2_list
root@data-001:/imports$ tar tf import001.tar.gz | sort > import001.tar.gz_list
```

Pour pousser la comparaison, nous pourrions utiliser `cat import001.tar.bz2_list | sha512sum` et comparer les empreintes.

Pour obtenir quelques informations sur le taux de compression, nous pouvons lancer
```bash
root@data-001:/imports$ gzip -l import001.tar.gz
```

Enfin, nous devrions obtenir ces fichiers :
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
