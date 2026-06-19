# Question 19 — Regex, filter out log lines

## Notes d'apprentissage

Les expressions régulières (*regex*) décrivent des motifs de texte. Couplées à `grep` (extraire) et `sed` (transformer), elles sont l'outil quotidien de l'analyse de logs.

**Modèle mental : `grep` cherche, `sed` remplace.**
- `grep` lit chaque ligne et **garde** celles qui correspondent au motif.
- `sed` lit chaque ligne et peut la **modifier** (substitution `s/motif/remplacement/`).

**Les métacaractères essentiels :**

| Motif | Sens |
|---|---|
| `.` | n'importe quel caractère |
| `.*` | n'importe quelle suite de caractères (y compris vide) |
| `^` | début de ligne |
| `$` | fin de ligne |
| `[abc]` | un caractère parmi a, b, c |
| `\|` | OU (en mode étendu) |
| `+` `?` `{n}` | quantificateurs (en mode étendu `-E`) |

**`^motif$` ancre toute la ligne.** « lignes commençant par `container.web`, finissant par `24h`, avec `Running` au milieu » se traduit directement :
```
^container.web.*Running.*24h$
```
Les ancres `^`/`$` évitent de capturer des lignes où le motif n'est qu'au milieu — c'est exactement le piège que l'énoncé tend (une URL `hacker-bot/1.2` qui n'est pas l'identité du navigateur).

**`grep -E` (regex étendues) : à privilégier.** Sans `-E` (mode basique), `+`, `?`, `|`, `{}` doivent être échappés (`\+`). Avec `-E`, ils s'écrivent naturellement.
```bash
grep -E "/app/user.*hacker-bot/1.2" nginx.log > nginx.log.extracted
grep -E "/app/user.*hacker-bot/1.2" nginx.log | wc -l    # toujours compter pour vérifier
```

**`sed` pour remplacer en place :**
```bash
sed 's/^container.web.*Running.*24h$/SENSITIVE LINE REMOVED/g' server.log   # vers stdout (test)
sed -i 's/.../.../g' server.log                                             # -i = modifie le fichier
```

**La méthode sûre : tester, compter, sauvegarder, appliquer.**
1. Lancer le `grep`/`sed` sans `-i` pour visualiser le résultat sur stdout.
2. `| wc -l` pour confirmer le bon nombre de lignes.
3. `cp server.log server.log.bak` — sauvegarde avant modification destructive.
4. Seulement alors `sed -i`.

**Pièges** :
- `.` correspond à *n'importe quel* caractère, donc `container.web` matche aussi `containerXweb` ; pour un point littéral il faut `\.` (souvent toléré à l'examen, mais à connaître).
- Sans `^`/`$`, le motif matche partout dans la ligne — source de faux positifs.
- `sed -i` est **irréversible** : toujours une `.bak` d'abord.
- En mode basique (sans `-E`), `+` et `|` ne sont pas spéciaux — d'où la préférence pour `grep -E` / `sed -E`.

## Énoncé

Solve this question on: `web-srv1`

On server `web-srv1` there are two log files that need to be worked with:
1. File `/var/log-collector/003/nginx.log`: extract all log lines where URLs start with `/app/user` and that were accessed by browser identity `hacker-bot/1.2`. Write only those lines into `/var/log-collector/003/nginx.log.extracted`
2. File `/var/log-collector/003/server.log`: replace all lines starting with `container.web`, ending with `24h` and that have the word `Running` anywhere in-between with: `SENSITIVE LINE REMOVED`

## Solution

First we find the files in the specified location
```bash
ssh web-srv1
root@web-srv1:~$ cd /var/log-collector/003
root@web-srv1:/var/log-collector/003$ ls -lha
total 23K
drwxr-xr-x 2 root root    4 Jul 19 09:43 .
drwxr-xr-x 8 root root    8 Jul 19 09:43 ..
-rw-r--r-- 1 root root 207K Jul 19 09:40 nginx.log
-rw-r--r-- 1 root root  29K Jul 19 09:39 server.log
```

### Step 1
To extract all log lines as required we could try some simple `grep` like:
```bash
root@web-srv1:/var/log-collector/003$ cat nginx.log | grep "/app/user" | grep "hacker-bot/1.2"
```

But this would also catch lines like these which are not asked for:

127.0.0.1 - - [18/Jul/2075:08:35:34 +0000] "GET /hacker-bot/1.2 HTTP/1.1" 200 8 "-" "/app/user" "-"

127.0.0.1 - - [18/Jul/2075:08:35:15 +0000] "GET /hacker-bot/1.2 HTTP/1.1" 200 8 "-" "/app/user" "-"

The lines above shouldn't match because the url is `hacker-bot/1.2` and **NOT** the browser identity.

So we better use a simple regex
```bash
root@web-srv1:/var/log-collector/003$ cat nginx.log | grep -E "/app/user.*hacker-bot/1.2"
```

It should be 27 lines:
```bash
root@web-srv1:/var/log-collector/003$ cat nginx.log | grep -E "/app/user.*hacker-bot/1.2" | wc -l
27
```

So we write it to the required location:
```bash
root@web-srv1:/var/log-collector/003$ cat nginx.log | grep -E "/app/user.*hacker-bot/1.2" > nginx.log.extracted
```

### Step 2
Next we shall remove some sensitive logs in `server.log`. Anything in the pattern of:

container.web ... Running ... 24h

In regex this could be:

^container.web.*Running.*24h$

Let's give this a go:
```bash
root@web-srv1:/var/log-collector/003$ cat server.log | grep -E "^container.web.*Running.*24h$"
```

It should be 44 lines:
```bash
root@web-srv1:/var/log-collector/003$ cat server.log | grep -E "^container.web.*Running.*24h$"  | wc -l
44
```

To replace these we can use `sed` using the same regex
```bash
root@web-srv1:/var/log-collector/003$ sed 's/^container.web.*Running.*24h$/SENSITIVE LINE REMOVED/g' server.log
```

This will simply output everything to stdout for us to verify. We can even further check by counting the lines:
```bash
root@web-srv1:/var/log-collector/003$ sed 's/^container.web.*Running.*24h$/SENSITIVE LINE REMOVED/g' server.log | grep "SENSITIVE LINE REMOVED" | wc -l
44
```

Looks fine, 44 lines again. Now we can use `sed` to replace the actual file. Still, always make a backup!
```bash
root@web-srv1:/var/log-collector/003$ cp server.log server.log.bak # backups ftw
root@web-srv1:/var/log-collector/003$ sed -i 's/^container.web.*Running.*24h$/SENSITIVE LINE REMOVED/g' server.log
root@web-srv1:/var/log-collector/003$ cat /var/log-collector/003/server.log | grep 'SENSITIVE LINE REMOVED' | wc -l
44
```

The 44 we see above is the result we want.

