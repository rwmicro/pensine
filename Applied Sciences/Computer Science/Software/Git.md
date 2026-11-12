---
title: "Git - Système de contrôle de version"
domain: "Applied Sciences"
subdomain: "Computer Science"
tags: [sciences-appliquées, informatique]
date: "2026-02-16"
---

# Git - Système de contrôle de version

En avril 2005, les développeurs du noyau Linux perdent du jour au lendemain l'outil avec lequel ils travaillaient, BitKeeper, dont l'éditeur retire la licence gratuite. Linus Torvalds décide d'écrire son propre outil. En une dizaine de jours, il a un prototype capable de gérer le code du noyau ; il l'appelle **Git**. Vingt ans plus tard, c'est l'outil de gestion de versions de presque tous les projets logiciels du monde.

Git est un système de contrôle de version **distribué** : chaque développeur possède une copie complète du dépôt et de tout son historique, et peut travailler, committer ou créer des branches sans serveur. Les échanges avec les autres ne sont que des synchronisations entre copies. C'est ce qui rend Git rapide, puisque presque tout se passe en local, et robuste, puisque chaque copie est une sauvegarde.

## Comprendre le modèle avant les commandes

La plupart des difficultés avec Git viennent d'un modèle mental flou. Trois idées suffisent à en comprendre l'essentiel.

D'abord, un **commit** n'est pas une liste de modifications mais un instantané complet du projet à un moment donné, accompagné d'un message, d'un auteur et d'un lien vers son ou ses commits parents. Chaque commit est identifié par une empreinte cryptographique (SHA-1 par défaut, SHA-256 en option) calculée à partir de son contenu et de ses parents : modifier un commit ancien change son identifiant, et donc celui de tous ses descendants. C'est ce qui garantit l'intégrité de l'historique, et c'est aussi pourquoi « réécrire l'historique » a des conséquences.

Ensuite, Git distingue trois zones. Le **répertoire de travail** contient les fichiers tels qu'on les édite. L'**index** (ou *staging area*) est une zone de préparation où l'on place, avec `git add`, exactement ce que l'on veut mettre dans le prochain commit. Le **dépôt** (le dossier `.git`) conserve les commits. Cette étape intermédiaire permet de découper un travail désordonné en commits propres, par exemple en n'ajoutant qu'une partie d'un fichier avec `git add -p`.

Enfin, une **branche** n'est qu'une étiquette mobile qui pointe vers un commit, et `HEAD` désigne la branche sur laquelle on se trouve. Créer une branche ne copie rien, ce qui explique qu'elles soient si légères et qu'on en crée pour la moindre fonctionnalité.

## Configurer Git

Avant le premier commit, Git doit savoir qui vous êtes, car chaque commit enregistre un nom et une adresse. La configuration existe à trois niveaux : système (`/etc/gitconfig`, option `--system`), utilisateur (`~/.gitconfig`, option `--global`) et dépôt (`.git/config`, option `--local`, par défaut). Le niveau le plus proche l'emporte : un réglage du dépôt surcharge le réglage global, qui surcharge celui du système.

```bash
# Identité (obligatoire)
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"

# Éditeur par défaut
git config --global core.editor "vim"
git config --global core.editor "code --wait"  # VS Code

# Voir toute la configuration, ou un paramètre
git config --list
git config user.name
```

## Le cycle de travail quotidien

On commence soit en créant un dépôt avec `git init`, soit en copiant un dépôt existant avec `git clone`. Un clone superficiel (`--depth 1`) ne récupère que le dernier état, ce qui est utile pour un gros projet dont on n'a pas besoin de l'historique.

```bash
git init mon-projet
git clone https://github.com/user/repo.git
git clone --depth 1 https://github.com/user/repo.git  # Clone superficiel
```

Le travail suit ensuite toujours la même boucle : on modifie des fichiers, on regarde où on en est avec `git status`, on prépare le commit avec `git add`, puis on l'enregistre avec `git commit`. `git diff` montre ce qui a changé dans le répertoire de travail par rapport à l'index, et `git diff --staged` ce qui est dans l'index par rapport au dernier commit, c'est-à-dire ce qui partira dans le prochain.

```bash
git status
git add fichier.txt
git add -p                  # Choisir les morceaux à ajouter
git commit -m "Message de commit"
git commit --amend          # Corriger le dernier commit

git diff                    # Répertoire de travail vs index
git diff --staged           # Index vs dernier commit

git log --oneline --graph --all
git log -p -- fichier.txt   # Historique détaillé d'un fichier
```

## Revenir en arrière

Git offre plusieurs façons d'annuler, et le bon choix dépend de l'endroit où se trouve la modification. Pour abandonner une modification non commitée, on utilise `git restore` ; pour retirer un fichier de l'index sans perdre la modification, `git restore --staged`.

Pour annuler des commits, deux philosophies s'opposent. `git reset` déplace la branche vers un commit antérieur, comme si les commits suivants n'avaient jamais existé : avec `--soft`, les changements restent dans l'index ; avec `--mixed` (par défaut), ils restent dans le répertoire de travail ; avec `--hard`, ils sont effacés. `git revert`, au contraire, crée un nouveau commit qui applique l'inverse d'un commit existant, sans toucher à l'historique. La règle pratique est simple : `reset` pour ce qui n'a pas encore été partagé, `revert` pour ce qui l'a déjà été.

```bash
git restore fichier.txt            # Abandonner les modifications
git restore --staged fichier.txt   # Retirer de l'index

git reset --soft HEAD~1    # Défait le commit, garde les changements dans l'index
git reset --hard HEAD~1    # DANGER : supprime aussi les changements

git revert <commit-hash>   # Nouveau commit qui annule l'ancien
```

Même après un `reset --hard`, rien n'est vraiment perdu tout de suite : le **reflog** garde la trace de toutes les positions successives de `HEAD`, ce qui permet de retrouver un commit « disparu » et de recréer une branche dessus.

```bash
git reflog
git branch branche-recuperee <commit-hash>
```

## Branches, fusion et rebase

Puisqu'une branche n'est qu'un pointeur, on en crée une pour chaque sujet de travail, on y committe tranquillement, puis on réintègre le résultat. `git switch` est la commande moderne pour changer de branche ; `git checkout`, plus ancienne, faisait à la fois cela et la restauration de fichiers, ce qui prêtait à confusion.

```bash
git branch -a                    # Lister toutes les branches
git switch -c nouvelle-branche   # Créer et basculer
git switch main
git branch -m nouveau-nom        # Renommer la branche courante
git branch -d branche            # Supprimer (refuse si non fusionnée)
```

Pour réintégrer une branche, il y a deux approches. La **fusion** (`git merge`) relie les deux historiques. Si la branche cible n'a pas bougé entre-temps, Git avance simplement son pointeur (*fast-forward*) ; sinon il crée un commit de fusion à deux parents. L'option `--no-ff` force ce commit même quand il n'est pas nécessaire, pour garder la trace qu'une branche a existé, et `--squash` écrase toute la branche en un seul commit.

Le **rebase** (`git rebase main`) procède autrement : il rejoue un à un les commits de la branche courante au-dessus de `main`, comme si on avait commencé le travail à partir de son état actuel. L'historique devient linéaire et plus lisible, mais les commits rejoués sont de nouveaux commits, avec de nouveaux identifiants. Le rebase interactif (`git rebase -i`) permet en plus de réordonner, renommer, fusionner (`squash`, `fixup`) ou supprimer (`drop`) des commits avant de les partager.

```bash
git merge branche-source
git merge --no-ff branche

git rebase main
git rebase -i HEAD~3       # Retravailler les 3 derniers commits
git rebase --continue      # Après avoir résolu un conflit
git rebase --abort         # Tout annuler
```

> [!warning] Règle d'or
> Ne jamais rebaser des commits déjà pushés sur une branche publique ! Le rebase réécrit l'historique (nouveaux hash de commits) — quiconque a déjà basé du travail sur l'ancien historique se retrouve avec des commits divergents impossibles à fusionner proprement.

Quand les deux côtés ont modifié les mêmes lignes, Git s'arrête sur un **conflit** et marque les zones concernées avec `<<<<<<<`, `=======` et `>>>>>>>`. On édite le fichier pour garder la bonne version, on le marque comme résolu avec `git add`, puis on termine avec `git commit` (pour une fusion) ou `git rebase --continue`.

Enfin, `git cherry-pick` applique un commit précis d'une autre branche sur la branche courante, ce qui sert typiquement à reporter un correctif.

## Travailler avec des dépôts distants

Un *remote* est une autre copie du dépôt, le plus souvent sur un serveur comme GitHub ou GitLab, à laquelle on donne un nom court : `origin` par convention pour son propre dépôt, `upstream` pour le projet d'origine d'un fork.

`git fetch` récupère les nouveaux commits du distant sans toucher à vos branches : on peut les examiner avant de décider quoi en faire. `git pull` fait un `fetch` suivi d'une fusion, ou d'un rebase avec `--rebase`. `git push` envoie vos commits ; l'option `-u` mémorise la branche distante associée pour que les `push` et `pull` suivants n'aient plus besoin d'arguments.

```bash
git remote -v
git remote add upstream https://github.com/original/repo.git

git fetch --prune          # Récupérer et nettoyer les références obsolètes
git pull --rebase
git push -u origin main
git push --force-with-lease
```

> [!tip] Pourquoi `--force-with-lease` plutôt que `--force`
> `--force` écrase le distant même si quelqu'un d'autre a poussé entre-temps — leurs commits disparaissent silencieusement. `--force-with-lease` vérifie d'abord que le distant est dans l'état où on l'a vu la dernière fois, et refuse sinon : ça transforme une perte de données silencieuse en erreur explicite.

Pour un fork, le cycle consiste à récupérer régulièrement le projet d'origine et à y rebaser ou fusionner son travail :

```bash
git fetch upstream
git switch main
git rebase upstream/main
git push origin main
```

## Tags, stash et autres outils du quotidien

Un **tag** marque un commit précis, en général une version publiée. Il ne bouge pas, contrairement à une branche. On préfère les tags annotés (`-a`), qui enregistrent un auteur, une date et un message. Les tags ne sont pas envoyés par un `push` ordinaire.

```bash
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
git tag -d v1.0.0 && git push origin --delete v1.0.0
```

Le **stash** met de côté des modifications en cours pour retrouver un répertoire propre, par exemple pour corriger un bug urgent sur une autre branche, puis les réapplique plus tard.

```bash
git stash push -m "Message descriptif"
git stash -u               # Inclure les fichiers non suivis
git stash list
git stash pop              # Réappliquer et supprimer de la pile
```

Pour enquêter dans un projet, `git grep` cherche dans les fichiers suivis, `git blame` indique pour chaque ligne le dernier commit qui l'a modifiée, et `git bisect` trouve le commit qui a introduit un bug par recherche dichotomique : on indique un commit « bon » et un « mauvais », Git propose un commit au milieu, on le teste, et en une dizaine d'étapes on isole le coupable parmi un millier de commits.

```bash
git grep -n "fonction" -- "*.js"
git blame -L 10,20 fichier.txt

git bisect start
git bisect bad              # Le commit actuel est mauvais
git bisect good v1.0.0      # Celui-ci était bon
# Tester chaque commit proposé, puis marquer good ou bad
git bisect reset
```

`git clean` supprime les fichiers non suivis ; toujours le lancer d'abord avec `-n` pour voir ce qui serait effacé. Les **submodules** permettent d'inclure un dépôt dans un autre en le figeant à un commit donné, au prix d'une gestion plus délicate (il faut penser à `--recurse-submodules` au clonage).

## Ignorer des fichiers

Le fichier `.gitignore` liste les fichiers que Git ne doit jamais suivre : dépendances installées, fichiers compilés, secrets, fichiers de l'éditeur ou du système. Les motifs acceptent les jokers, `**` pour n'importe quelle profondeur de dossiers et `!` pour une exception.

```gitignore
node_modules/
build/
*.log
.env

# Tous les .txt sauf important.txt
*.txt
!important.txt

# Tous les .pdf dans doc/ et ses sous-dossiers
doc/**/*.pdf

# Éditeurs et systèmes
.vscode/
.idea/
.DS_Store
```

Un fichier déjà suivi n'est pas concerné par `.gitignore` : il faut d'abord le retirer du suivi avec `git rm --cached fichier`, puis committer.

## Organiser le travail en équipe

Plusieurs modèles d'organisation des branches coexistent. **Git Flow** utilise une branche `main` pour la production et une branche `develop` pour l'intégration, plus des branches temporaires `feature/*`, `release/*` et `hotfix/*`. Il convient à des logiciels publiés en versions numérotées, mais il est lourd pour un service déployé en continu.

```bash
# Une fonctionnalité dans Git Flow
git switch -c feature/nouvelle-fonction develop
# ... travail ...
git switch develop
git merge --no-ff feature/nouvelle-fonction
git branch -d feature/nouvelle-fonction
```

Le **GitHub Flow** est plus simple : tout part de `main`, chaque changement se fait sur une branche courte, passe par une *pull request* avec revue, puis est fusionné et déployé. Le **trunk-based development** va plus loin : tout le monde committe très fréquemment sur une seule branche principale, les fonctionnalités inachevées sont masquées par des *feature flags*, et une intégration continue solide garantit que la branche reste toujours déployable.

Quel que soit le modèle, quelques habitudes rendent l'historique utile. Un commit doit correspondre à une seule modification logique, ce qui facilite la relecture et permet d'annuler proprement. Les messages gagnent à suivre une convention, comme les *Conventional Commits* (`type(portée): sujet`, avec des types comme `feat`, `fix`, `docs`, `refactor`, `test` ou `chore`), qui permet aussi de générer automatiquement des changelogs.

```
feat(auth): add password reset functionality

fix(api): correct user validation logic
```

Avant de pousser, il est prudent de vérifier ce qui va partir :

```bash
git log origin/main..HEAD    # Commits à pousser
git diff origin/main..HEAD   # Différences à pousser
```

## Récupérer un fichier ou un seul dossier

Pour retrouver un fichier supprimé dans un commit passé, on cherche le commit qui l'a supprimé, puis on restaure la version de son parent :

```bash
git log -- fichier.txt
git checkout <commit>^ -- fichier.txt
```

Pour ne télécharger qu'un dossier d'un gros dépôt, on combinait autrefois GitHub et Subversion, mais GitHub a cessé de prendre en charge Subversion en janvier 2024. La méthode actuelle est le clonage partiel avec *sparse checkout* :

```bash
git clone --filter=blob:none --sparse https://github.com/exemple/exemple.git
cd exemple
git sparse-checkout set test
```

## Aide-mémoire

```bash
# Configuration
git config --global user.name "Nom"
git config --global user.email "email@example.com"

# Démarrer
git init
git clone <url>

# Cycle de travail
git status
git add <fichier>
git commit -m "message"
git diff

# Branches
git branch
git switch -c <branche>
git merge <branche>

# Distant
git remote add origin <url>
git push -u origin main
git pull
git fetch

# Historique
git log --oneline --graph
git reflog

# Annuler
git restore <fichier>
git reset --soft HEAD~1
git revert <commit>

# Mettre de côté
git stash
git stash pop
```

## Ressources

- Scott Chacon et Ben Straub, [*Pro Git*](https://git-scm.com/book/fr/v2), le livre de référence, gratuit et traduit en français.
- Interfaces graphiques : GitKraken, SourceTree, GitHub Desktop, ou `gitk`, livré avec Git ; dans VS Code, les extensions GitLens et Git Graph.
- Hébergement : GitHub, GitLab (intégration continue intégrée), Bitbucket, ou Gitea pour un hébergement personnel léger.
