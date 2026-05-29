# LFCS — Notes de préparation

> Notes formatées pour réviser la certification **Linux Foundation Certified System Administrator** via le simulateur [killer.sh](https://killer.sh/).

## Simulateur

### Serveurs disponibles

- `terminal` _(par défaut)_
- `web-srv1`
- `app-srv1`
- `data-001`
- `data-002`

### Règles du simulateur

1. Le serveur sur lequel résoudre une question est indiqué dans l'énoncé.
2. Si l'énoncé demande de créer des fichiers de solution dans `/opt/course/*`, **toujours le faire** sur le `terminal` principal.
3. Connexion à un serveur via ssh, par exemple `ssh web-srv1`.
4. Toutes les adresses sont configurées dans `/etc/hosts` sur chaque serveur.
5. Le ssh imbriqué n'est **pas possible** : on ne se connecte aux serveurs que depuis le `terminal` principal.
6. Impossible de redémarrer un serveur individuellement. En cas de problème, la seule solution est de redémarrer le simulateur complet via le menu *Restart Session*.
7. Ce simulateur ne couvre pas tous les sujets du programme officiel LFCS — les questions 21+ complètent le curriculum.

## Questions — simulateur killer.sh

| #   | Sujet                                                                                                   | Serveur    |
| --- | ------------------------------------------------------------------------------------------------------- | ---------- |
| 1   | [Kernel and System Info](q01-kernel-and-system-info.md)                                                 | `terminal` |
| 2   | [CronJobs](q02-cronjobs.md)                                                                             | `data-001` |
| 3   | [Time synchronisation Configuration](q03-time-synchronisation-configuration.md)                         | `terminal` |
| 4   | [Environment Variables](q04-environment-variables.md)                                                   | `terminal` |
| 5   | [Archives and Compression](q05-archives-and-compression.md)                                             | `data-001` |
| 6   | [User, Groups and Sudoers](q06-user-groups-and-sudoers.md)                                              | `app-srv1` |
| 7   | [Network Packet Filtering](q07-network-packet-filtering.md)                                             | `data-002` |
| 8   | [Disk Management](q08-disk-management.md)                                                               | `terminal` |
| 9   | [Find files with properties and perform actions](q09-find-files-with-properties-and-perform-actions.md) | `data-001` |
| 10  | [SSHFS and NFS](q10-sshfs-and-nfs.md)                                                                   | `terminal` |
| 11  | [Docker Management](q11-docker-management.md)                                                           | `terminal` |
| 12  | [Git Workflow](q12-git-workflow.md)                                                                     | `terminal` |
| 13  | [Runtime Security of processes](q13-runtime-security-of-processes.md)                                   | `web-srv1` |
| 14  | [Output redirection](q14-output-redirection.md)                                                         | `app-srv1` |
| 15  | [Build and install from source](q15-build-and-install-from-source.md)                                   | `app-srv1` |
| 16  | [LoadBalancer](q16-loadbalancer.md)                                                                     | `web-srv1` |
| 17  | [OpenSSH Configuration](q17-openssh-configuration.md)                                                   | `data-002` |
| 18  | [LVM Storage](q18-lvm-storage.md)                                                                       | `terminal` |
| 19  | [Regex, filter out log lines](q19-regex-filter-out-log-lines.md)                                        | `web-srv1` |
| 20  | [User and Group limits](q20-user-and-group-limits.md)                                                   | `web-srv1` |

## Questions complémentaires — curriculum officiel LFCS

Sujets du programme officiel non couverts par le simulateur. Énoncés inspirés de questions plausibles à l'examen.

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

Les notes ci-dessus utilisent majoritairement l'outillage Debian/Ubuntu (apt, iptables, systemd-timesyncd). L'examen LFCS laisse choisir la distribution : cette note rassemble les équivalents RHEL (chrony, firewalld, nftables, dnf, SELinux).

| # | Sujet |
|---|---|
| 45 | [RHEL vs Debian Equivalents](q45-rhel-vs-debian-equivalents.md) |
