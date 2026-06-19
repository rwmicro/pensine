# Question 17 — OpenSSH Configuration

## Notes d'apprentissage

OpenSSH est la porte d'entrée distante de la quasi-totalité des serveurs Linux. Durcir sa configuration (`sshd`) est un classique de l'administration sécurisée.

**Modèle mental : client vs serveur — ne pas confondre les fichiers.**

| Fichier | Rôle |
|---|---|
| `/etc/ssh/sshd_config` | configuration du **serveur** (le démon `sshd`) |
| `/etc/ssh/sshd_config.d/*.conf` | fragments de conf serveur (drop-in, recommandés) |
| `/etc/ssh/ssh_config` + `~/.ssh/config` | configuration du **client** ssh |

Le `d` de `sshd` = *daemon* = le serveur. Une faute fréquente est d'éditer `ssh_config` (client) en pensant configurer le serveur.

**Privilégier les drop-in.** Plutôt que d'éditer le gros `sshd_config`, déposer un fichier dans `/etc/ssh/sshd_config.d/` : plus propre, survit aux mises à jour du paquet. (Encore faut-il que `sshd_config` contienne `Include /etc/ssh/sshd_config.d/*.conf`.)

**Directives de durcissement courantes :**
```sshd-config
X11Forwarding no              # pas de transfert d'affichage graphique
PasswordAuthentication no     # forcer l'authentification par clé
PermitRootLogin no            # interdire la connexion directe en root
Banner /etc/ssh/sshd-banner   # message affiché avant connexion
```

**Appliquer une règle à certains utilisateurs : les blocs `Match`.** C'est le mécanisme pour « désactiver les mots de passe sauf pour marta ». Les directives sous un `Match` ne s'appliquent qu'aux sessions correspondantes :
```sshd-config
PasswordAuthentication no          # règle globale par défaut
Match User marta
    PasswordAuthentication yes     # exception pour marta

Match User marta,cilla
    Banner /etc/ssh/sshd-banner    # bannière seulement pour ces deux-là
```

**Tester AVANT de redémarrer — la règle d'or :**
```bash
sshd -t                        # valider la syntaxe (rien = OK)
sshd -T | grep -i x11forwarding   # afficher la config EFFECTIVE résolue
systemctl reload ssh           # appliquer
```

**Pièges** :
- Une erreur dans `sshd_config` + un `restart` = **plus aucun accès SSH**. Toujours `sshd -t` d'abord, garder une session ouverte, et un accès console de secours (`lxc exec`).
- Les blocs `Match` s'étendent jusqu'au prochain `Match` ou la fin du fichier — l'indentation est cosmétique, c'est la position qui compte.
- Après changement : `reload` suffit (plus doux que `restart`) ; les sessions en cours ne sont pas coupées.
- `sshd -T` montre la config réellement appliquée, utile pour confirmer qu'un drop-in a bien été pris en compte.

## Énoncé

Solve this question on: `data-002`

You need to perform OpenSSH server configuration changes on `data-002`. Users `marta` and `cilla` exist on that server and can be used for testing. Passwords are their username and shouldn't be changed. Please go ahead and:
1. Disable `X11Forwarding`
2. Disable `PasswordAuthentication` for everyone but user `marta`
3. Enable `Banner` with file `/etc/ssh/sshd-banner` for users `marta` and `cilla`

> In case of misconfiguration you can still access the instance using `sudo lxc exec data-002 bash`

## Solution

### Step 1
We are required to perform ssh server config changes, always fun because nothing can ever go wrong!

We're doing a simple one first:
```bash
ssh data-002
root@data-002:~# sshd -T | grep -i X11Forwarding
x11forwarding yes
root@data-002:~$ vim /etc/ssh/sshd_config.d/custom.conf
X11Forwarding no
```

We could also edit `/etc/ssh/sshd_config` directly, but it is probably cleaner to override via drop-in config files. We can verify if the config change is accepted before restart:
```bash
root@data-002:~# sshd -T | grep -i X11Forwarding
x11forwarding no
```

Now we can restart the ssh service:
```bash
root@data-002:~$ service ssh restart # no error output means good
```

**Step 2+3**

We now need to first disable `PasswordAuthentication` globally and then enable it for user `marta`. Then we also add the `Banner` settings for users `marta` and `cilla`:
```bash
root@data-002:~$ vim /etc/ssh/sshd_config.d/custom.conf
X11Forwarding no
PasswordAuthentication no
Match User marta
  PasswordAuthentication yes
  Banner /etc/ssh/sshd-banner
Match User cilla
  Banner /etc/ssh/sshd-banner
```

Using `Match User` or `Match Group` we can override global settings for specific users and groups.

It's **very important** to add any `Match` lines at the very bottom of the `/etc/ssh/sshd_config` config file because all following lines are considered part of that block until another `Match` or the end of the file.

If drop-in configuration files are used, such as in `/etc/ssh/sshd_config.d/`, this rule still applies because all files are loaded in lexical (alphabetical) order.

Therefore, if you have multiple drop-in files and want to include `Match` directives safely, one reliable approach is to create a file named something like `sshd_config.d/99-match-users.conf` to ensure it will be read last.

We can verify our settings:
```bash
root@data-002:~# sshd -T | grep banner
debianbanner yes
banner none
root@data-002:~# sshd -T -C user=marta | grep banner
debianbanner yes
banner /etc/ssh/sshd-banner
root@data-002:~# sshd -T -C user=cilla | grep banner
debianbanner yes
banner /etc/ssh/sshd-banner
root@data-002:~# sshd -T -C user=root | grep banner
debianbanner yes
banner none
```

This looks great. Let's test if it works:
```bash
root@data-002:~$ service ssh restart
root@data-002:~$ exit
ssh marta@data-002
Hello our favorite user!
marta@data-002's password:
Last login: Tue Nov  4 13:27:24 2025 from 192.168.10.1
```

User `marta` sees the banner message and can log in using password.
```bash
ssh cilla@data-002
Hello our favorite user!
cilla@data-002: Permission denied (publickey).
```

User `cilla` sees the banner message but cannot log in using password.
```bash
ssh root@data-002
Last login: Tue Nov  4 13:38:00 2025 from 192.168.10.1
```

User `root` can still log in and does not see the banner message.

