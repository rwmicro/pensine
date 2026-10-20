---
title: "LFCS Q12 — Flux de travail Git"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, workflow]
date: "2026-08-09"
---

# Question 12 — Flux de travail Git

## Notes d'apprentissage

Git suit l'historique d'un projet sous forme d'instantanés (*commits*). L'examen LFCS ne demande pas d'expertise Git, mais le flux de base : cloner, comparer des branches, fusionner, committer.

> [!tip] Modèle mental : trois zones
> ```
> répertoire de travail  ──git add──►  index (staging)  ──git commit──►  dépôt (.git)
> (vos fichiers)                       (changements                      (historique
>                                       préparés)                         des commits)
> ```

Un fichier ne rejoint l'historique qu'après `git add` (le mettre en staging) **puis** `git commit`. C'est en deux temps : on choisit *quoi* committer, puis on committe.

**Git fonctionne aussi en local.** On peut cloner un dépôt depuis un simple chemin de fichier, sans serveur distant :
```bash
git clone /repositories/auto-verifier ~/repositories/auto-verifier
```

**Branches : explorer et comparer sans fusionner.** Pour trouver dans quelle branche un fichier a une valeur donnée, on lit le fichier *sur* chaque branche sans changer de branche :
```bash
git branch -a                          # lister toutes les branches
git show dev4:config.yaml              # contenu de config.yaml DANS la branche dev4
git checkout dev5 -- config.yaml       # (autre approche) extraire un fichier d'une branche
```

**Fusionner (`merge`)** intègre l'historique d'une branche dans la branche courante :
```bash
git checkout main          # se placer sur la branche cible
git merge dev5             # y intégrer dev5
```
On fusionne *vers* la branche sur laquelle on se trouve. Toujours `checkout` la cible d'abord.

**Committer un dossier vide** : Git ne suit que des fichiers, pas des dossiers. Pour qu'un dossier `logs/` soit versionné, il faut y placer un fichier — convention : `.keep` ou `.gitkeep`.
```bash
mkdir logs && touch logs/.keep
git add logs/.keep
git commit -m "added log directory"
```

> [!warning] Pièges
> - Un dossier vide n'est jamais committé — d'où l'astuce du fichier `.keep`.
> - `git merge` peut produire un *conflit* si les deux branches modifient les mêmes lignes ; il faut alors éditer, `git add`, puis `git commit`.
> - Vérifier l'état à tout moment avec `git status` et `git log --oneline --graph`.
> - `git config user.name`/`user.email` doivent être définis pour committer.

## Énoncé

Résolvez cette question sur : `terminal`

Il vous est demandé d'effectuer des modifications dans le dépôt Git de l'application Auto-Verifier :
1. Clonez le dépôt `/repositories/auto-verifier` vers `/home/candidate/repositories/auto-verifier`.
    _Effectuez les étapes suivantes dans le répertoire fraîchement cloné_
2. Trouvez, parmi les branches `dev4`, `dev5` et `dev6`, celle dans laquelle le fichier `config.yaml` contient `user_registration_level: open`. Fusionnez uniquement cette branche dans la branche `main`
3. Dans la branche `main`, créez un nouveau répertoire `logs` à la racine du dépôt. Pour garantir que le répertoire sera committé, créez-y un fichier vide caché `.keep`
4. Committez votre changement avec le message `added log directory`

## Solution

### Étape 1 — Cloner le dépôt
Git est le plus souvent utilisé pour cloner et manipuler des dépôts distants comme sur Github ou Gitlab. Mais l'essentiel des fonctionnalités de Git peut aussi être utilisé en local. Nous clonons donc le répertoire local :
```bash
git clone /repositories/auto-verifier ~/repositories/auto-verifier
Cloning into '/home/candidate/repositories/auto-verifier'...
done.
cd ~/repositories/auto-verifier
~/repositories/auto-verifier$ git status
```

On branch main

Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean

### Étape 2 — Trouver la bonne branche
Nous listons d'abord toutes les branches :
```bash
~/repositories/auto-verifier$ git branch
```

* main
```bash
~/repositories/auto-verifier$ git branch -a
```

* main
  remotes/origin/HEAD -> origin/main

  remotes/origin/dev4

  remotes/origin/dev5

  remotes/origin/dev6

  remotes/origin/main

Nous pouvons simplement parcourir toutes les branches et vérifier le contenu du fichier :
```bash
~/repositories/auto-verifier$ git checkout dev4
```

Branch 'dev4' set up to track remote branch 'dev4' from 'origin'.

Switched to a new branch 'dev4'
```bash
~/repositories/auto-verifier$ grep user_registration_level config.yaml
user_registration_level: closed
~/repositories/auto-verifier$ git checkout dev5
```

Branch 'dev5' set up to track remote branch 'dev5' from 'origin'.

Switched to a new branch 'dev5'
```bash
~/repositories/auto-verifier$ grep user_registration_level config.yaml
user_registration_level: open
# Match! We could've stopped here, but let's also check the final branch
~/repositories/auto-verifier$ git checkout dev6
```

Branch 'dev6' set up to track remote branch 'dev6' from 'origin'.

Switched to a new branch 'dev6'
```bash
~/repositories/auto-verifier$ grep user_registration_level config.yaml
user_registration_level: closed
```

Nous pourrions aussi examiner le commit qui a réellement effectué le changement :
```bash
~/repositories/auto-verifier$ git checkout dev5
```

Branch 'dev5' set up to track remote branch 'dev5' from 'origin'.

Switched to a new branch 'dev5'
```bash
~/repositories/auto-verifier$ git log
commit cdf23b8c4000a4ff280f4feced059888e99d63e4 (HEAD -> dev5, origin/dev5)
Author: manager <manager@auto-verifier>
Date:   Tue Jan 10 17:03:55 2023 +1000
    updated config.yaml
commit 40842892dd0858eb96533654d5682c2c8b2ccb5c (origin/main, origin/HEAD, main)
Author: manager <manager@auto-verifier>
Date:   Fri Jan 6 06:33:43 2023 +1000
    set user_registration_level to closed
commit 9b73a28f2c87c6b34b9a779f5e82b4ebbf8bc78c
Author: manager <manager@auto-verifier>
Date:   Thu Jan 5 20:19:58 2023 +1000
    start of something cool
~/repositories/auto-verifier$ git diff main
diff --git a/config.yaml b/config.yaml
index bbbfb9b..5d1ccb4 100755
--- a/config.yaml
+++ b/config.yaml
@@ -31,7 +31,7 @@ system_transport_50x_list: 50x
 system_transport_50x_dsn: 'srv://default?list=50x'
 system_transport_50x_retry_strategy:
 system_transport_50x_ax_retries: 3
-user_registration_level: closed
+user_registration_level: open   # the change
 user_registration_enabled: false
 user_free_labels_enabled: true
 user_email_verify_enabled: true
```

Une autre méthode consiste à comparer depuis la branche `main` sans réellement basculer sur une autre :
```bash
~/repositories/auto-verifier$ git branch -a
```

* main
  remotes/origin/HEAD -> origin/main

  remotes/origin/dev4

  remotes/origin/dev5

  remotes/origin/dev6

  remotes/origin/main
```bash
~/repositories/auto-verifier$ git diff origin/dev5
diff --git a/config.yaml b/config.yaml
index 5d1ccb4..bbbfb9b 100755
--- a/config.yaml
+++ b/config.yaml
@@ -31,7 +31,7 @@ system_transport_50x_list: 50x
 system_transport_50x_dsn: 'srv://default?list=50x'
 system_transport_50x_retry_strategy:
 system_transport_50x_ax_retries: 3
-user_registration_level: open
+user_registration_level: closed
 user_registration_enabled: false
 user_free_labels_enabled: true
 user_email_verify_enabled: true
```

Il ne nous reste plus qu'à fusionner la branche `dev5` dans `main` :
```bash
~/repositories/auto-verifier$git checkout main
Switched to branch 'main'
```

Your branch is up to date with 'origin/main'.
```bash
~/repositories/auto-verifier$ git branch
  dev4
  dev5
  dev6
```

* main
```bash
~/repositories/auto-verifier$ git merge dev5
```

Updating 4084289..cdf23b8

Fast-forward

 config.yaml | 2 +-

 1 file changed, 1 insertion(+), 1 deletion(-)
```bash
~/repositories/auto-verifier$ grep user_registration_level config.yaml
user_registration_level: open
```

### Étape 3 — Créer un nouveau répertoire
Il nous est demandé de créer un nouveau répertoire ; voyons ce qui se passe si nous essayons de le committer tel quel :
```bash
~/repositories/auto-verifier$ mkdir logs
~/repositories/auto-verifier$ ls -l
total 20
-rwxrwxr-x 1 candidate candidate 2015 Jul 27 14:20 config.yaml
drwxrwxr-x 2 candidate candidate 4096 Jul 27 14:16 lib
drwxrwxr-x 2 candidate candidate 4096 Jul 27 14:29 logs
-rwxrwxr-x 1 candidate candidate  205 Jul 27 14:16 main.go
-rwxrwxr-x 1 candidate candidate  133 Jul 27 14:16 README.md
~/repositories/auto-verifier$ git status
```

On branch main

Your branch is ahead of 'origin/main' by 1 commit.

  (use "git push" to publish your local commits)

nothing to commit, working tree clean

Ci-dessus, nous voyons que `git status` ne liste pas du tout le répertoire parce qu'il est vide. Cela signifie qu'il ne serait pas non plus inclus dans les commits. Nous ajoutons maintenant le fichier demandé et voyons si les choses changent :
```bash
~/repositories/auto-verifier$ touch logs/.keep
~/repositories/auto-verifier$ git status
```

On branch main

Your branch is ahead of 'origin/main' by 1 commit.

  (use "git push" to publish your local commits)

Untracked files:

  (use "git add <file>..." to include in what will be committed)

        logs/

nothing added to commit but untracked files present (use "git add" to track)

C'est mieux !

### Étape 4 — Commiter
Il est toujours préférable de confirmer ce qui va être commité :
```bash
~/repositories/auto-verifier$ git status
```

On branch main

Your branch is ahead of 'origin/main' by 1 commit.

  (use "git push" to publish your local commits)

Untracked files:

  (use "git add <file>..." to include in what will be committed)

        logs/
```bash
~/repositories/auto-verifier$ git add logs
~/repositories/auto-verifier$ git status
```

On branch main

Your branch is ahead of 'origin/main' by 1 commit.

  (use "git push" to publish your local commits)

Changes to be committed:

  (use "git restore --staged <file>..." to unstage)

        new file:   logs/.keep
```bash
~/repositories/auto-verifier$ git commit -m 'added log directory'
[main 3cc53ed] added log directory
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 logs/.keep
```
