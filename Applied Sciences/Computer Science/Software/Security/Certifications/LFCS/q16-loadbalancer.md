---
title: "LFCS Q16 — Répartiteur de charge (LoadBalancer)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, loadbalancer]
date: "2026-08-09"
---

# Question 16 — Répartiteur de charge (LoadBalancer)

## Notes d'apprentissage

Un *reverse proxy* reçoit les requêtes des clients et les transmet à un ou plusieurs serveurs en arrière-plan. Quand il répartit la charge entre plusieurs backends, on parle de *load balancer*. Nginx fait les deux.

> [!tip] Modèle mental : reverse proxy vs load balancer
> ```
>                  ┌──► backend (1 seul)        = reverse proxy
> client ──► nginx ┤
>                  └──► backend A / B / C ...    = load balancer (répartition)
> ```

- **`proxy_pass`** vers une seule cible = simple transfert (étape « port 8001 → :2222/special »).
- **`upstream`** (groupe de serveurs) + `proxy_pass` vers ce groupe = répartition de charge (étape « port 8000 »).

**Squelette de configuration Nginx :**
```nginx
upstream backend_pool {
    # méthode de répartition (défaut = round robin)
    server 192.168.10.60:1111;
    server 192.168.10.60:2222;
}

server {
    listen 8000;
    location / {
        proxy_pass http://backend_pool;     # vers le groupe → répartition
    }
}

server {
    listen 8001;
    location / {
        proxy_pass http://192.168.10.60:2222/special;   # vers une cible unique
    }
}
```

**Algorithmes de répartition** (dans le bloc `upstream`) :
- **round robin** (défaut) : chaque serveur à tour de rôle.
- `least_conn;` : vers le serveur le moins chargé.
- `random;` : choix aléatoire.
- `ip_hash;` : même client → même serveur (sessions persistantes).

**Organisation des fichiers Nginx** (Debian) : on crée un fichier dans `/etc/nginx/sites-available/`, puis on l'active par un lien symbolique vers `/etc/nginx/sites-enabled/`.
```bash
ln -s /etc/nginx/sites-available/lb /etc/nginx/sites-enabled/
nginx -t                 # TESTER la config avant de recharger (indispensable)
systemctl reload nginx   # recharger sans coupure
```

> [!warning] Pièges
> - **Toujours `nginx -t`** avant `reload` : une faute de syntaxe empêche le rechargement et peut couper le service.
> - Le slash final de `proxy_pass` change le comportement de réécriture de l'URI — attention à `/special`.
> - Sur Debian, ne pas oublier le lien dans `sites-enabled/` ; un fichier dans `sites-available/` seul n'est pas chargé.
> - Ne pas modifier la config des apps existantes (1111/2222) : le LB est une couche au-dessus.

## Énoncé

Résolvez cette question sur : `web-srv1`

Le serveur `web-srv1` héberge deux applications, l'une accessible sur le port `1111` et l'autre sur `2222`. Elles sont servies par Nginx et il n'est **pas** permis de modifier leur configuration. L'IP de `web-srv1` est `192.168.10.60`.

Créez un nouveau répartiteur de charge HTTP sur ce serveur qui :
- écoute sur le port `8001` et redirige tout le trafic vers `192.168.10.60:2222/special`
- écoute sur le port `8000` et répartit le trafic entre `192.168.10.60:1111` et `192.168.10.60:2222` de façon aléatoire (Random) ou en Round Robin
Nginx est déjà préinstallé et il est recommandé de l'utiliser pour l'implémentation. Il reste toutefois possible d'utiliser d'autres technologies (comme Apache ou HAProxy), car seul le résultat final sera vérifié.

## Solution

Nous vérifions d'abord que tout fonctionne comme annoncé :
```bash
curl web-srv1:1111
app1
curl web-srv1:2222
app2
curl web-srv1:2222/special
app2 special
```

Parfait, nous pouvons travailler là-dessus ! Nous allons maintenant créer un répartiteur de charge Nginx, mais il serait également possible d'utiliser une autre technologie si vous la maîtrisez mieux.
```bash
candidate@terminal:~$ ssh web-srv1
root@web-srv1:~$ cd /etc/nginx/sites-available
root@web-srv1:/etc/nginx/sites-available$ ls -lh
total 2.0K
-rw-r--r-- 1 root root 329 Jun 14 17:17 app1
-rw-r--r-- 1 root root 413 Jun 14 17:17 app2
root@web-srv1:/etc/nginx/sites-available$ cat app1
server {
        listen 1111 default_server;
        listen [::]:1111 default_server;
        server_name _;
        location / {
                return 200 'app1\n';
        }
}
```

Nous y voyons les deux applications existantes `app1` et `app2`, que nous n'avons pas le droit de modifier. Mais nous pouvons bien sûr en utiliser une comme modèle pour notre nouveau répartiteur de charge :
```bash
root@web-srv1:/etc/nginx/sites-available$ cp app1 lb
root@web-srv1:/etc/nginx/sites-available$ vim lb
server {
        listen 8001 default_server;                           # change port
        listen [::]:8001 default_server;                      # change port
        server_name _;
        location / {
                proxy_pass http://192.168.10.60:2222/special; # reverse proxy to the requested url
        }
}
```

Nous commençons doucement avec le cas le plus simple sur le port `8001`, où nous utilisons simplement une option `proxy_pass`. Enregistrez le fichier puis :
```bash
root@web-srv1:/etc/nginx/sites-available$ cd ../sites-enabled
root@web-srv1:/etc/nginx/sites-enabled$ ln -s ../sites-available/lb . # this is the nginx way for enabling
root@web-srv1:/etc/nginx/sites-enabled$ service nginx restart
root@web-srv1:/etc/nginx/sites-enabled$ curl localhost:8001           # our LB is reachable on port 8001
app2 special
```

Ça fonctionne ! Nous copions maintenant la première partie, y ajoutons quelques éléments et l'utilisons comme seconde partie :
```bash
root@web-srv1:/etc/nginx/sites-enabled$ vim lb
### FIRST PART
server {
        listen 8001 default_server;
        listen [::]:8001 default_server;
        server_name _;
        location / {
                proxy_pass http://192.168.10.60:2222/special; # reverse proxy to the requested url
        }
}
### SECOND PART
upstream backend {
        # when no load balancing method is specified, Round Robin is used
        server 192.168.10.60:1111; # app1
        server 192.168.10.60:2222; # app2
}
server {
        listen 8000 default_server;
        listen [::]:8000 default_server;
        server_name _;
        location / {
                proxy_pass http://backend; # reverse proxy to the requested url
        }
}
```

La seconde partie est globalement identique à la précédente. Il est possible de créer plusieurs serveurs qui écoutent sur des ports différents dans un même fichier. Ici, nous avons simplement créé un `upstream backend` contenant les URL fournies et nous l'utilisons dans la directive `proxy_pass`. Plutôt pratique, non ! Mais est-ce que cela fonctionne ?
```bash
root@web-srv1:/etc/nginx/sites-enabled$ service nginx restart
root@web-srv1:/etc/nginx/sites-enabled$ exit
curl web-srv1:8000
app1
curl web-srv1:8000
app2
curl web-srv1:8000
app1
curl web-srv1:8000
app2
curl web-srv1:8000
app1
curl web-srv1:8001
app2 special
curl web-srv1:8001
app2 special
curl web-srv1:8001/anything/even/not/special
app2 special
```

Ci-dessus, nous voyons que les requêtes vers `web-srv1:8000` sont envoyées à la fois à `app1` et à `app2`. Et les requêtes sur `web-srv1:8001` ne sont envoyées qu'à `app2` et au chemin `/special`.

