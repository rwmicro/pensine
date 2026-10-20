---
title: "LFCS Q17 — Configuration OpenSSH"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, openssh]
date: "2026-08-09"
---

# Question 17 — Configuration OpenSSH

## Notes d'apprentissage

OpenSSH est la porte d'entrée distante de la quasi-totalité des serveurs Linux. Durcir sa configuration (`sshd`) est un classique de l'administration sécurisée.

> [!tip] Modèle mental : client vs serveur — ne pas confondre les fichiers
> | Fichier | Rôle |
> |---|---|
> | `/etc/ssh/sshd_config` | configuration du **serveur** (le démon `sshd`) |
> | `/etc/ssh/sshd_config.d/*.conf` | fragments de conf serveur (drop-in, recommandés) |
> | `/etc/ssh/ssh_config` + `~/.ssh/config` | configuration du **client** ssh |

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

> [!warning] Pièges
> - Une erreur dans `sshd_config` + un `restart` = **plus aucun accès SSH**. Toujours `sshd -t` d'abord, garder une session ouverte, et un accès console de secours (`lxc exec`).
> - Les blocs `Match` s'étendent jusqu'au prochain `Match` ou la fin du fichier — l'indentation est cosmétique, c'est la position qui compte.
> - Après changement : `reload` suffit (plus doux que `restart`) ; les sessions en cours ne sont pas coupées.
> - `sshd -T` montre la config réellement appliquée, utile pour confirmer qu'un drop-in a bien été pris en compte.

## Énoncé

Résolvez cette question sur : `data-002`

Vous devez effectuer des modifications de configuration du serveur OpenSSH sur `data-002`. Les utilisateurs `marta` et `cilla` existent sur ce serveur et peuvent servir aux tests. Leur mot de passe est leur nom d'utilisateur et ne doit pas être changé. Veuillez donc :
1. Désactiver `X11Forwarding`
2. Désactiver `PasswordAuthentication` pour tout le monde sauf pour l'utilisateur `marta`
3. Activer `Banner` avec le fichier `/etc/ssh/sshd-banner` pour les utilisateurs `marta` et `cilla`

> En cas de mauvaise configuration, vous pouvez toujours accéder à l'instance avec `sudo lxc exec data-002 bash`

## Solution

### Étape 1
Nous devons effectuer des changements de configuration du serveur ssh, toujours amusant car rien ne peut jamais mal se passer !

Nous commençons par le cas simple :
```bash
ssh data-002
root@data-002:~# sshd -T | grep -i X11Forwarding
x11forwarding yes
root@data-002:~$ vim /etc/ssh/sshd_config.d/custom.conf
X11Forwarding no
```

Nous pourrions aussi éditer directement `/etc/ssh/sshd_config`, mais il est probablement plus propre de surcharger via des fichiers de configuration drop-in. Nous pouvons vérifier que le changement de configuration est accepté avant de redémarrer :
```bash
root@data-002:~# sshd -T | grep -i X11Forwarding
x11forwarding no
```

Nous pouvons maintenant redémarrer le service ssh :
```bash
root@data-002:~$ service ssh restart # no error output means good
```

**Étapes 2 et 3**

Nous devons maintenant d'abord désactiver `PasswordAuthentication` globalement, puis l'activer pour l'utilisateur `marta`. Ensuite, nous ajoutons également les réglages `Banner` pour les utilisateurs `marta` et `cilla` :
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

Avec `Match User` ou `Match Group`, nous pouvons surcharger les réglages globaux pour des utilisateurs et des groupes précis.

Il est **très important** de placer toutes les lignes `Match` tout en bas du fichier de configuration `/etc/ssh/sshd_config`, car toutes les lignes suivantes sont considérées comme faisant partie de ce bloc jusqu'à un autre `Match` ou la fin du fichier.

Si des fichiers de configuration drop-in sont utilisés, comme dans `/etc/ssh/sshd_config.d/`, cette règle s'applique toujours, car tous les fichiers sont chargés dans l'ordre lexical (alphabétique).

Par conséquent, si vous avez plusieurs fichiers drop-in et que vous voulez inclure des directives `Match` sans risque, une approche fiable consiste à créer un fichier nommé par exemple `sshd_config.d/99-match-users.conf` pour garantir qu'il sera lu en dernier.

Nous pouvons vérifier nos réglages :
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

Cela semble parfait. Testons si cela fonctionne :
```bash
root@data-002:~$ service ssh restart
root@data-002:~$ exit
ssh marta@data-002
Hello our favorite user!
marta@data-002's password:
Last login: Tue Nov  4 13:27:24 2025 from 192.168.10.1
```

L'utilisateur `marta` voit le message de bannière et peut se connecter avec un mot de passe.
```bash
ssh cilla@data-002
Hello our favorite user!
cilla@data-002: Permission denied (publickey).
```

L'utilisateur `cilla` voit le message de bannière mais ne peut pas se connecter avec un mot de passe.
```bash
ssh root@data-002
Last login: Tue Nov  4 13:38:00 2025 from 192.168.10.1
```

L'utilisateur `root` peut toujours se connecter et ne voit pas le message de bannière.

