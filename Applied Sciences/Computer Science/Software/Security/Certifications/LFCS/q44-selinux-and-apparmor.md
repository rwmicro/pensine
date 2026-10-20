---
title: "LFCS Q44 — SELinux et AppArmor (MAC)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, selinux, apparmor]
date: "2026-08-09"
---

# Question 44 — SELinux et AppArmor (MAC)

## Notes d'apprentissage

Le MAC (*Mandatory Access Control*) ajoute une couche de sécurité **au-dessus** des permissions Unix classiques. Différence fondamentale : même `root` est contraint par la politique. C'est ce qui limite les dégâts si un service est compromis.

> [!tip] Modèle mental : DAC vs MAC
> ```
> DAC (permissions Unix)        MAC (SELinux / AppArmor)
> le PROPRIÉTAIRE décide    +   une POLITIQUE système décide, root inclus
> (rwx, chmod)                  (un service compromis ne peut sortir de son bac à sable)
> ```

Le DAC répond « le propriétaire autorise-t-il ? » ; le MAC ajoute « la politique du système l'autorise-t-elle ? ». Les **deux** doivent dire oui.

**Deux implémentations, deux familles** (mutuellement exclusives en pratique) :

| | SELinux (RHEL) | AppArmor (Debian) |
|---|---|---|
| Approche | **étiquettes** (labels) sur fichiers/processus | **chemins** (profils par binaire) |
| Unité | contexte `user:role:type:level` | profil dans `/etc/apparmor.d/` |
| Voir l'état | `getenforce` / `sestatus` | `aa-status` |

**SELinux : tout est étiqueté.** Chaque fichier et processus porte un *contexte* ; le **type** est le cœur (« type enforcement ») : un processus en domaine `httpd_t` ne peut toucher que des fichiers `httpd_sys_content_t`. D'où le piège classique : déplacer le contenu web sans corriger l'étiquette → Apache refuse de servir.

**Les trois modes** (le réflexe de diagnostic) :
```
Enforcing   → bloque ET journalise les violations
Permissive  → journalise SEULEMENT (idéal pour debugger : "est-ce SELinux le coupable ?")
Disabled    → désactivé (changement vers/depuis exige un reboot)
```
Méthode type : un service ne démarre qu'en permissive → c'est SELinux ; lire l'AVC (`ausearch`/`sealert`) et corriger le **contexte** (`semanage fcontext` + `restorecon`) ou un **booléen** (`setsebool -P`).

**`chcon` vs `semanage`+`restorecon`** : `chcon` change un contexte *temporairement* (perdu au relabel) ; `semanage fcontext` enregistre la règle de façon *persistante*, appliquée par `restorecon`. Pour du durable, toujours le second.

**AppArmor : par chemin.** Chaque profil liste ce qu'un binaire précis peut faire. Deux modes : **enforce** (bloque) et **complain** (journalise seulement, équivalent du permissive ciblé). `aa-complain`/`aa-enforce` basculent un profil.

> [!warning] Pièges
> - Passer SELinux de `disabled` à `enforcing` déclenche un **relabel complet** au reboot (long).
> - Sans `-P`, `setsebool` est perdu au reboot.
> - `chcon` est écrasé par un `restorecon`/relabel — non persistant.
> - Ne pas confondre les outils selon la distrib — voir [[q45-rhel-vs-debian-equivalents]]. Lié au confinement des processus : seccomp/strace en [[q13-runtime-security-of-processes]].

## Énoncé

Résolvez cette question sur : `terminal`

Famille RHEL (`data-001`, SELinux) — tâches 1 à 5.
Famille Debian (`web-srv1`, AppArmor) — tâches 6 et 7.

1. Relevez le mode SELinux actuel et écrivez-le dans `/opt/course/44/mode`.
2. Passez SELinux en mode **permissive** pour la session courante sans redémarrer.
3. Configurez SELinux pour être en mode **enforcing** de façon persistante après redémarrage.
4. La racine web a été déplacée vers `/srv/www`. Définissez le contexte de fichier SELinux correct pour qu'Apache (`httpd`) puisse la servir.
5. Autorisez le service `httpd` à établir des connexions réseau sortantes en définissant le bon booléen SELinux de façon persistante.
6. (AppArmor) Listez tous les profils chargés et leur mode.
7. (AppArmor) Passez le profil `usr.sbin.tcpdump` en mode **complain**.

## Solution

Le Mandatory Access Control (MAC) ajoute une couche de politique **au-dessus** des permissions Unix standard : même root est contraint par la politique. RHEL/Fedora utilisent **SELinux** ; Debian/Ubuntu/SUSE utilisent **AppArmor**. Les deux sont mutuellement exclusifs en pratique — connaissez celui qui correspond à votre distribution d'examen.

## SELinux (famille RHEL)

SELinux étiquette chaque processus et chaque fichier avec un contexte `user:role:type:level`. Le **type** est ce qui compte le plus (type enforcement) : un processus s'exécutant dans le domaine `httpd_t` ne peut toucher que des fichiers étiquetés `httpd_sys_content_t`, etc.

### Étape 1 — Mode actuel

```bash
getenforce                          # Enforcing | Permissive | Disabled
sestatus                            # detailed: current + config-file mode
getenforce > /opt/course/44/mode
```

- **Enforcing** — les refus de la politique sont bloqués et journalisés.
- **Permissive** — les refus sont seulement journalisés (idéal pour le débogage).
- **Disabled** — SELinux complètement désactivé (un redémarrage est nécessaire pour en sortir ou y revenir).

### Étape 2 — Changer de mode pour la session courante

```bash
sudo setenforce 0                   # → Permissive
sudo setenforce 1                   # → Enforcing
```

Ce changement n'est **pas** persistant et ne permet pas de passer à `Disabled` ni d'en revenir.

### Étape 3 — Mode persistant

Éditez `/etc/selinux/config` :
```bash
SELINUX=enforcing                   # enforcing | permissive | disabled
```
Prend effet au prochain démarrage. Passer de `disabled` à `enforcing` déclenche un relabel complet du système de fichiers au redémarrage (ou forcez-le avec `sudo fixfiles -F onboot`).

### Étape 4 — Corriger un contexte de fichier

Le bon type pour le contenu web servi par Apache est `httpd_sys_content_t`. Ajoutez une règle persistante, puis appliquez-la :
```bash
# add the rule to the local policy (persists across relabels)
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/www(/.*)?'
# apply it to existing files now
sudo restorecon -Rv /srv/www
```

- `semanage fcontext -a` enregistre le mapping de façon permanente.
- `restorecon` réinitialise le contexte d'un fichier selon ce que la politique prévoit.
- `chcon -t httpd_sys_content_t -R /srv/www` le change **temporairement** — un relabel l'annulera. Préférez `semanage` + `restorecon` pour tout ce qui doit être persistant.
- Inspectez les contextes avec `ls -Z`, les processus avec `ps -eZ`.

Si `semanage` est absent : `sudo dnf install policycoreutils-python-utils`.

### Étape 5 — Booléens SELinux

Les booléens activent ou désactivent des comportements de politique prédéfinis sans écrire de politique personnalisée.
```bash
getsebool -a | grep httpd           # list httpd-related booleans
sudo setsebool -P httpd_can_network_connect on
```
`-P` le rend persistant au fil des redémarrages (écriture dans la politique). Sans `-P`, il revient à sa valeur précédente au redémarrage.

### Diagnostiquer les refus

```bash
sudo ausearch -m AVC -ts recent     # raw audit denials
sudo sealert -a /var/log/audit/audit.log   # human-readable, suggests fixes (setroubleshoot)
```
Un schéma classique en examen : un service ne démarre *que* lorsque SELinux est en enforcing → passez-le en permissive pour confirmer que c'est bien SELinux, puis lisez l'AVC et corrigez le contexte ou le booléen.

## AppArmor (famille Debian)

AppArmor est **basé sur les chemins** (et non sur les étiquettes) : chaque profil (sous `/etc/apparmor.d/`) liste les fichiers et capacités qu'un binaire précis peut utiliser. Les modes sont **enforce** (bloquer + journaliser) ou **complain** (journaliser seulement).

### Étape 6 — Lister les profils

```bash
sudo aa-status                      # or: sudo apparmor_status
```
Affiche combien de profils sont chargés, lesquels sont en mode enforce ou complain et à quels processus ils s'appliquent.

### Étape 7 — Passer un profil en mode complain

```bash
sudo aa-complain /usr/sbin/tcpdump          # complain (log only)
sudo aa-enforce /usr/sbin/tcpdump           # back to enforce
sudo aa-disable /usr/sbin/tcpdump           # unload + disable the profile
```
Les assistants se trouvent dans le paquet `apparmor-utils`. Les profils sont nommés d'après le chemin du binaire avec `/` → `.` (par exemple `usr.sbin.tcpdump`). Après avoir modifié un fichier de profil, rechargez-le :
```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.tcpdump
```

### Référence

| SELinux | AppArmor | Rôle |
|---|---|---|
| `getenforce` / `sestatus` | `aa-status` | afficher l'état actuel |
| `setenforce 0/1` | `aa-complain` / `aa-enforce` | changer de mode (par objet) |
| `/etc/selinux/config` | activer/désactiver par profil | mode persistant |
| `ls -Z`, `ps -eZ` | les profils listent les chemins de fichiers | inspecter les accès |
| `semanage` + `restorecon` | éditer `/etc/apparmor.d/` + `apparmor_parser -r` | ajuster la politique |
| `setsebool -P` | (n/a — éditer le profil) | activer/désactiver un comportement |
| `ausearch` / `sealert` | `dmesg` / `journalctl` | lire les refus |
