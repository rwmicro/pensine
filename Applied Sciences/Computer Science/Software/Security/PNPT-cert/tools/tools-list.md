---
title: "Outils PNPT — Catalogue par phase"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, outils, pnpt]
date: "2026-05-18"
---

# Outils pour la PNPT

Catalogue des outils à connaître, classés par phase de l'engagement. Référence rapide — pour le détail d'utilisation, voir les notes thématiques (01–20). À l'examen, mieux vaut maîtriser un outil de chaque catégorie que d'en connaître dix superficiellement.

## Reconnaissance & OSINT

| Outil          | Usage                                |
|----------------|--------------------------------------|
| theHarvester   | Collecte d'emails, sous-domaines     |
| Sublist3r      | Énumération de sous-domaines         |
| Amass          | Énumération avancée (passif + actif) |
| crt.sh         | Sous-domaines via certificats SSL    |
| Sherlock       | Recherche de comptes par username    |
| Recon-ng       | Framework OSINT modulaire            |
| linkedin2username | Génération de wordlists depuis LinkedIn |
| Shodan / Censys | Recherche d'infrastructures exposées |

## Scanning & Énumération

| Outil          | Usage                                |
|----------------|--------------------------------------|
| Nmap           | Scan de ports et services            |
| Masscan        | Scan ultra-rapide (rapide mais bruyant) |
| enum4linux-ng  | Énumération SMB/NetBIOS              |
| smbclient      | Client SMB                           |
| smbmap         | Cartographie SMB                     |
| rpcclient      | Client RPC (null session)            |
| ldapsearch     | Requêtes LDAP                        |
| windapsearch   | Énumération AD via LDAP              |
| dnsenum / dnsrecon | Énumération DNS                  |

## Web

| Outil          | Usage                                |
|----------------|--------------------------------------|
| Gobuster       | Brute force directories / DNS / vhost|
| Feroxbuster    | Brute force directories (récursif)   |
| ffuf           | Fuzzer rapide                        |
| Nikto          | Scan de vulnérabilités web           |
| Burp Suite     | Proxy d'interception                 |
| Nuclei         | Scan automatisé de CVE / templates   |
| wfuzz          | Fuzzing web                          |
| sqlmap         | Exploitation SQL injection           |
| jwt_tool       | Manipulation JWT                     |

## Exploitation

| Outil          | Usage                                |
|----------------|--------------------------------------|
| Metasploit     | Framework d'exploitation             |
| msfvenom       | Génération de payloads               |
| searchsploit   | Recherche d'exploits (ExploitDB)     |
| CVE PoCs (GitHub) | Exploits version-spécifiques      |

## Post-Exploitation

| Outil          | Usage                                |
|----------------|--------------------------------------|
| Mimikatz       | Dump credentials Windows             |
| BloodHound     | Cartographie AD (graphe d'attaque)   |
| SharpHound     | Collecteur pour BloodHound (Windows) |
| bloodhound-python | Collecteur depuis Linux           |
| PowerView      | Énumération AD (PowerShell)          |
| Rubeus         | Attaques Kerberos (Windows)          |
| Mimikatz       | Dump creds + DCSync + Golden Ticket  |

## Cracking

| Outil          | Usage                                |
|----------------|--------------------------------------|
| Hashcat        | Cracking de hashes (GPU)             |
| John the Ripper| Cracking de hashes (CPU + variantes) |
| Hydra          | Brute force en ligne                 |
| medusa         | Alternative à Hydra                  |

## Impacket Suite

| Outil           | Usage                               |
|-----------------|-------------------------------------|
| psexec.py       | Exécution distante (SMB)            |
| wmiexec.py      | Exécution distante (WMI)            |
| smbexec.py      | Exécution distante (SMB, autre)     |
| secretsdump.py  | Dump de credentials (local + DCSync) |
| GetUserSPNs.py  | Kerberoasting                       |
| GetNPUsers.py   | AS-REP Roasting                     |
| ntlmrelayx.py   | Relay NTLM                          |
| ticketer.py     | Création de tickets Kerberos (Golden/Silver) |
| addcomputer.py  | Créer un compte machine             |
| rbcd.py         | Configurer RBCD                     |
| getST.py        | S4U2Self/Proxy depuis Linux         |

## Privilege Escalation

| Outil                     | Usage                          |
|---------------------------|--------------------------------|
| LinPEAS                   | Énumération privesc Linux      |
| WinPEAS                   | Énumération privesc Windows    |
| PowerUp                   | Privesc Windows (PowerShell)   |
| linux-exploit-suggester   | Suggestions kernel exploits    |
| Seatbelt                  | Énumération sécurité Windows   |
| PrintSpoofer              | Potato attack (SeImpersonate)  |
| GodPotato                 | Potato moderne (Win10/11/Server) |
| JuicyPotatoNG             | Variante pour Server 2016/2019/2022 |
| GTFOBins (web)            | Référence privesc binaires Linux |

## Pivoting

| Outil          | Usage                                |
|----------------|--------------------------------------|
| Chisel         | Tunneling TCP / SOCKS                |
| Ligolo-ng      | Tunneling avancé (interface réseau)  |
| sshuttle       | VPN over SSH                         |
| Proxychains    | Routage via proxy SOCKS              |
| socat          | Relais TCP polyvalent                |

## Networking offensif

| Outil          | Usage                                |
|----------------|--------------------------------------|
| Responder      | LLMNR / NBT-NS poisoning             |
| mitm6          | IPv6 DNS takeover                    |
| CrackMapExec / NetExec | Swiss army knife AD         |
| Evil-WinRM     | Shell WinRM                          |
| Inveigh        | Équivalent Responder pour Windows    |

## AD avancé

| Outil           | Usage                                       |
|-----------------|---------------------------------------------|
| kerbrute        | User enum + password spray Kerberos         |
| Certipy         | Attaques AD Certificate Services (ESC1-8)   |
| Certify         | Équivalent Certipy en C# (Windows)          |
| bloodyAD        | ACL abuse + manipulation AD (Linux)         |
| pyWhisker / Whisker | Shadow Credentials                      |
| targetedKerberoast | Kerberoasting ciblé via GenericWrite     |
| PetitPotam      | Coercion MS-EFSRPC                          |
| printerbug / SpoolSample | Coercion MS-RPRN (PrinterBug)      |
| dfscoerce       | Coercion DFS                                |
| noPac.py        | CVE-2021-42278 / 42287                      |

## Initial Access (externe)

| Outil           | Usage                                       |
|-----------------|---------------------------------------------|
| o365spray       | Spray O365 / Azure AD                       |
| MSOLSpray       | Spray Azure AD (PowerShell)                 |
| MailSniper      | Spray + recherche dans OWA                  |
| Evilginx2       | Reverse proxy phishing (bypass MFA)         |
| GoPhish         | Campagnes de phishing                       |
| macro_pack      | Génération de macros Office malveillantes   |
| EvilClippy      | Manipulation de docs Office                 |

## AV / EDR Evasion

| Outil           | Usage                                       |
|-----------------|---------------------------------------------|
| Donut           | Conversion EXE/DLL en shellcode             |
| Inceptor        | Framework de loaders + obfuscation          |
| Nimcrypt2       | Loader Nim avec bypass AV                   |
| freeze.rs       | Loader Rust avec direct syscalls            |
| ScareCrow       | Loader avec bypass EDR userland             |
| SysWhispers3    | Génération de stubs direct/indirect syscalls |
| HellsGate / HalosGate | Résolution dynamique de syscalls      |
| AmsiBypass-Reflection | Bypass AMSI sans signature              |
| Invisi-Shell    | PowerShell sans logging ni AMSI             |

## Extraction de credentials

| Outil           | Usage                                       |
|-----------------|---------------------------------------------|
| Mimikatz        | LSASS, SAM, LSA, DPAPI, Kerberos            |
| SharpDPAPI      | Extraction credentials DPAPI                |
| LaZagne         | Extraction creds multi-app multi-browser    |
| SharpChromium / SharpWeb | Vol creds Chrome / Edge / Firefox  |
| pypykatz        | Mimikatz en Python (parse LSASS dump)       |

## Notes & Reporting

| Outil          | Usage                                |
|----------------|--------------------------------------|
| Obsidian       | Prise de notes markdown (recommandé) |
| CherryTree     | Prise de notes hiérarchique + screenshots |
| Flameshot      | Screenshots (Linux)                  |
| Greenshot      | Screenshots (Windows)                |
| ShareX         | Screenshots avancés (Windows)        |
| SysReptor      | Génération de rapports modernes      |
| Pwndoc         | Génération de rapports (legacy)      |
| GhostWriter    | Collaboration équipe pentest         |
