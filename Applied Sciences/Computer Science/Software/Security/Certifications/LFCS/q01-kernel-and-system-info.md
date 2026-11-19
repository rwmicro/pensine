---
title: "LFCS Q01 — Kernel and System Info"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, kernel, system, info]
date: "2026-08-09"
prerequis: ["[[Applied Sciences/Computer Science/Software/Security/Certifications/LFCS/notes]]"]
niveau: "Exploitation du système"
---

# Question 1 — Kernel and System Info

## Notes d'apprentissage

Interroger un système qu'on ne connaît pas est le premier réflexe de l'administrateur : version du noyau (pour savoir si une CVE s'applique ou si un module est compatible), paramètres du noyau actifs, et fuseau horaire (qui décale tous les logs).

**Le noyau et `uname`**. `uname` lit ses informations directement depuis le noyau en cours d'exécution. Les options à connaître :

```bash
uname -r     # release : 5.15.0-69-generic  (la version, celle qui compte pour les modules/CVE)
uname -a     # tout : noyau + hostname + architecture + date de build
uname -m     # architecture matérielle (x86_64, aarch64...)
```

> [!tip] Modèle mental : `/proc/sys` = les réglages vivants du noyau
> Tout ce qui est sous `/proc/sys/` est un paramètre du noyau modifiable à chaud. Chaque fichier = un réglage. Le chemin reflète la hiérarchie de `sysctl` : `net.ipv4.ip_forward` ↔ `/proc/sys/net/ipv4/ip_forward`.
>
> ```bash
> cat /proc/sys/net/ipv4/ip_forward   # lecture brute du fichier
> sysctl net.ipv4.ip_forward          # même valeur, via l'outil dédié
> ```

`ip_forward = 1` signifie que la machine route les paquets entre interfaces (comportement d'un routeur, pas d'un poste classique). Voir [[q25-sysctl-kernel-parameters]] pour rendre ces réglages persistants.

**Le fuseau horaire a plusieurs sources.** Il influence l'horodatage de tous les logs, d'où son importance.

```bash
date +%Z              # abréviation du fuseau actif (UTC, CEST...)
cat /etc/timezone     # fichier texte (Debian/Ubuntu)
timedatectl           # vue complète et moderne (systemd) — voir q03
```

> [!warning] Piège
> `/etc/timezone` est un fichier propre à Debian. Sur RHEL, le fuseau est le lien symbolique `/etc/localtime → /usr/share/zoneinfo/...`. `timedatectl` et `date +%Z` fonctionnent partout, à utiliser de préférence.

## Énoncé

Relevez trois informations système et écrivez chacune dans un fichier sous `~/lab/1/` :
1. la version (release) du noyau Linux dans `~/lab/1/kernel` ;
2. la valeur actuelle du paramètre noyau `ip_forward` dans `~/lab/1/ip_forward` ;
3. le fuseau horaire du système dans `~/lab/1/timezone`.

## Solution

```bash
# display kernel version
uname -r
# output value of kernel parameter
cat /proc/sys/net/ipv4/ip_forward
# get current timezone
date +%Z
cat /etc/timezone # also possible on some distro
```

The files should look like:
```bash
# ~/lab/1/kernel
5.15.0-69-generic
# ~/lab/1/ip_forward
1
# ~/lab/1/timezone
UTC
```
