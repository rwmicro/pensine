---
title: "Docker"
domain: "Applied Sciences"
subdomain: "Computer Science > DevSecOps > Docker"
tags: [sciences-appliquées, informatique, devsecops, docker]
date: "2026-02-04"
parcours: "DevSecOps : conteneurs, CI/CD et sécurité"
parcours-description: "De Docker à Kubernetes et à leur sécurisation, puis GitLab CI/CD et le pipeline DevSecOps."
---

# Docker

« Ça marche sur ma machine. » Pendant des décennies, cette phrase a résumé le cauchemar du déploiement : une application qui tourne chez le développeur plante en production, parce que la version de Python, une bibliothèque système ou une variable d'environnement n'est pas la même. En 2013, une petite société de PaaS, dotCloud, présente à la conférence PyCon un outil interne qu'elle vient de libérer : **Docker**. L'idée est empruntée au transport maritime. Comme le conteneur standard a permis de charger n'importe quelle marchandise sur n'importe quel navire, Docker emballe une application avec tout ce dont elle a besoin, bibliothèques, configuration, système de fichiers, dans un **conteneur** qui s'exécute de la même façon partout.

> [!important] Idée clé
> Un conteneur n'est pas une VM allégée : il ne virtualise pas le matériel, il **partage le kernel de l'hôte** et isole le processus par des mécanismes du kernel Linux (namespaces, cgroups). C'est ce qui explique à la fois sa légèreté (pas d'OS à démarrer) et sa limite (un conteneur Linux ne peut pas faire tourner un kernel Windows).

## Conteneurs et machines virtuelles

Une machine virtuelle simule un ordinateur complet : un hyperviseur lui présente du matériel virtuel, sur lequel elle démarre son propre système d'exploitation. Elle pèse donc plusieurs gigaoctets et met des dizaines de secondes, voire des minutes, à démarrer, mais son isolation est forte, au niveau du matériel.

Un conteneur, lui, n'est qu'un processus ordinaire de l'hôte, auquel le noyau Linux donne une vue restreinte du système. Les **namespaces** lui font croire qu'il est seul : il a son propre arbre de processus, son propre réseau, ses propres points de montage, ses propres utilisateurs. Les **cgroups** limitent les ressources qu'il peut consommer, mémoire, CPU, entrées-sorties. Une image ne pèse souvent que quelques dizaines de mégaoctets et le conteneur démarre en une fraction de seconde. En contrepartie, tous les conteneurs partagent le même noyau, et une faille de ce noyau peut permettre de s'échapper d'un conteneur vers l'hôte.

## Images, conteneurs et registres

Trois notions organisent tout Docker. Une **image** est un modèle en lecture seule : un système de fichiers figé, construit par couches (*layers*) empilées, chacune correspondant à une étape de construction. Un **conteneur** est une instance en cours d'exécution d'une image, à laquelle Docker ajoute une fine couche en écriture ; quand on supprime le conteneur, cette couche disparaît avec lui, ce qui rend les conteneurs éphémères par nature. Un **registre** stocke et distribue les images : Docker Hub est le registre public par défaut, et les entreprises utilisent des registres privés comme GHCR, GitLab Registry ou Harbor.

Côté logiciel, le **Docker Engine** se compose d'un démon (`dockerd`) qui fait le vrai travail, d'une API REST et de la commande `docker`, qui n'est qu'un client de cette API.

```bash
# Images
docker pull nginx:latest
docker images
docker build -t mon-app:v1 .
docker rmi mon-app:v1
docker image prune          # Supprimer les images inutilisées

# Conteneurs
docker run -d -p 80:80 --name webserver nginx
docker ps                   # Conteneurs actifs (-a pour tous)
docker logs webserver
docker exec -it webserver /bin/sh
docker stop webserver && docker rm webserver
```

Dans `docker run`, `-d` lance le conteneur en arrière-plan et `-p 80:80` relie le port 80 de l'hôte au port 80 du conteneur.

## Construire une image : le Dockerfile

Une image se décrit dans un **Dockerfile**, une recette exécutée de haut en bas. `FROM` choisit l'image de départ, `WORKDIR` fixe le répertoire de travail, `COPY` copie des fichiers de l'hôte dans l'image (`ADD` fait de même mais sait aussi extraire des archives et télécharger des URL, ce qui le rend moins prévisible : on lui préfère `COPY`). `RUN` exécute une commande pendant la construction et crée une nouvelle couche, `ENV` et `ARG` définissent des variables d'exécution ou de construction, `EXPOSE` documente les ports utilisés, `USER` change d'utilisateur. Enfin, `CMD` donne la commande lancée par défaut au démarrage du conteneur, tandis qu'`ENTRYPOINT` fixe l'exécutable principal, auquel `CMD` fournit alors des arguments par défaut.

```dockerfile
FROM node:22-alpine
WORKDIR /app

# Dépendances d'abord (voir l'encadré sur le cache)
COPY package*.json ./
RUN npm ci --omit=dev

# Puis le code source
COPY . .

EXPOSE 3000
USER node
CMD ["node", "server.js"]
```

> [!tip] Pourquoi cet ordre précis
> Docker invalide le cache d'une layer dès que son contenu change, **et toutes les layers suivantes avec elle**. Copier `package.json` avant le reste du code fait que modifier un fichier source ne réinvalide pas `npm ci` (layer coûteuse) — seule la dernière `COPY . .` est refaite. Inverser l'ordre ferait réinstaller toutes les dépendances à chaque changement de code.

Le même raisonnement explique l'intérêt du fichier `.dockerignore` : tout ce qui est copié dans le contexte de construction peut invalider le cache et alourdir l'image. On y exclut les dépendances installées localement, le dossier `.git`, les secrets.

```
node_modules
npm-debug.log
.git
.env
.vscode
```

Les **builds multi-étapes** séparent la construction de l'exécution. Une première étape, avec tous les outils de compilation, produit le résultat ; une seconde, partant d'une image minimale, ne copie que ce résultat. L'image finale ne contient ni compilateur, ni dépendances de développement, ni code source, ce qui la rend plus légère et réduit sa surface d'attaque.

```dockerfile
# Étape de construction
FROM node:22 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Étape d'exécution
FROM node:22-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --omit=dev
USER node
CMD ["node", "dist/server.js"]
```

## Réseaux et volumes

Par défaut, un conteneur est branché sur un réseau **bridge** : un réseau virtuel privé sur l'hôte, d'où il sort par traduction d'adresses. Sur un réseau bridge créé par l'utilisateur, les conteneurs se trouvent par leur nom grâce au DNS interne de Docker, ce qui est la façon normale de relier une application à sa base de données. Le mode **host** supprime l'isolation réseau, le conteneur utilisant directement les interfaces de l'hôte ; le mode **none** le prive de réseau ; le mode **overlay** relie des conteneurs répartis sur plusieurs hôtes, dans Docker Swarm.

```bash
docker network create mon-reseau
docker run -d --network mon-reseau --name db postgres:16
docker run -d --network mon-reseau --name app mon-app:v1   # joint « db » par son nom
```

Puisqu'un conteneur est éphémère, les données qui doivent survivre vont dans un **volume**. Un volume nommé est géré par Docker, qui le stocke dans son propre répertoire : c'est la solution recommandée pour une base de données. Un *bind mount* monte un dossier précis de l'hôte dans le conteneur, pratique en développement pour voir ses modifications de code immédiatement. Un montage **tmpfs** vit en mémoire et disparaît à l'arrêt, utile pour des fichiers temporaires sensibles.

```bash
docker volume create mydata
docker run -v mydata:/data nginx                   # Volume nommé
docker run -v /host/path:/container/path nginx     # Bind mount
docker run --tmpfs /tmp nginx                      # En mémoire
```

## Plusieurs conteneurs : Docker Compose

Une application réelle comporte plusieurs services, un serveur web, une base de données, un cache. Plutôt que d'enchaîner des `docker run` interminables, **Docker Compose** les décrit dans un fichier YAML et les lance ensemble, avec leurs réseaux et volumes. Compose est aujourd'hui intégré à la commande `docker` (`docker compose`, en deux mots) ; l'ancien exécutable `docker-compose` et la clé `version:` en tête de fichier sont obsolètes.

```yaml
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_DB: mydb
    secrets:
      - db_password
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - app-network

secrets:
  db_password:
    file: ./db_password.txt

volumes:
  db-data:

networks:
  app-network:
```

```bash
docker compose up -d
docker compose logs -f
docker compose ps
docker compose down
```

Attention, `depends_on` garantit seulement l'ordre de démarrage, pas que la base soit prête à répondre : pour cela, il faut un *healthcheck* et la condition `service_healthy`.

## Sécuriser ses conteneurs

La première règle est de ne pas faire tourner l'application en root dans le conteneur, d'où l'instruction `USER` dans les exemples ci-dessus.

> [!warning] Pourquoi c'est important
> Un processus root dans le conteneur n'est isolé du root de l'hôte que par les namespaces — une faille de conteneur à hôte (container breakout) donne alors directement les pleins pouvoirs sur la machine hôte. Avec un utilisateur non-root, la même faille limite l'attaquant aux droits de cet utilisateur, même après l'évasion.

La deuxième est de réduire ce qui se trouve dans l'image : partir d'images minimales (Alpine, *distroless*), utiliser des builds multi-étapes, et n'installer que le nécessaire. Moins de paquets, c'est moins de vulnérabilités. Ces vulnérabilités se détectent en scannant les images avec un outil comme Trivy, Grype ou Docker Scout (`docker scout cves mon-image`), qui a remplacé l'ancienne commande `docker scan`.

La troisième concerne les secrets. Un mot de passe écrit dans un Dockerfile reste lisible dans les couches de l'image, même s'il est supprimé dans une étape suivante, et une variable d'environnement est visible par `docker inspect`. On préfère monter les secrets au moment de l'exécution, comme dans l'exemple Compose ci-dessus, ou utiliser les secrets de build de BuildKit (`RUN --mount=type=secret`).

On peut enfin durcir l'exécution elle-même : système de fichiers en lecture seule (`--read-only`), suppression de toutes les capacités Linux inutiles (`--cap-drop ALL`), interdiction d'en acquérir de nouvelles (`--security-opt no-new-privileges`), et limites de mémoire et de CPU (`--memory`, `--cpus`).

## Déboguer

Quand un conteneur se comporte mal, `docker logs` est le premier réflexe. `docker inspect` affiche toute sa configuration (réseau, montages, variables), `docker stats` sa consommation en temps réel, `docker top` ses processus et `docker events` le flux des événements du démon. `docker cp` copie des fichiers entre le conteneur et l'hôte.

```bash
docker inspect conteneur
docker stats
docker top conteneur
docker cp conteneur:/path/file /local/path
```

## Et après : l'orchestration

Docker gère des conteneurs sur une machine. Dès qu'il faut en faire tourner des centaines sur plusieurs serveurs, les redémarrer en cas de panne, répartir la charge et déployer sans interruption, il faut un orchestrateur : Docker Swarm, intégré à Docker et simple, ou surtout [[Kubernetes]], devenu le standard.

## Ressources

- [Documentation officielle de Docker](https://docs.docker.com), notamment le guide des bonnes pratiques pour écrire un Dockerfile.
- Play with Docker, un bac à sable en ligne pour s'exercer sans rien installer.
- Pour aller plus loin : BuildKit, les healthchecks, les limites de ressources, un registre privé.
