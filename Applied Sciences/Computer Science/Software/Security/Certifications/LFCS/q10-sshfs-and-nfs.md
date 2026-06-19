# Question 10 — SSHFS and NFS

## Notes d'apprentissage

Monter un système de fichiers **distant** le fait apparaître comme un dossier local : les applications travaillent dessus sans savoir qu'il est sur une autre machine. Deux approches au programme, aux philosophies opposées.

**SSHFS vs NFS — le bon outil selon le contexte :**

| | SSHFS | NFS |
|---|---|---|
| Transport | par-dessus SSH (chiffré) | protocole dédié (port 2049) |
| Mise en place | côté **client** uniquement | serveur (`/etc/exports`) + client |
| Authentification | comptes SSH existants | basée sur l'IP/réseau |
| Usage typique | ponctuel, ad hoc, à travers Internet | partages permanents en LAN |
| Performance | correcte | élevée |

**SSHFS** réutilise une connexion SSH — rien à configurer côté serveur, juste un accès SSH valide.
```bash
sudo mkdir -p /app-srv1/data-export
sudo sshfs -o allow_other,rw app-srv1:/data-export /app-srv1/data-export
```
- `rw` : montage en lecture-écriture (`ro` = lecture seule).
- `allow_other` : autorise les **autres** utilisateurs que celui qui a monté à accéder au point de montage. Pratique, mais c'est un relâchement de sécurité (à éviter en production).

**NFS** se configure côté serveur via `/etc/exports`, une ligne par partage :
```
/nfs/share    192.168.10.0/24(ro,sync,no_subtree_check)
   │              │             └ options du partage
   │              └ qui peut monter (IP, réseau CIDR, ou hostname)
   └ répertoire exporté
```
Options clés : `ro`/`rw` (droits), `sync` (écritures confirmées sur disque, sûr), `root_squash` (par défaut : le root distant est mappé en `nobody` — sécurité ; `no_root_squash` désactive cette protection).

Après modification d'`/etc/exports`, **recharger** :
```bash
sudo exportfs -ra        # -r réexporte, -a tout
showmount -e             # vérifier ce qui est exporté
```
Côté client : créer le point de montage puis monter.
```bash
sudo mkdir -p /nfs/terminal/share
sudo mount terminal:/nfs/share /nfs/terminal/share
```

**Pièges** :
- Le point de montage local doit **exister** avant de monter (`mkdir -p`).
- Côté NFS, oublier `exportfs -ra` après avoir édité `/etc/exports` = le partage n'est pas pris en compte.
- Un export `ro` rend toute écriture impossible côté client (*Read-only file system*) — c'est le comportement attendu, pas un bug.
- Pour persister au reboot : ligne dans `/etc/fstab` (avec le type `nfs` ou `fuse.sshfs`).
- Debugger la connectivité NFS : `nc -v serveur 2049` vérifie que le port répond.

## Énoncé

Solve this question on: `terminal`

In this task it's required to access remote filesystems over network.

On your main server `terminal` use SSHFS to mount directory `/data-export` from server `app-srv1` to `/app-srv1/data-export`. The mount should be `read-write` and option `allow_other` should be enabled.

The NFS service has been installed on your main server `terminal`. Directory `/nfs/share` should be read-only accessible from `192.168.10.0/24`. On `app-srv1`, mount the NFS share `/nfs/share` to `/nfs/terminal/share`.

## Solution

**SSHFS**

We go ahead and create the SSHFS mount:
```bash
man sshfs # always helpful
sudo mkdir -p /app-srv1/data-export
sudo sshfs -o allow_other,rw app-srv1:/data-export /app-srv1/data-export
```

No errors but also no output, we further verify:
```bash
find /app-srv1/data-export
/app-srv1/data-export
/app-srv1/data-export/datRTG_1.gz
/app-srv1/data-export/datRTG_2.gz
touch /app-srv1/data-export/new
find /app-srv1/data-export
/app-srv1/data-export
/app-srv1/data-export/new
/app-srv1/data-export/datRTG_1.gz
/app-srv1/data-export/datRTG_2.gz
ssh app-srv1 find /data-export
/data-export
/data-export/new
/data-export/datRTG_1.gz
/data-export/datRTG_2.gz
```

Above we can see that creating a new file works and that both directories are synced. Note that all users can now access that mount in read-write mode because of option allow_other, which might not be something we want in production environments!

**NFS Server**

We could start by verifying the service runs without issues:
```bash
service --help                     # how to list all services?
Usage: service < option > | --status-all | [ service_name [ command | --full-restart ] ]
service --status-all | grep nfs    # find nfs service
 [ - ]  nfs-common
 [ + ]  nfs-kernel-server
service nfs-kernel-server status   # check nfs service status
● nfs-server.service - NFS server and services
     Loaded: loaded (/lib/systemd/system/nfs-server.service; enabled; vendor preset: enabled)
```

     Active: active (exited) since Thu 2023-06-15 15:09:18 UTC; 18min ago

   Main PID: 25267 (code=exited, status=0/SUCCESS)

        CPU: 8ms

NFS server seems to be running. We can expose certain directories via `/etc/exports`:
```bash
sudo vim /etc/exports
# /etc/exports: the access control list for filesystems which may be exported
#               to NFS clients.  See exports(5).
#
# Example for NFSv2 and NFSv3:
# /srv/homes       hostname1(rw,sync,no_subtree_check) hostname2(ro,sync,no_subtree_check)
#
# Example for NFSv4:
# /srv/nfs4        gss/krb5i(rw,sync,fsid=0,crossmnt,no_subtree_check)
# /srv/nfs4/homes  gss/krb5i(rw,sync,no_subtree_check)
#
/nfs/share            192.168.10.0/24(ro,sync,no_subtree_check,no_root_squash)
```

The file provides some comments with examples which can be very useful. After adding the exports we need to run:
```bash
man exportfs # in case we forget the arguments: "-r" for reexport and "-a" for all
sudo exportfs -ra
showmount -e
Export list for terminal:
/nfs/share       192.168.10.0/24
```

**NFS Client**

Now we check if our NFS server-side settings can actually be accessed on client-side by NFS mounting:
```bash
ssh app-srv1
root@app-srv1:~$ nc -v terminal 2049 # for debugging we check can if NFS on port 2049 is open
```

Connection to terminal (192.168.100.2) 2049 port [tcp/nfs] succeeded!

^C
```bash
root@app-srv1:~$ mkdir -p /nfs/terminal/share # we need to create the local mount destination directory
root@app-srv1:~$ mount terminal:/nfs/share /nfs/terminal/share # mount the remote NFS export
root@app-srv1:~$ find /nfs/terminal/share # view existing files
/nfs/terminal/share
/nfs/terminal/share/2.log
/nfs/terminal/share/3.log
/nfs/terminal/share/1.log
root@app-srv1:~$ touch /nfs/terminal/share/new # not possible to create new file (because of read-only)
touch: cannot touch '/nfs/terminal/share/new': Read-only file system
```

Above we see that we were able to mount the required NFS export in read-only mode on `app-srv1`.