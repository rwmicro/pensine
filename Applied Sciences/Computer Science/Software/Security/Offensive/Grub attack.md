---
title: "Attaque via GRUB"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-04"
---

# Attaque via GRUB

GRUB (Grand Unified Bootloader) est le chargeur de démarrage de la plupart des systèmes Linux. Si GRUB n'est pas protégé par un mot de passe, un attaquant ayant accès physique à la machine peut compromettre le système entier.


## Pourquoi c'est dangereux

Si quelqu'un peut modifier les options de démarrage GRUB, il peut :
- Démarrer en **mode single-user** (root sans mot de passe)
- Modifier les paramètres du kernel pour **désactiver la sécurité**
- Monter le système de fichiers et **lire/modifier n'importe quel fichier**
- Réinitialiser le mot de passe root


## Types d'attaques courantes

### 1. Mode recovery / single user
En appuyant sur `e` dans GRUB au démarrage, on peut éditer la ligne de commande du kernel.

Ajouter `init=/bin/bash` ou `single` à la fin de la ligne kernel → accès root sans authentification.

```bash
# Ce qu'on modifie dans la ligne kernel :
linux /boot/vmlinuz-... root=/dev/sda1 ro quiet splash
# Devient :
linux /boot/vmlinuz-... root=/dev/sda1 rw init=/bin/bash
```

### 2. Live USB / CD
Démarrer sur un système externe pour monter le disque et accéder à tous les fichiers.

### 3. Modification de GRUB lui-même
Si le bootloader n'est pas protégé, on peut le remplacer par une version malveillante (bootkits).


## Protection

### Mettre un mot de passe sur GRUB

```bash
# Générer un hash du mot de passe
grub-mkpasswd-pbkdf2

# Ajouter dans /etc/grub.d/40_custom :
set superusers="admin"
password_pbkdf2 admin <hash_généré>

# Régénérer GRUB
update-grub
```

### Autres mesures
- **Désactiver le boot USB/CD** dans le BIOS et mettre un mot de passe BIOS/UEFI
- **Activer Secure Boot** (UEFI) pour vérifier l'intégrité du bootloader
- **Chiffrement disque** (LUKS) — même si on accède au disque, les données sont illisibles
- **TPM** (Trusted Platform Module) — lie le démarrage à la configuration matérielle


## Contexte

Cette attaque nécessite un **accès physique** à la machine. Elle est donc surtout pertinente pour :
- Serveurs dans des datacenters partagés
- Laptops volés
- Machines en environnement non sécurisé

Sur les systèmes cloud, l'hyperviseur protège généralement le bootloader.
