# Question 16 — LoadBalancer

## Notes d'apprentissage

Un *reverse proxy* reçoit les requêtes des clients et les transmet à un ou plusieurs serveurs en arrière-plan. Quand il répartit la charge entre plusieurs backends, on parle de *load balancer*. Nginx fait les deux.

**Modèle mental : reverse proxy vs load balancer.**

```
                 ┌──► backend (1 seul)        = reverse proxy
client ──► nginx ┤
                 └──► backend A / B / C ...    = load balancer (répartition)
```

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

**Pièges** :
- **Toujours `nginx -t`** avant `reload` : une faute de syntaxe empêche le rechargement et peut couper le service.
- Le slash final de `proxy_pass` change le comportement de réécriture de l'URI — attention à `/special`.
- Sur Debian, ne pas oublier le lien dans `sites-enabled/` ; un fichier dans `sites-available/` seul n'est pas chargé.
- Ne pas modifier la config des apps existantes (1111/2222) : le LB est une couche au-dessus.

## Énoncé

Solve this question on: `web-srv1`

Server `web-srv1` is hosting two applications, one accessible on port `1111` and one on `2222`. These are served using Nginx and it's **not** allowed to change their config. The ip of `web-srv1` is `192.168.10.60`.

Create a new HTTP LoadBalancer on that server which:
- Listens on port `8001` and redirects all traffic to `192.168.10.60:2222/special`
- Listens on port `8000` and balances traffic between `192.168.10.60:1111` and `192.168.10.60:2222` in a Random or Round Robin fashion
Nginx is already preinstalled and is recommended to be used for the implementation. Though it's also possible to use any other technologies (like Apache or HAProxy) because only the end result will be verified.

## Solution

First we check if everything works as claimed:
```bash
curl web-srv1:1111
app1
curl web-srv1:2222
app2
curl web-srv1:2222/special
app2 special
```

Cool, we can work with that! Here we're now going to create an Nginx LoadBalancer, but it would also be possible to use any other technology if you're more familiar with it.
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

There we see the two existing applications `app1` and `app2` which we aren't allowed to be changed. But we sure can use one as template for our new LoadBalancer:
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

We start slowly with the easier one on port `8001` where we simply use a `proxy_pass` option. Save the file and:
```bash
root@web-srv1:/etc/nginx/sites-available$ cd ../sites-enabled
root@web-srv1:/etc/nginx/sites-enabled$ ln -s ../sites-available/lb . # this is the nginx way for enabling
root@web-srv1:/etc/nginx/sites-enabled$ service nginx restart
root@web-srv1:/etc/nginx/sites-enabled$ curl localhost:8001           # our LB is reachable on port 8001
app2 special
```

Working! Now we go ahead and copy the first part, make some additions and use it as the second part:
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

The second part is mostly the same as before. It's possible to create multiple servers which listen on different ports within the same file. Here we simply created an `upstream backend` that contains the provided urls and we use it in the `proxy_pass` directive. Pretty nice right! But does it work?
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

Above we see that requests to `web-srv1:8000` are sent to both `app1` and `app2`. And requests on `web-srv1:8001` are only sent to `app2` and path `/special`.

