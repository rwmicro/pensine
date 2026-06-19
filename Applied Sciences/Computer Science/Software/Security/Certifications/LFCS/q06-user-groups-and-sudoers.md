# Question 6 — User, Groups and Sudoers

## Notes d'apprentissage

La gestion des comptes repose sur trois fichiers et deux notions de groupe. C'est la base de la sécurité multi-utilisateurs.

**Les fichiers du système de comptes :**

| Fichier | Contenu | Lisible par |
|---|---|---|
| `/etc/passwd` | comptes : nom, UID, GID, home, shell | tous |
| `/etc/shadow` | hashes des mots de passe + politique d'expiration | root only |
| `/etc/group` | groupes et leurs membres | tous |

Format d'une ligne `/etc/passwd` :
```
user1:x:1001:1001::/home/accounts/user1:/bin/bash
  │   │  │    │   │         │              └ shell de login (/usr/sbin/nologin = pas de connexion)
  │   │  │    │   │         └ répertoire home
  │   │  │    │   └ GECOS (nom complet, optionnel)
  │   │  │    └ GID = groupe PRINCIPAL
  │   │  └ UID
  │   └ x = mot de passe dans /etc/shadow
  └ nom d'utilisateur
```

**Groupe principal vs groupes secondaires** — la distinction clé :
- **Principal** (champ GID de `/etc/passwd`) : un seul, c'est le groupe propriétaire des fichiers que l'utilisateur crée. Changé avec `usermod -g`.
- **Secondaires** (listés dans `/etc/group`) : autant qu'on veut, pour donner des droits supplémentaires. Définis avec `usermod -G` (remplace la liste) ou `usermod -aG` (**a**joute sans écraser — le `-a` est vital, l'oublier vide les autres groupes).

**Les commandes (préférer aux édits manuels) :**
```bash
useradd -m -d /home/x -s /bin/bash -g dev -G op user2   # créer (m=créer home)
usermod -g dev -d /home/x user1                         # modifier groupe principal + home
usermod -aG docker user1                                # AJOUTER un groupe secondaire
id user1 ; groups user1                                 # vérifier
```
Note : `adduser`/`addgroup` (Debian) sont des wrappers interactifs plus conviviaux ; `useradd`/`usermod` sont l'outillage portable et scriptable de l'examen.

**sudoers : déléguer des droits root finement.** La syntaxe d'une règle :
```
user2  ALL=(root) NOPASSWD: /bin/bash /root/dangerous.sh
  │     │    │       │             └ commande exacte autorisée (chemin absolu)
  │     │    │       └ sans demander de mot de passe
  │     │    └ peut s'exécuter en tant que (root)
  │     └ sur quelles machines (ALL)
  └ à qui s'applique la règle (un %nom = un groupe)
```

**Pièges** :
- **Toujours éditer sudoers avec `visudo`**, jamais avec `vim` : `visudo` valide la syntaxe avant d'enregistrer. Une faute dans `/etc/sudoers` peut bloquer tout accès root définitivement.
- Mieux que toucher `/etc/sudoers` : déposer un fichier dans `/etc/sudoers.d/` (`visudo -f /etc/sudoers.d/user2`).
- `usermod -G` **sans** `-a` retire l'utilisateur de tous ses autres groupes secondaires.
- Une règle sudoers doit pointer la commande **exactement** comme elle sera tapée (chemin absolu inclus), sinon elle ne s'applique pas.

## Énoncé

Solve this question on: `app-srv1`

On server `app-srv1`:
1. Change the primary group of user `user1` to `dev` and the home directory to `/home/accounts/user1`
2. Add a new user `user2` with groups `dev` and `op`, home directory `/home/accounts/user2`, terminal `/bin/bash`
3. User `user2` should be able to execute `sudo bash /root/dangerous.sh` without having to enter the root password

## Solution

### Step 1
We can use different approaches. We could:
```bash
ssh app-srv1
root@app-srv1:~$ usermod -d /home/accounts/user1 user1
```

Or we could edit `/etc/passwd` manually:
```bash
root@app-srv1:~$ vim /etc/passwd
root:x:0:0:root:/root:/bin/bash
...
lxd:x:999:100::/var/snap/lxd/common/lxd:/bin/false
ntp:x:113:121::/nonexistent:/usr/sbin/nologin
user1:x:1001:1001::/home/accounts/user1:/bin/bash # change path
```

No matter what solution, this should be correct:
```bash
root@app-srv1:~$ su user1
user1@app-srv1:/root$ cd
user1@app-srv1:~$ pwd
/home/accounts/user1
```

And to change the primary group:
```bash
root@app-srv1:~$ usermod -g dev user1
root@app-srv1:~$ groups user1
user1 : dev
```

### Step 2
First we can check available options:
```bash
root@app-srv1:~$ useradd -h
Usage: useradd [options] LOGIN
       useradd -D
       useradd -D [options]
Options:
      --badnames                do not check for bad names
  -b, --base-dir BASE_DIR       base directory for the home directory of the
                                new account
      --btrfs-subvolume-home    use BTRFS subvolume for home directory
  -c, --comment COMMENT         GECOS field of the new account
  -d, --home-dir HOME_DIR       home directory of the new account                           # useful
  -D, --defaults                print or change default useradd configuration
  -e, --expiredate EXPIRE_DATE  expiration date of the new account
  -f, --inactive INACTIVE       password inactivity period of the new account
  -g, --gid GROUP               name or ID of the primary group of the new
                                account
  -G, --groups GROUPS           list of supplementary groups of the new                     # useful
                                account
  -h, --help                    display this help message and exit
  -k, --skel SKEL_DIR           use this alternative skeleton directory
  -K, --key KEY=VALUE           override /etc/login.defs defaults
  -l, --no-log-init             do not add the user to the lastlog and
                                faillog databases
  -m, --create-home             create the users home directory                             # useful
  -M, --no-create-home          do not create the user's home directory
  -N, --no-user-group           do not create a group with the same name as
                                the user
  -o, --non-unique              allow to create users with duplicate
                                (non-unique) UID
  -p, --password PASSWORD       encrypted password of the new account
  -r, --system                  create a system account
  -R, --root CHROOT_DIR         directory to chroot into
  -P, --prefix PREFIX_DIR       prefix directory where are located the /etc/* files
  -s, --shell SHELL             login shell of the new account                              # useful
  -u, --uid UID                 user ID of the new account
  -U, --user-group              create a group with the same name as the user
  -Z, --selinux-user SEUSER     use a specific SEUSER for the SELinux user mapping
      --extrausers              Use the extra users database
```

Using the correct arguments we create the required new user:
```bash
root@app-srv1:~$ useradd -s /bin/bash -m -d /home/accounts/user2 -G dev,op user2
```

To verify that it was added to the required groups:
```bash
root@app-srv1:~$ cat /etc/group | grep user2
op:x:1003:user2
dev:x:1004:user2
user2:x:1005:
```

### Step 3
Now it's getting interesting. We can try to execute the script with current configuration:
```bash
root@app-srv1:~$ su user2
user2@app-srv1:/root$ cd
user2@app-srv1:~$ bash /root/dangerous.sh
bash: /root/dangerous.sh: Permission denied # DENIED
```

We need to configure sudoers to allow this specific script call. We should always edit the `/etc/sudoers` file using the command `visudo`, because it performs proper syntax validation before saving the file. Any misconfiguration of that file could lock us out of the system for good. So we do as root:
```bash
root@app-srv1:~$ visudo
...
# User privilege specification
root    ALL=(ALL:ALL) ALL
# Members of the admin group may gain root privileges
%admin ALL=(ALL) ALL
# Allow members of group sudo to execute any command
%sudo   ALL=(ALL:ALL) ALL
# See sudoers(5) for more information on "@include" directives:
@includedir /etc/sudoers.d
user2 ALL=(root) NOPASSWD: /bin/bash /root/dangerous.sh # ADD THIS
```

You can exit via `Ctrl + X`, then `Y` and then `Enter` to save.

And to verify:
```bash
user2@app-srv1:~$ sudo bash /root/dangerous.sh
Sun Jun 11 17:54:20 UTC 2023
dangerous
```
