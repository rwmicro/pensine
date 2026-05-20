---
title: "Git - Système de contrôle de version"
domain: "Applied Sciences"
subdomain: "Computer Science"
tags: [sciences-appliquées, informatique]
date: "2026-02-16"
---

# Git - Système de contrôle de version

## Vue d'ensemble

**Git** est un système de contrôle de version distribué (DVCS) créé par Linus Torvalds en 2005 pour gérer le développement du noyau Linux.

**Avantages** :
- Décentralisé : chaque développeur a une copie complète de l'historique
- Rapide et efficace
- Branches légères
- Intégrité des données (SHA-1)
- Open source et gratuit


## Configuration initiale

### Configuration de base

```bash
# Identité (obligatoire)
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"

# Éditeur par défaut
git config --global core.editor "vim"
git config --global core.editor "code --wait"  # VS Code

# Couleurs
git config --global color.ui auto

# Voir toute la configuration
git config --list
git config --global --list

# Voir un paramètre spécifique
git config user.name
```

### Niveaux de configuration

1. **System** (`/etc/gitconfig`) : `--system`
2. **Global** (`~/.gitconfig`) : `--global`
3. **Local** (`.git/config` du dépôt) : `--local` (par défaut)

La configuration locale surcharge la globale qui surcharge la système.


## Commandes de base

### Créer un dépôt

```bash
# Nouveau dépôt local
git init
git init mon-projet

# Cloner un dépôt existant
git clone https://github.com/user/repo.git
git clone https://github.com/user/repo.git nouveau-nom
git clone --depth 1 https://github.com/user/repo.git  # Clone superficiel (shallow)
```

### Workflow de base

```bash
# Voir le statut
git status
git status -s  # Version courte

# Ajouter des fichiers à l'index (staging area)
git add fichier.txt
git add *.js
git add .  # Tout ajouter
git add -p  # Ajouter par morceaux (interactif)

# Créer un commit
git commit -m "Message de commit"
git commit -am "Message"  # add + commit (fichiers suivis uniquement)
git commit --amend  # Modifier le dernier commit

# Voir l'historique
git log
git log --oneline
git log --graph --oneline --all
git log --since="2 weeks ago"
git log --author="Nom"
git log -- fichier.txt  # Historique d'un fichier
git log -p  # Avec les diff
git log -3  # 3 derniers commits

# Voir les différences
git diff  # Working dir vs staging
git diff --staged  # Staging vs dernier commit
git diff HEAD  # Working dir vs dernier commit
git diff branche1..branche2
```

### Annuler des modifications

```bash
# Annuler les modifications (working directory)
git restore fichier.txt
git checkout -- fichier.txt  # Ancienne syntaxe

# Retirer de la staging area
git restore --staged fichier.txt
git reset HEAD fichier.txt  # Ancienne syntaxe

# Annuler un commit (3 méthodes)
git reset --soft HEAD~1  # Garde les changements en staging
git reset --mixed HEAD~1  # Garde les changements (défaut)
git reset --hard HEAD~1  # DANGER : Supprime tout

# Créer un commit qui annule un autre
git revert <commit-hash>
git revert HEAD  # Annuler le dernier commit
```


## Branches

### Gestion des branches

```bash
# Lister les branches
git branch  # Locales
git branch -a  # Toutes (locales + distantes)
git branch -r  # Distantes uniquement

# Créer une branche
git branch nouvelle-branche
git branch nouvelle-branche <commit>  # À partir d'un commit

# Changer de branche
git checkout branche
git switch branche  # Nouvelle syntaxe

# Créer et changer de branche
git checkout -b nouvelle-branche
git switch -c nouvelle-branche  # Nouvelle syntaxe

# Renommer une branche
git branch -m ancien-nom nouveau-nom
git branch -m nouveau-nom  # Branche actuelle

# Supprimer une branche
git branch -d branche  # Sécurisé (refuse si non fusionnée)
git branch -D branche  # Force
```

### Fusion (merge)

```bash
# Fusionner une branche dans la branche actuelle
git merge branche-source

# Types de merge
git merge --ff branche  # Fast-forward (défaut si possible)
git merge --no-ff branche  # Force un commit de merge
git merge --squash branche  # Écrase tous les commits en un seul

# En cas de conflit
# 1. Résoudre manuellement les conflits dans les fichiers
# 2. Marquer comme résolu
git add fichier-resolu.txt
# 3. Finaliser le merge
git commit
```

### Rebase

```bash
# Rebaser la branche actuelle sur une autre
git rebase main
git rebase --onto nouvelle-base ancienne-base branche

# Rebase interactif (modifier l'historique)
git rebase -i HEAD~3  # 3 derniers commits

# Options du rebase interactif :
# pick   : garder le commit
# reword : modifier le message
# edit   : modifier le commit
# squash : fusionner avec le précédent
# fixup  : comme squash mais jette le message
# drop   : supprimer le commit

# En cas de conflit
git rebase --continue  # Après résolution
git rebase --skip  # Ignorer ce commit
git rebase --abort  # Annuler le rebase
```

**Règle d'or** : Ne jamais rebaser des commits déjà pushés sur une branche publique !


## Travail avec des dépôts distants

### Gestion des remotes

```bash
# Lister les remotes
git remote
git remote -v  # Avec les URLs

# Ajouter un remote
git remote add origin https://github.com/user/repo.git
git remote add upstream https://github.com/original/repo.git

# Modifier un remote
git remote set-url origin https://github.com/user/nouveau-repo.git

# Supprimer un remote
git remote remove origin

# Voir les détails d'un remote
git remote show origin
```

### Push et Pull

```bash
# Push (envoyer vers le remote)
git push origin main
git push -u origin main  # Set upstream (première fois)
git push  # Si upstream configuré
git push --all  # Toutes les branches
git push --tags  # Tous les tags
git push --force  # DANGER : Force le push (écrase l'historique distant)
git push --force-with-lease  # Plus sûr : vérifie avant de forcer

# Pull (récupérer + fusionner)
git pull origin main
git pull  # Si upstream configuré
git pull --rebase  # Rebase au lieu de merge

# Fetch (récupérer sans fusionner)
git fetch origin
git fetch --all  # Tous les remotes
git fetch --prune  # Nettoie les références obsolètes
```

### Synchronisation avec upstream

```bash
# Workflow fork/upstream classique
git remote add upstream https://github.com/original/repo.git
git fetch upstream
git checkout main
git merge upstream/main
# ou
git rebase upstream/main
git push origin main
```


## Tags

```bash
# Lister les tags
git tag
git tag -l "v1.*"  # Filtre

# Créer un tag léger
git tag v1.0.0

# Créer un tag annoté (recommandé)
git tag -a v1.0.0 -m "Version 1.0.0"

# Tagger un commit spécifique
git tag -a v0.9.0 <commit-hash> -m "Version 0.9.0"

# Voir les détails d'un tag
git show v1.0.0

# Supprimer un tag
git tag -d v1.0.0  # Local
git push origin --delete v1.0.0  # Distant

# Push des tags
git push origin v1.0.0  # Un tag spécifique
git push origin --tags  # Tous les tags
```


## Stash (remiser)

```bash
# Mettre de côté les modifications
git stash
git stash save "Message descriptif"
git stash -u  # Inclure les fichiers non suivis

# Lister les stash
git stash list

# Appliquer un stash
git stash apply  # Le plus récent
git stash apply stash@{2}  # Stash spécifique
git stash pop  # Apply + drop

# Supprimer un stash
git stash drop stash@{0}
git stash clear  # Tous les stash

# Créer une branche depuis un stash
git stash branch nouvelle-branche
```


## Recherche et navigation

### Git grep

```bash
# Rechercher dans le code
git grep "fonction"
git grep -n "fonction"  # Avec numéros de ligne
git grep -c "fonction"  # Compte les occurrences
git grep "fonction" -- "*.js"  # Dans les fichiers .js
```

### Git blame

```bash
# Voir qui a modifié chaque ligne
git blame fichier.txt
git blame -L 10,20 fichier.txt  # Lignes 10 à 20
git blame -e fichier.txt  # Montrer les emails
```

### Git bisect

```bash
# Trouver le commit qui a introduit un bug (recherche binaire)
git bisect start
git bisect bad  # Le commit actuel est mauvais
git bisect good v1.0.0  # Ce commit était bon
# Git checkout des commits, vous testez et marquez :
git bisect good  # ou
git bisect bad
# À la fin :
git bisect reset
```


## .gitignore

### Syntaxe

```gitignore
# Commentaire

# Fichier spécifique
config.local.json

# Extension
*.log
*.tmp

# Dossier
node_modules/
build/

# Tous les .txt sauf important.txt
*.txt
!important.txt

# Tous les .pdf dans doc/ et sous-dossiers
doc/**/*.pdf

# Négation
!important/
```

### Templates utiles

```gitignore
# Node.js
node_modules/
npm-debug.log
.env

# Python
__pycache__/
*.py[cod]
venv/
.pytest_cache/

# Java
*.class
target/

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

### Ignorer après commit

```bash
# Fichier déjà commité qu'on veut ignorer
git rm --cached fichier.txt
git rm --cached -r dossier/
# Puis ajouter à .gitignore et commit
```


## Workflow avancés

### Git Flow

Branches principales :
- **main** : Production
- **develop** : Développement

Branches de support :
- **feature/*** : Nouvelles fonctionnalités
- **release/*** : Préparation release
- **hotfix/*** : Corrections urgentes

```bash
# Feature
git checkout -b feature/nouvelle-fonction develop
# ... travail ...
git checkout develop
git merge --no-ff feature/nouvelle-fonction
git branch -d feature/nouvelle-fonction
git push origin develop

# Release
git checkout -b release/1.2.0 develop
# ... préparation (version, changelog) ...
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Version 1.2.0"
git checkout develop
git merge --no-ff release/1.2.0
git branch -d release/1.2.0

# Hotfix
git checkout -b hotfix/1.2.1 main
# ... fix ...
git checkout main
git merge --no-ff hotfix/1.2.1
git tag -a v1.2.1 -m "Hotfix 1.2.1"
git checkout develop
git merge --no-ff hotfix/1.2.1
git branch -d hotfix/1.2.1
```

### GitHub Flow (simplifié)

1. Tout part de `main`
2. Créer une branche descriptive : `fix/bug-login`
3. Commit réguliers
4. Ouvrir une Pull Request
5. Discussion et review
6. Merge dans `main`
7. Deploy immédiat

### Trunk-Based Development

- Une seule branche principale (`main` ou `trunk`)
- Feature flags pour les fonctionnalités en cours
- CI/CD très forte
- Commits fréquents

## Commandes utiles

### Alias

```bash
# Créer des alias
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.lg "log --graph --oneline --all"

# Utilisation
git co main
git lg
```

### Cherry-pick

```bash
# Appliquer un commit spécifique sur la branche actuelle
git cherry-pick <commit-hash>
git cherry-pick <hash1> <hash2>
git cherry-pick <hash1>..<hash3>  # Range
```

### Reflog

```bash
# Historique de toutes les références (y compris les commits "perdus")
git reflog
git reflog show HEAD
git reflog show branche

# Récupérer un commit perdu
git reflog  # Trouver le SHA
git checkout <commit-hash>
git branch branche-recuperee  # Créer une branche
```

### Clean

```bash
# Supprimer les fichiers non suivis
git clean -n  # Dry run (voir ce qui serait supprimé)
git clean -f  # Force
git clean -fd  # Fichiers et dossiers
git clean -fx  # Inclure les ignorés
```

### Submodules

```bash
# Ajouter un submodule
git submodule add https://github.com/user/lib.git lib/

# Cloner un repo avec submodules
git clone --recurse-submodules https://github.com/user/repo.git

# Mettre à jour les submodules
git submodule update --init --recursive
git submodule update --remote

# Supprimer un submodule
git submodule deinit lib/
git rm lib/
```

## Astuces et bonnes pratiques

### Messages de commit

**Format conventionnel** :
```
type(scope): sujet

Corps du message (optionnel)

Footer (optionnel)
```

**Types** :
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage (pas de changement de code)
- `refactor`: Refactoring
- `test`: Ajout/modification de tests
- `chore`: Maintenance (build, dépendances)

**Exemples** :
```
feat(auth): add password reset functionality

fix(api): correct user validation logic

docs: update installation instructions
```

### Commits atomiques

- Un commit = une modification logique
- Facilite la revue de code
- Facilite les reverts
- Meilleur historique

### Branches

- Noms descriptifs : `feature/user-login`, `fix/header-bug`
- Branches courtes (merge rapidement)
- Supprimer les branches mergées

### Pull/Rebase

```bash
# Garder un historique propre
git config --global pull.rebase true

# Ou explicitement
git pull --rebase
```

### Vérifier avant de push

```bash
git log origin/main..HEAD  # Commits à push
git diff origin/main..HEAD  # Différences à push
```

## Dépannage

### Annuler un push

```bash
# SI personne n'a pull
git push --force-with-lease

# SI quelqu'un a pull : créer un revert
git revert <commit-hash>
git push
```

### Récupérer un fichier supprimé

```bash
# Fichier supprimé mais pas commité
git restore fichier.txt

# Fichier supprimé et commité
git log -- fichier.txt  # Trouver le commit avant suppression
git checkout <commit>^ -- fichier.txt
```

### Changer l'auteur du dernier commit

```bash
git commit --amend --author="Nom <email@example.com>"
```

### Résoudre les conflits de merge

```bash
# 1. Voir les fichiers en conflit
git status

# 2. Éditer les fichiers (chercher <<<<<<<, =======, >>>>>>>)

# 3. Marquer comme résolu
git add fichier-resolu.txt

# 4. Finaliser
git commit
# ou si en cours de rebase
git rebase --continue
```

## Outils et ressources

### Interfaces graphiques

- **GitKraken** : Multi-plateforme, puissant
- **SourceTree** : Gratuit, Windows/Mac
- **GitHub Desktop** : Simple, intégré GitHub
- **Git GUI** : Livré avec Git
- **Gitk** : Visualiseur d'historique livré avec Git

### Extensions VSCode

- GitLens
- Git Graph
- Git History

### Hosting

- **GitHub** : Le plus populaire
- **GitLab** : CI/CD intégré
- **Bitbucket** : Intégration Atlassian
- **Gitea** : Auto-hébergé léger

## Astuce : Télécharger un dossier d'un repo (SVN)

### Prérequis
- Package `subversion` sur votre distribution

### Méthode
1. Remplacer `tree/master` par `trunk` dans l'URL :
   
   `https://github.com/exemple/exemple/tree/master/test` ➜ `https://github.com/exemple/exemple/trunk/test`

2. Télécharger avec `svn checkout` :
```bash
svn checkout https://github.com/exemple/exemple/trunk/test
```


## Commandes de référence rapide

```bash
# Configuration
git config --global user.name "Nom"
git config --global user.email "email@example.com"

# Initialisation
git init
git clone <url>

# Changements
git status
git add <fichier>
git commit -m "message"
git diff

# Branches
git branch
git branch <branche>
git checkout <branche>
git merge <branche>

# Remote
git remote add origin <url>
git push -u origin main
git pull
git fetch

# Historique
git log
git log --oneline --graph
git reflog

# Annuler
git restore <fichier>
git reset --soft HEAD~1
git revert <commit>

# Stash
git stash
git stash pop
```
