---
title: "Index — Security"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité, index, moc]
date: "2026-05-29"
---

# Index — Security

Carte du domaine sécurité du vault. Organisation par discipline, du concept à l'opérationnel.

## Méthodologie et concepts transverses

- [[Pentest Methodology]] — démarche générale d'un pentest
- [[Red Team et Blue Team]] — adversary simulation, rôles offensif/défensif
- [[Purple Teaming]] — collaboration red/blue, validation de la détection
- [[MITRE ATT&CK]] — vocabulaire des TTP, cartographie et limites
- [[Adversary Emulation]] — construction et mesure d'un scénario d'émulation

## Offensive

`Offensive/` — exploitation et post-exploitation.

- Accès initial : [[Initial Access]] — phishing, fichiers, services exposés, comptes valides, supply chain
- Élévation de privilèges : [[Linux Privilege Escalation]], [[Windows Privilege Escalation]]
- Mouvement et accès : [[Lateral Movement]], [[Pivoting et Tunneling]], [[Persistence]]
- Identifiants : [[Credential Access]] — LSASS, SAM/NTDS, DCSync, DPAPI, Kerberos, jetons
- Infrastructure et discrétion : [[C2 Infrastructure]], [[C2 avancé]], [[AV-EDR Evasion]], [[OPSEC Red Team]], [[Data Exfiltration]]
- Vivre de la terre : [[LOLBAS et GTFOBins]], [[Recon Automation]], [[Bug Bounty Methodology]]
- **Outils** (`Offensive/Tools/`) : [[nmap]], [[Burp Suite]], [[ffuf et Gobuster]], [[Nuclei]], [[Impacket]], [[Responder]], [[Tshark]]

## Malware Development

`Malware Development/` — développement de malware Windows, du format PE aux syscalls. Voir l'index détaillé : [[00 - Index Malware Development]].

- Fondations : [[Architecture Windows]], [[Gestion de la mémoire Windows]], [[Windows API]], [[Format PE]]
- Payload : [[Placement du payload]], [[Chiffrement du payload]], [[Obfuscation du payload]]
- Injection : [[Injection de DLL]], [[Injection de shellcode]], [[Détournement de threads]], [[Injection APC et Early Bird]], [[Injection par mapping]], [[Process hollowing]], [[Reflective DLL injection]]
- Évasion : [[Dissimulation de l'IAT]], [[API hooking]], [[Introduction aux syscalls]], [[Unhooking de NTDLL]], [[AMSI et ETW bypass]], [[Obscurcissement du sommeil]], [[Spoofing de pile d'appels]]
- Anti-analyse : [[Anti-debugging]], [[Anti-VM et évasion d'environnement]]
- Autres systèmes : [[Malware Linux]], [[Malware macOS]]

## Active Directory

`Active Directory/` — [[Active Directory Security]], [[Kerberos Attacks]], [[NTLM Relay]], [[ACL Abuse]], [[ADCS]], [[AD Trusts et Forêts]], [[AD Persistence Avancée]], [[BloodHound]], [[Mimikatz]], [[CrackMapExec]], [[PowerShell Pentest]]

## Web Security

`Web Security/` — OWASP et au-delà : [[SQL Injections]], [[Command Injection]], [[Path Traversal]], [[SSTI]], [[XXE en profondeur]], [[Insecure Deserialization]], [[File Upload Vulnerabilities]], [[HTTP Request Smuggling]], [[Web Cache Poisoning]], [[API Security]], [[GraphQL Security]], [[Business Logic Vulnerabilities]], [[Race Conditions]]… (28 notes)

## Networking

`Networking/Fundamentals/` — réseau pur : [[IPv4]], [[IPv6]], [[Adressage IP]], [[ARP]], [[Modèles Réseau]], [[Protocoles Réseau]], [[DNS en profondeur]], [[HTTPS]], [[NAT et ACL]], [[SNMP]], [[QoS]], routage ([[OSPF]], [[RIP]], [[EIGRP]]), [[VPN Protocols]], [[Outils Réseau]]…

`Networking/Network Security/` — sécurité réseau : [[Sécurité Réseau]], [[Attaques Réseau]], [[Spoofing]], [[VLAN Hopping]], [[BGP Hijacking]], [[IDS-IPS-WAF]], [[Scanning]], [[Iptable]], et le WiFi ([[00 - Index WiFi]]).

## Defensive — SOC, détection, forensique

`Defensive/` — [[Forensique Réseau]], [[Ransomware]]

`Defensive/SOC Analysis/` — [[SOC Analyst]], [[SOC Structure]], [[SIEM (Security Information and event Management)]], [[SOAR]], [[Splunk]], [[Detection Engineering]], [[Sigma]], [[YARA et CAPA]], [[EDR internals]], [[Détection mémoire des injections]], [[Threat Hunting]], [[Threat Intelligence]], [[Threat Modeling pour la détection (SOC)]], [[APT et Acteurs de la Menace]], [[Logs]]

`Defensive/SOC Analysis/DFIR/` — [[DFIR]], [[Malware Analysis]], [[Memory Analysis]], [[Volatility 3]], [[Windows Forensics]], [[Linux Forensics]], [[Network Forensics]], [[Playbooks IR]]

## GRC et Gouvernance

`GRC et Gouvernance/` — [[Threat Modeling]] (note canonique), [[Compliance]], [[Gestion des Vulnérabilités]], [[Secure SDLC]], [[Zero Trust Architecture]], [[Business Continuity et Disaster Recovery]], [[Supply Chain Attacks]], [[Privacy Engineering]], EBIOS RM (`Risk Analysis/`)

## OSINT et Social Engineering

`OSINT/` — [[Méthodologie OSINT]], [[Sources OSINT]], [[Outils OSINT]], [[Techniques et Use Cases]], [[Shodan]], [[Protection et Reporting]]

`Social Engineering/` — [[Ingénierie Sociale]], [[Phishing Analysis]], [[Email Security]], [[SMTP et Email Attacks]]

## Spécialités

- `Cryptographie/` — [[Cryptographie]], [[TLS 1.3]], [[Cryptographie post-quantique]], [[Gestion des clés et HSM]], [[Hachage de mots de passe]], [[Attaques par canal auxiliaire]], [[Hash Cracking]], [[Padding Oracle Attack]], [[PKI en profondeur]], [[Encodages]], [[Steganographie]]
- `Cloud/` — [[Cloud Security]], [[Azure Security]], [[GCP Security]], [[Kubernetes Security]]
- `Identity et Auth/` — [[JWT]], [[OAuth et OIDC]], [[PAM - Privileged Access Management]]
- `Reverse Engineering/` — [[Reverse Engineering]], [[Binary Exploitation]], [[Firmware Analysis]], [[fuzzing]]
- `Platform Security/` — [[ICS-SCADA Security]], [[macOS Security]], [[Sécurité Mobile]], [[Physical Security]]
- `AI Security/` — [[Prompt Injection]]

## Parcours de lecture

Des chemins possibles pour aborder le domaine sans se disperser. Chaque étape suppose la précédente.

| Parcours | Progression |
|---|---|
| Fondations offensives | [[Pentest Methodology]] → [[Recon Automation]] → [[Initial Access]] → [[Windows Privilege Escalation]] / [[Linux Privilege Escalation]] → [[Lateral Movement]] → [[Credential Access]] |
| Infrastructure red team | [[C2 Infrastructure]] → [[C2 avancé]] → [[Pivoting et Tunneling]] → [[OPSEC Red Team]] → [[Data Exfiltration]] |
| Malware Development | [[00 - Index Malware Development]] → fondations Windows → payload → injection → évasion → [[Obscurcissement du sommeil]] / [[Spoofing de pile d'appels]] → [[Malware Linux]] / [[Malware macOS]] |
| Détection et réponse | [[Logs]] → [[SIEM (Security Information and event Management)]] → [[Detection Engineering]] → [[Sigma]] → [[YARA et CAPA]] → [[EDR internals]] → [[Détection mémoire des injections]] → [[Purple Teaming]] |
| Émulation et mesure | [[MITRE ATT&CK]] → [[Threat Intelligence]] → [[Adversary Emulation]] → [[Purple Teaming]] |
| Cryptographie appliquée | [[Cryptographie]] → [[TLS 1.3]] → [[PKI en profondeur]] → [[Gestion des clés et HSM]] → [[Cryptographie post-quantique]] |
| Gouvernance | [[Threat Modeling]] → [[Compliance]] → [[EBIOS RM]] → [[Privacy Engineering]] → [[Business Continuity et Disaster Recovery]] |

## Certifications

`Certifications/` — préparation d'examens (notes structurées par question/sujet)

- **LFCS** — voir l'index `Certifications/LFCS/notes.md`
- **PNPT** — voir `Certifications/PNPT-cert/`
