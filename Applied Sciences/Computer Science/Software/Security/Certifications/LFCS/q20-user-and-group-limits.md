---
title: "LFCS Q20 — Limites utilisateurs et groupes"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, user, group, limits]
date: "2026-08-09"
---

# Question 20 — Limites utilisateurs et groupes

## Notes d'apprentissage

Les *ulimits* plafonnent les ressources qu'un utilisateur ou un processus peut consommer (nombre de processus, fichiers ouverts, mémoire…). Ils protègent le système contre l'épuisement, accidentel (boucle de `fork`) ou malveillant (*fork bomb*).

> [!tip] Modèle mental : limite douce (soft) vs limite dure (hard)
> ```
>         0 ───────────── soft ─────────── hard ──────► ∞
>                           │                │
>         l'utilisateur peut ajuster sa      l'utilisateur NE PEUT PAS
>         soft limit librement entre 0       dépasser la hard ; seul root
>         et la hard limit                   peut l'élever
> ```

- **soft** : la limite réellement appliquée, modifiable par l'utilisateur **jusqu'à** la hard.
- **hard** : le plafond absolu ; seul root peut le relever.

C'est tout l'enjeu de l'exercice : une soft limit posée dans `.bashrc` est contournable par l'utilisateur (`ulimit -S -u 1100`). Une hard limit dans `/etc/security/limits.conf` ne l'est pas.

**Deux endroits, deux portées :**
```bash
ulimit -a                 # voir les limites de la session courante
ulimit -S -u 1100         # modifier la SOFT (session, temporaire, contournable)
ulimit -H -u              # afficher la HARD
```
Pour une limite **persistante et non contournable**, c'est `/etc/security/limits.conf` (ou un fichier dans `/etc/security/limits.d/`), appliqué au login par le module PAM `pam_limits.so` (voir [[q30-pam-configuration]]).

**Syntaxe de `/etc/security/limits.conf` :**
```
<domaine>   <type>   <item>      <valeur>
jackie      hard     nproc       1024
@operators  hard     maxlogins   1
*           soft     nofile      4096
```
- **domaine** : un utilisateur, `@groupe`, ou `*` (tous).
- **type** : `soft`, `hard`, ou `-` (les deux).
- **item** : `nproc` (nb de processus), `nofile` (fichiers ouverts), `maxlogins` (sessions simultanées), `fsize`, `as` (mémoire)…

> [!warning] Pièges
> - Une limite via `.bashrc` n'est **pas** une vraie limite système : l'utilisateur peut l'éditer ou la relever. La « bonne » façon est `limits.conf`.
> - `limits.conf` n'agit qu'aux **nouvelles** sessions de login (via PAM) — pas sur les processus déjà lancés.
> - `@nom` cible un **groupe** ; sans `@`, c'est un utilisateur.
> - Une soft limit ne peut jamais dépasser la hard ; définir d'abord la hard si on veut une soft élevée.

## Énoncé

Sur un serveur `web01`, l'utilisatrice `jackie` a lancé un programme qui a créé tellement de processus que la machine a saturé. Pour parer au plus pressé, une commande `ulimit` a été ajoutée dans son `~/.bashrc`, mais elle ne fixe que la limite douce (soft) du nombre de processus.

1. Fixez une limite dure (hard) du nombre de processus pour `jackie`, avec la même valeur que la limite douce actuelle, au bon endroit (pas dans `.bashrc`).
2. Limitez les membres du groupe `operators` à une seule session ouverte à la fois, avec `maxlogins`.

> `maxlogins` ne se vérifie qu'en ouvrant plusieurs sessions en même temps, par exemple deux connexions SSH.

## Solution

### Étape 1
Eh bien, cela fait beaucoup. Nous examinons d'abord cet utilisateur et ses limites :
```bash
root@server:~$ su jackie
jackie@server:/root$ cd
jackie@server:~$
jackie@server:~$ ulimit -a
core file size          (blocks, -c) 0
data seg size           (kbytes, -d) unlimited
scheduling priority             (-e) 0
file size               (blocks, -f) unlimited
pending signals                 (-i) 7815
max locked memory       (kbytes, -l) 64
max memory size         (kbytes, -m) unlimited
open files                      (-n) 1024
pipe size            (512 bytes, -p) 8
POSIX message queues     (bytes, -q) 819200
real-time priority              (-r) 0
stack size              (kbytes, -s) 8192
cpu time               (seconds, -t) unlimited
max user processes              (-u) 1024 # that's he one!
virtual memory          (kbytes, -v) unlimited
file locks                      (-x) unlimited
```

Avec `ulimit`, nous pouvons voir toutes les limites configurées, et `max user processes` vaut 1024. Nous devons vérifier comment cela a été défini dans `.bashrc` :
```bash
jackie@server:~$ if ! shopt -oq posix; then
...
ulimit -S -u 1024 # current implementation
```

Cela fonctionne, mais l'utilisatrice `jackie` pourrait le modifier elle-même comme ceci :
```bash
jackie@server:~$ ulimit -u # list current
1024
jackie@server:~$ ulimit -S -u 1100
jackie@server:~$ ulimit -u
1100
```

Nous supprimons d'abord la ligne qui avait été ajoutée comme correctif temporaire
```bash
root@server:~$ vim /home/jackie/.bashrc # remove the ulimit setting
```

Ensuite, nous la configurons via `/etc/security/limits.conf` (nous devons être root pour cela). Ce fichier contient déjà quelques exemples utiles en bas. Nous ajoutons une nouvelle ligne
```bash
root@server:~$ vim /etc/security/limits.conf
...
jackie         hard    nproc           1024     # add a new line
```

Nous pouvons maintenant confirmer notre changement :
```bash
jackie@server:~$ ulimit -u
1024
jackie@server:~$ ulimit -S -u 1100
bash: ulimit: max user processes: cannot modify limit: Invalid argument
```

L'utilisatrice `jackie` n'est plus capable de modifier cette limite elle-même.

### Étape 2
L'autre ticket concernait la mise en place d'une limitation pour le groupe `operators`, nous l'ajoutons donc également au fichier :
```bash
root@server:~$ vim /etc/security/limits.conf
...
jackie          hard    nproc           1024
@operators      hard    maxlogins       1 # add this line
```

Nous ne pourrons peut-être pas tester ce réglage en raison de la façon dont le serveur a été configuré.

