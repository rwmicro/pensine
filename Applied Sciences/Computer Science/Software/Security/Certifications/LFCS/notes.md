---
title: "LFCS — Notes de préparation"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification]
date: "2026-08-09"
prerequis: ["[[Bash — Scripts et Automatisation]]", "[[Démarrage et Bootloader]]", "[[Système de Fichiers]]"]
---

# LFCS — Notes de préparation

> Notes de révision pour la certification **Linux Foundation Certified System Administrator** (LFCS) : pour chaque sujet du programme, les notions à comprendre, un exercice pratique et sa solution commentée.

## Comment utiliser ces exercices

Les exercices se font sur des machines de test : des VM ou des conteneurs jetables (Vagrant, LXD, KVM…), jamais sur une machine dont on a besoin. Certains supposent un petit réseau de plusieurs hôtes, aux noms génériques (`client`, `web01`, `app01`, `data01`, `data02`) : il suffit de les déclarer dans `/etc/hosts`.

Quand un énoncé demande d'écrire une réponse dans un fichier, il s'agit de `~/lab/<numéro>/…` : créer le dossier avec `mkdir -p` avant de commencer.

> [!warning] Piège
> Avant toute commande qui peut couper l'accès à une machine distante (modification du pare-feu, du réseau ou de `sshd`), gardez une session ouverte et un accès console de secours, et validez la configuration (`sshd -t`, `nft -c`, `nginx -t`…) avant de redémarrer le service. Sur une VM, un instantané pris avant l'exercice permet de revenir en arrière.

## Exercices pratiques

| #   | Sujet                                                                                                   |
| --- | ------------------------------------------------------------------------------------------------------- |
| 1   | [Kernel and System Info](q01-kernel-and-system-info.md)                                                 |
| 2   | [CronJobs](q02-cronjobs.md)                                                                             |
| 3   | [Time synchronisation Configuration](q03-time-synchronisation-configuration.md)                         |
| 4   | [Environment Variables](q04-environment-variables.md)                                                   |
| 5   | [Archives and Compression](q05-archives-and-compression.md)                                             |
| 6   | [User, Groups and Sudoers](q06-user-groups-and-sudoers.md)                                              |
| 7   | [Network Packet Filtering](q07-network-packet-filtering.md)                                             |
| 8   | [Disk Management](q08-disk-management.md)                                                               |
| 9   | [Find files with properties and perform actions](q09-find-files-with-properties-and-perform-actions.md) |
| 10  | [SSHFS and NFS](q10-sshfs-and-nfs.md)                                                                   |
| 11  | [Docker Management](q11-docker-management.md)                                                           |
| 12  | [Git Workflow](q12-git-workflow.md)                                                                     |
| 13  | [Runtime Security of processes](q13-runtime-security-of-processes.md)                                   |
| 14  | [Output redirection](q14-output-redirection.md)                                                         |
| 15  | [Build and install from source](q15-build-and-install-from-source.md)                                   |
| 16  | [LoadBalancer](q16-loadbalancer.md)                                                                     |
| 17  | [OpenSSH Configuration](q17-openssh-configuration.md)                                                   |
| 18  | [LVM Storage](q18-lvm-storage.md)                                                                       |
| 19  | [Regex, filter out log lines](q19-regex-filter-out-log-lines.md)                                        |
| 20  | [User and Group limits](q20-user-and-group-limits.md)                                                   |

## Autres sujets du programme LFCS

Les exercices suivants couvrent le reste du programme officiel, regroupés par domaine.

### Operation of Running Systems

| # | Sujet |
|---|---|
| 21 | [GRUB and Bootloader](q21-grub-bootloader.md) |
| 22 | [Systemd Targets and Services](q22-systemd-targets-and-services.md) |
| 23 | [Process Management](q23-process-management.md) |
| 24 | [System Logs](q24-system-logs.md) |
| 25 | [Sysctl Kernel Parameters](q25-sysctl-kernel-parameters.md) |
| 26 | [Package Management](q26-package-management.md) |
| 27 | [Bash Scripting](q27-bash-scripting.md) |
| 43 | [Kernel Modules](q43-kernel-modules.md) |

### Essential Commands & Users

| # | Sujet |
|---|---|
| 28 | [Permissions, SUID/SGID and ACL](q28-permissions-and-acl.md) |
| 29 | [Links and File Attributes](q29-links-and-file-attributes.md) |
| 30 | [PAM Configuration](q30-pam-configuration.md) |
| 44 | [SELinux and AppArmor (MAC)](q44-selinux-and-apparmor.md) |

### Networking

| # | Sujet |
|---|---|
| 31 | [Network Configuration](q31-network-configuration.md) |
| 32 | [Bonding and Bridges](q32-bonding-and-bridges.md) |

### Service Configuration

| # | Sujet |
|---|---|
| 33 | [DNS Server](q33-dns-server.md) |
| 34 | [Apache HTTP Server](q34-apache-http-server.md) |
| 35 | [Database Server](q35-database-server.md) |
| 36 | [HTTP Proxy](q36-http-proxy.md) |
| 37 | [Mail Aliases and Postfix](q37-mail-aliases-and-postfix.md) |
| 38 | [KVM Virtualization](q38-kvm-virtualization.md) |

### Storage Management

| # | Sujet |
|---|---|
| 39 | [LUKS Encrypted Storage](q39-luks-encrypted-storage.md) |
| 40 | [Swap Configuration](q40-swap-configuration.md) |
| 41 | [Software RAID with mdadm](q41-raid-mdadm.md) |
| 42 | [Disk Quotas](q42-disk-quotas.md) |

### Distribution differences

Les notes ci-dessus utilisent majoritairement l'outillage Debian/Ubuntu (apt, iptables, systemd-timesyncd). Depuis sa mise à jour, l'examen LFCS ne fait plus choisir de distribution (il se veut indépendant de la distribution) : connaître les deux familles reste utile au quotidien, et cette note rassemble les équivalents RHEL (chrony, firewalld, nftables, dnf, SELinux).

> [!tip] Méthode
> Plutôt que d'apprendre deux jeux de commandes en parallèle, repérer d'abord les outils communs aux deux familles (`systemctl`, `ip`, `mount`, `timedatectl`) — ils marchent à l'identique partout et couvrent une bonne partie de l'examen. Ne mémoriser les équivalents spécifiques (table ci-dessous) que pour ce qui reste vraiment distro-dépendant.

| # | Sujet |
|---|---|
| 45 | [RHEL vs Debian Equivalents](q45-rhel-vs-debian-equivalents.md) |

## Questions de révision

> [!quiz] Quelles précautions prendre avant de modifier le pare-feu ou `sshd` d'une machine distante ?
> Garder une session ouverte et un accès console de secours, et valider la configuration (`sshd -t`, `nft -c`…) avant de redémarrer le service, pour ne pas se retrouver enfermé dehors.

> [!quiz] Où réaliser ces exercices, et pourquoi ?
> Sur des VM ou des conteneurs jetables, idéalement avec un instantané pris avant : plusieurs exercices modifient le réseau, les disques ou le démarrage, et une erreur doit pouvoir s'annuler sans conséquence.

> [!quiz] Quels outils fonctionnent à l'identique sur les familles Debian/Ubuntu et RHEL, et sont donc à maîtriser en priorité ?
> Les outils communs comme `systemctl`, `ip`, `mount` et `timedatectl`.

> [!quiz] Donnez les équivalents RHEL de `apt` et de `systemd-timesyncd` cités dans la note.
> `dnf` pour la gestion des paquets et `chrony` pour la synchronisation de l'heure.
