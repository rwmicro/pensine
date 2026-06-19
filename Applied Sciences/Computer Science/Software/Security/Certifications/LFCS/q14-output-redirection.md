# Question 14 — Output redirection

## Notes d'apprentissage

Chaque processus naît avec **trois flux** standards. Les rediriger est un automatisme du shell, essentiel pour les logs, les scripts et le diagnostic.

**Modèle mental : trois descripteurs de fichiers.**

| Flux | Numéro | Rôle |
|---|---|---|
| `stdin` | 0 | entrée |
| `stdout` | 1 | sortie normale |
| `stderr` | 2 | sortie d'erreurs |

La séparation stdout/stderr est volontaire : elle permet de filtrer les résultats sans mélanger les messages d'erreur. C'est pourquoi `commande | wc -l` ne compte que le stdout — les erreurs partent ailleurs.

**Les opérateurs de redirection :**
```bash
cmd > fichier      # stdout ÉCRASE le fichier   (1> équivalent)
cmd >> fichier     # stdout AJOUTE à la fin
cmd 2> fichier     # stderr seul
cmd > f 2>&1       # stdout PUIS stderr vers le même fichier
cmd &> fichier     # raccourci bash : stdout + stderr
cmd 2>&1 | less    # envoyer aussi stderr dans le pipe
cmd > /dev/null    # jeter la sortie (le "trou noir")
```

**Le piège de l'ordre dans `> f 2>&1`.** `2>&1` signifie « envoie stderr là où va stdout *en ce moment* ». Donc :
- `cmd > f 2>&1` (correct) : stdout va vers `f`, puis stderr suit stdout vers `f`.
- `cmd 2>&1 > f` (faux) : stderr copie la destination *actuelle* de stdout (le terminal), **puis** stdout part vers `f` — stderr reste au terminal.

L'ordre se lit de gauche à droite. C'est l'erreur la plus classique de tout l'exercice.

**Le code de retour `$?`** : chaque commande renvoie un code de sortie (0 = succès, ≠0 = erreur). Il est stocké dans `$?` mais **écrasé par la commande suivante** :
```bash
output-generator        # lancer
echo $? > 4.out         # capturer IMMÉDIATEMENT le code (avant toute autre commande)
```

**Pièges** :
- `> ` écrase, `>>` ajoute — confondre les deux fait perdre des données.
- `2>&1` doit venir **après** la redirection de stdout, pas avant.
- `$?` ne reflète que la **dernière** commande : le capturer tout de suite.
- Dans un pipe `a | b`, `$?` donne le code de `b` (le dernier) ; utiliser `${PIPESTATUS[@]}` pour les autres.

## Énoncé

Solve this question on: `app-srv1`

On server `app-srv1` there is a program `/bin/output-generator` which, who would've guessed, generates some output. It'll always generate the very same output for every run:
1. Run it and redirect all `stdout` into `/var/output-generator/1.out`
2. Run it and redirect all `stderr` into `/var/output-generator/2.out`
3. Run it and redirect all `stdout` and `stderr` into `/var/output-generator/3.out`
4. Run it and write the exit code number into `/var/output-generator/4.out`

## Solution

We go ahead and check the program
```bash
ssh app-srv1
root@app-srv1:~$ output-generator
...
2021/07/20 08:58:20 32668 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32669 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32670 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32671 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32672 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32673 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32674 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32675 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32676 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32677 - a99947a1-2f68-475e-9326-32dbd4876f60
```

**Investigation**

What a mess! Let's try to count the rows:
```bash
root@app-srv1:~$ output-generator | wc -l
...
2021/07/20 09:00:44 22670 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22671 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22672 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22673 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22674 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22675 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22676 - a99947a1-2f68-475e-9326-32dbd4876f60
20342
```

It looks like `wc -l` does only count rows that are written to stdout.

We can investigate a bit further using `stdout` (1) and `stderr` (2) redirection
```bash
output-generator > /dev/null # no stdout rows
output-generator 1> /dev/null # no stdout rows (same command as above)
output-generator 1> /dev/null 2> /dev/null # no stdout or stderr
output-generator 2>&1 # stderr will be redirected into stdout
```

Using this we can count all lines:
```bash
root@app-srv1:~$ output-generator 2>&1 | wc -l
32678
```

**Solution**

We redirect as required:
```bash
root@app-srv1:~$ output-generator > /var/output-generator/1.out
root@app-srv1:~$ output-generator 2> /var/output-generator/2.out
root@app-srv1:~$ output-generator >> /var/output-generator/3.out 2>> /var/output-generator/3.out
root@app-srv1:~$ output-generator
root@app-srv1:~$ echo $? > /var/output-generator/4.out # get the exit code and redirect to file
```

Note that with `$?` we can access the exit code of the last command run. Which means we need to let `output-generator` finish properly and not interrupt it. We also can't run another command afterwards or else `$?` won't contain the `output-generator` exit code.

This should give us:
```bash
root@app-srv1:~$ cat /var/output-generator/1.out | wc -l
20342
root@app-srv1:~$ cat /var/output-generator/2.out | wc -l
12336
root@app-srv1:~$ cat /var/output-generator/3.out | wc -l
32678
root@app-srv1:~$ cat /var/output-generator/4.out
123
```

