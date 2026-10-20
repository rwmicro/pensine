---
title: "LFCS Q11 — Gestion de Docker"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, docker, management]
date: "2026-08-09"
---

# Question 11 — Gestion de Docker

## Notes d'apprentissage

Un conteneur est un processus isolé qui embarque ses propres dépendances. À la différence d'une VM, il **partage le noyau de l'hôte** — d'où sa légèreté et son démarrage instantané.

> [!tip] Modèle mental : les trois objets Docker
> ```
> Dockerfile  ──build──►  Image  ──run──►  Container
> (recette)               (modèle figé,    (instance vivante,
>                          en couches)      avec son état)
> ```

- **Dockerfile** : liste d'instructions pour construire une image.
- **Image** : artefact en lecture seule, empilé en *couches*, identifié par `nom:tag` (ex. `nginx:alpine`).
- **Container** : une exécution de l'image, avec sa propre couche d'écriture, son réseau, ses limites.

**Cycle de vie et inspection :**
```bash
docker ps              # conteneurs EN COURS (-a pour inclure les arrêtés)
docker stop NAME       # arrêt propre (SIGTERM puis SIGKILL)
docker start/restart NAME
docker logs NAME       # sortie du conteneur
docker inspect NAME    # TOUTES les métadonnées en JSON (IP, volumes, env...)
```
`docker inspect` est la mine d'or de cet exercice : IP, montages, variables. On cible un champ précis avec `--format` :
```bash
docker inspect -f '{{.NetworkSettings.IPAddress}}' frontend_v2
docker inspect -f '{{range .Mounts}}{{.Destination}}{{end}}' frontend_v2
```

**Lancer un conteneur, les options clées :**
```bash
docker run -d --name frontend_v3 --memory 30m -p 1234:80 nginx:alpine
           │   │                  │            │
           │   │                  │            └ -p HÔTE:CONTENEUR (mappage de port)
           │   │                  └ --memory limite de RAM
           │   └ --name nom du conteneur
           └ -d détaché (tourne en arrière-plan)
```

**Le sens de `-p HÔTE:CONTENEUR`** est une erreur fréquente : le port de gauche est celui exposé sur la machine hôte, celui de droite est le port à l'intérieur du conteneur. `-p 1234:80` = « le 1234 de l'hôte mène au 80 de nginx ».

**Volumes** : un conteneur est éphémère, sa couche d'écriture meurt avec lui. Un *volume* monte un stockage persistant à un chemin (`Destination`) dans le conteneur. `-v /hôte:/conteneur` ou volume nommé `-v nom:/conteneur`.

> [!warning] Pièges
> - `docker ps` ne montre pas les conteneurs arrêtés — ajouter `-a`.
> - Sans `-d`, le terminal reste attaché au conteneur.
> - Sans `--name`, Docker génère un nom aléatoire.
> - Inverser les ports de `-p` est l'erreur classique : hôte d'abord, conteneur ensuite.

## Énoncé

Résolvez cette question sur : `terminal`

Quelqu'un a entendu dire que vous êtes spécialiste de la conteneurisation, ce qui suit devrait donc être facile pour vous ! Veuillez :
1. Arrêter le conteneur Docker nommé `frontend_v1`
2. Rassembler les informations du conteneur Docker nommé `frontend_v2` :
    - Écrire l'adresse IP qui lui est attribuée dans `/opt/course/11/ip-address`
    - Il possède un montage de volume. Écrire le répertoire de destination de ce montage dans `/opt/course/11/mount-destination`
3. Démarrer un nouveau conteneur Docker détaché :
    - Nom : `frontend_v3`
    - Image : `nginx:alpine`
    - Limite de mémoire : `30m` (30 mégaoctets)
    - Mappage de port TCP : `1234/host` => `80/container`

## Solution

_Dockerfile_ : liste de commandes à partir desquelles une _Image_ peut être construite

_Image_ : fichier binaire qui contient toutes les données et prérequis nécessaires pour être exécuté en tant que _Container_

_Container_ : instance en cours d'exécution d'une _Image_

_Registry_ : endroit où l'on peut pousser ou récupérer des _Images_

Nous listons d'abord tous les conteneurs Docker :
```bash
sudo docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS     NAMES
a9b334cfaae0   nginx:alpine   "/docker-entrypoint.…"   11 minutes ago   Up 11 minutes   80/tcp    frontend_v1
e68fa28f231d   nginx:alpine   "/docker-entrypoint.…"   7 minutes ago    Up 7 minutes    80/tcp    frontend_v2
```

### Étape 1
Pour la première étape, nous arrêtons le conteneur :
```bash
sudo docker stop frontend_v1
frontend_v1
sudo docker ps -a  # show also stopped containers using "ps -a"
CONTAINER ID   IMAGE          ...  CREATED          STATUS                      PORTS     NAMES
e68fa28f231d   nginx:alpine   ...  8 minutes ago    Up 8 minutes                80/tcp    frontend_v2
a9b334cfaae0   nginx:alpine   ...  13 minutes ago   Exited (0) 45 seconds ago             frontend_v1
```

### Étape 2
`docker inspect` fournit la configuration du conteneur au format JSON, qui contient toutes les informations demandées dans cette tâche :
```bash
sudo docker inspect frontend_v2
        "Mounts": [
            {
                "Type": "bind",
                "Source": "/var/www",
                "Destination": "/srv",                 # WE NEED THIS
                "Mode": "",
                "RW": true,
                "Propagation": "rprivate"
            }
        ],
...
        "NetworkSettings": {
            "Bridge": "",
            "SandboxID": "a550576248b3f6c15211c2ad10efc421c7b48285cd69d57b64d8dc7b1b59e0ef",
            "HairpinMode": false,
...
            "Networks": {
                "bridge": {
                    "IPAMConfig": null,
                    "Links": null,
                    "Aliases": null,
                    "NetworkID": "5889aae0b056e4f944d6fb9afd8edd26ecd589c5e45b7533b59c878138fb5625",
                    "EndpointID": "954fcc88c2b64ef9ba3809eb130060ceb064301c4906b4a7ab0902be6153eedb",
                    "Gateway": "172.17.0.1",
                    "IPAddress": "172.17.0.3",         # WE NEED THIS
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "MacAddress": "02:42:ac:11:00:03",
                    "DriverOpts": null
                }
            }
        }
```

C'est probablement une bonne idée de rechercher des valeurs précises dans la sortie de `inspect`. Pour cela, nous pouvons ouvrir directement la sortie dans vim :
```bash
sudo docker inspect frontend_v2 | vim -
```

Il ne nous reste plus qu'à créer les fichiers demandés avec leur contenu correct (l'adresse IP de votre conteneur peut différer) :
```bash
echo "172.17.0.3" > /opt/course/11/ip-address
echo "/srv" > /opt/course/11/mount-destination
```

Ce qui donne :
```bash
# /opt/course/11/ip-address
172.17.0.3
# /opt/course/11/mount-destination
/srv
```

### Étape 3
Nous pouvons enfin démarrer notre propre conteneur ! Malheureusement avec des conditions très strictes à respecter... alors obéissons !

La sortie de l'aide de `docker run` fournit généralement tout ce qui est nécessaire :
```bash
sudo docker run --help
Usage:  docker run [OPTIONS] IMAGE [COMMAND] [ARG...]      # the order of arguments is important
```

Run a command in a new container

Options:

      --add-host list                  Add a custom host-to-IP mapping (host:ip)

  -a, --attach list                    Attach to STDIN, STDOUT or STDERR

...

      --cpus decimal                   Number of CPUs

      --cpuset-cpus string             CPUs in which to allow execution (0-3, 0,1)

      --cpuset-mems string             MEMs in which to allow execution (0-3, 0,1)

  -d, --detach                         Run container in background and print container ID    # need this

      --detach-keys string             Override the key sequence for detaching a container

      --device list                    Add a host device to the container

      --device-cgroup-rule list        Add a rule to the cgroup allowed devices list

...

      --mount mount                    Attach a filesystem mount to the container

      --name string                    Assign a name to the container                        # need this

      --network network                Connect a container to a network

...

      --pids-limit int                 Tune container pids limit (set -1 for unlimited)

      --platform string                Set platform if server is multi-platform capable

      --privileged                     Give extended privileges to this container

  -p, --publish list                   Publish a containers port(s) to the host              # need this

  -P, --publish-all                    Publish all exposed ports to random ports

...

Avec cela, nous pouvons construire la commande de lancement nécessaire :
```bash
sudo docker run -d --name frontend_v3 --memory 30m -p 1234:80 nginx:alpine
1e7d4612df4aff82c96d2c65102966561038ebfb94a996c86afebf6e3cb1432a
```

Si la commande ci-dessus renvoie des erreurs iptables, nous pouvons redémarrer le service docker :
```bash
sudo docker rm --force frontend_v3 # delete existing container
sudo service docker restart        # restart docker servier
```

Grâce au mappage de port, nous devrions maintenant pouvoir faire :
```bash
curl localhost:1234
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>
<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>
<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```

[← Question 10](q10-sshfs-and-nfs.md) · [Index](notes.md) · [Question 12 →](q12-git-workflow.md)
