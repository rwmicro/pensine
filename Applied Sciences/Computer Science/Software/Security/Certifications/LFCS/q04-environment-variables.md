# Question 4 — Environment Variables

## Notes d'apprentissage

Les variables d'environnement configurent le comportement des programmes sans toucher à leur code (`PATH`, `LANG`, `HOME`, proxies…). Comprendre **leur portée** est le cœur de cet exercice.

**Modèle mental : variable de shell vs variable d'environnement.**

```bash
VAR=valeur          # variable de SHELL : visible dans ce shell uniquement
export VAR=valeur   # variable d'ENVIRONNEMENT : héritée par tous les processus enfants
```

La différence se joue à `export`. Sans `export`, la variable existe dans le shell courant mais **disparaît** dès qu'on lance un sous-processus. Avec `export`, elle est copiée dans l'environnement de chaque enfant.

```
shell parent
│  VAR1=x          (shell uniquement)
│  export VAR2=y   (exportée)
│
└─► sous-processus (ex: un script bash)
       VAR1  →  ABSENTE
       VAR2  →  "y"   (héritée)
```

**Point crucial : l'héritage va vers le bas, jamais vers le haut.** Un script ne peut pas modifier l'environnement de son shell parent (c'est pourquoi un script qui fait `cd` ne déplace pas votre terminal). Pour qu'une définition agisse sur le shell courant, il faut la **sourcer** : `source script.sh` ou `. script.sh` — le script s'exécute alors *dans* le shell courant, pas dans un enfant.

**Où sont définies les variables au login ?**

| Fichier | Quand |
|---|---|
| `/etc/environment` | toutes sessions, format `CLE=valeur` (pas de scripting) |
| `/etc/profile`, `/etc/profile.d/*` | shells de login, tous utilisateurs |
| `~/.bash_profile` / `~/.profile` | shell de login d'un utilisateur |
| `~/.bashrc` | shell interactif non-login (nouveau terminal) |

**Inspection :**

```bash
echo $VAR             # afficher une variable
env                   # lister les variables EXPORTÉES (environnement)
set                   # lister TOUT (shell + environnement + fonctions)
printenv VAR          # afficher une variable d'environnement précise
```

**Pièges** :
- `VAR = valeur` (avec espaces) est une **erreur** : bash y voit une commande `VAR`. Toujours `VAR=valeur` sans espace.
- `env | grep VAR` ne montre **pas** les variables non exportées — utiliser `set` pour celles-ci.
- Modifier `~/.bashrc` ne prend effet qu'aux nouveaux shells (ou après `source ~/.bashrc`).

## Énoncé

Solve this question on: `terminal`

There is an existing env variable for user `candidate@terminal`: `VARIABLE1=random-string`, defined in file `.bashrc`. Create a new script under `/opt/course/4/script.sh` which:
1. Defines a new env variable `VARIABLE2` with content `v2`, only available in the script itself
2. Outputs the content of the env variable `VARIABLE2`
3. Defines a new env variable `VARIABLE3` with content `${VARIABLE1}-extended`, available in the script itself and all child processes of the shell as well
4. Outputs the content of the env variable `VARIABLE3`

> ℹ️ Do not alter the `.bashrc` file, everything needs to be done in the script itself

## Solution

Well, let's check the existing variable and its content as mentioned:
```bash
echo $VARIABLE1
random-string
env | grep VARIABLE
VARIABLE1=random-string
```

How the variable's value defined? Let's check the `.bashrc` file:
```bash
cat .bashrc | grep VARIABLE1
export VARIABLE1=random-string
```

Now let's create a script which will define a new env variable called `VARIABLE2` with content `v2`:
```bash
vim /opt/course/4/script.sh
VARIABLE2="v2"
echo $VARIABLE2
```

We give it a try, it should output the variable content, but shouldn't make it available (export) afterwards:
```bash
bash /opt/course/4/script.sh
v2
```

Finally, we define the third environment variable called `VARIABLE3` within the same script

VARIABLE2="v2"

echo $VARIABLE2

export VARIABLE3="${VARIABLE1}-extended"    # add

echo $VARIABLE3                             # add

Run and check the result
```bash
sh /opt/course/4/script.sh
v2
random-string-extended
```

What's the difference between export and not using export? Let's demonstrate it:
```bash
TEST1=test1
export TEST2=test2
echo $TEST1
test1
echo $TEST2
test2
bash
echo $TEST1 # variable NOT available in subprocesses
echo $TEST2 # exported variable available in subprocesses
test2
```
