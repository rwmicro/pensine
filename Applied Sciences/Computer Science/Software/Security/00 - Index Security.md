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

## Offensive

`Offensive/` — exploitation et post-exploitation.

- Élévation de privilèges : [[Linux Privilege Escalation]], [[Windows Privilege Escalation]]
- Mouvement et accès : [[Lateral Movement]], [[Pivoting et Tunneling]], [[Persistence]]
- Infrastructure et discrétion : [[C2 Infrastructure]], [[AV-EDR Evasion]], [[Data Exfiltration]]
- Vivre de la terre : [[LOLBAS et GTFOBins]], [[Recon Automation]], [[Bug Bounty Methodology]]
- **Outils** (`Offensive/Tools/`) : [[nmap]], [[Burp Suite]], [[ffuf et Gobuster]], [[Nuclei]], [[Impacket]], [[Responder]], [[Tshark]]

## Active Directory

`Active Directory/` — [[Active Directory Security]], [[Kerberos Attacks]], [[NTLM Relay]], [[ACL Abuse]], [[ADCS]], [[AD Trusts et Forêts]], [[AD Persistence Avancée]], [[BloodHound]], [[Mimikatz]], [[CrackMapExec]], [[PowerShell Pentest]]

## Web Security

`Web Security/` — OWASP et au-delà : [[SQL Injections]], [[Command Injection]], [[Path Traversal]], [[SSTI]], [[XXE en profondeur]], [[Insecure Deserialization]], [[File Upload Vulnerabilities]], [[HTTP Request Smuggling]], [[Web Cache Poisoning]], [[API Security]], [[GraphQL Security]], [[Business Logic Vulnerabilities]], [[Race Conditions]]… (28 notes)

## Networking

`Networking/Fundamentals/` — réseau pur : [[IPv4]], [[IPv6]], [[Adressage IP]], [[ARP]], [[Modèles Réseau]], [[Protocoles Réseau]], [[DNS en profondeur]], [[HTTPS]], [[NAT et ACL]], [[SNMP]], [[QoS]], routage ([[OSPF]], [[RIP]], [[EIGRP]]), [[VPN Protocols]], [[Outils Réseau]]…

`Networking/Network Security/` — sécurité réseau : [[Sécurité Réseau]], [[Attaques Réseau]], [[Spoofing]], [[VLAN Hopping]], [[BGP Hijacking]], [[IDS-IPS-WAF]], [[Scanning]], [[Iptable]], et le WiFi ([[00 - Index WiFi]]).

## Defensive — SOC, détection, forensique

`Defensive/` — [[Forensique Réseau]], [[Ransomware]]

`Defensive/SOC Analysis/` — [[SOC Analyst]], [[SOC Structure]], [[SIEM (Security Information and event Management)]], [[SOAR]], [[Splunk]], [[Detection Engineering]], [[Sigma]], [[Threat Hunting]], [[Threat Intelligence]], [[Threat Modeling pour la détection (SOC)]], [[APT et Acteurs de la Menace]], [[Logs]]

`Defensive/SOC Analysis/DFIR/` — [[DFIR]], [[Malware Analysis]], [[Memory Analysis]], [[Volatility 3]], [[Windows Forensics]], [[Linux Forensics]], [[Network Forensics]], [[Playbooks IR]]

## GRC et Gouvernance

`GRC et Gouvernance/` — [[Threat Modeling]] (note canonique), [[Compliance]], [[Gestion des Vulnérabilités]], [[Secure SDLC]], [[Zero Trust Architecture]], [[Business Continuity et Disaster Recovery]], [[Supply Chain Attacks]], EBIOS RM (`Risk Analysis/`)

## OSINT et Social Engineering

`OSINT/` — [[Méthodologie OSINT]], [[Sources OSINT]], [[Outils OSINT]], [[Techniques et Use Cases]], [[Shodan]], [[Protection et Reporting]]

`Social Engineering/` — [[Ingénierie Sociale]], [[Phishing Analysis]], [[Email Security]], [[SMTP et Email Attacks]]

## Spécialités

- `Cryptographie/` — [[Cryptographie]], [[Hash Cracking]], [[Padding Oracle Attack]], [[PKI en profondeur]], [[Encodages]], [[Steganographie]]
- `Cloud/` — [[Cloud Security]], [[Azure Security]], [[GCP Security]], [[Kubernetes Security]]
- `Identity et Auth/` — [[JWT]], [[OAuth et OIDC]], [[PAM - Privileged Access Management]]
- `Reverse Engineering/` — [[Reverse Engineering]], [[Binary Exploitation]], [[Firmware Analysis]], [[fuzzing]]
- `Platform Security/` — [[ICS-SCADA Security]], [[macOS Security]], [[Sécurité Mobile]], [[Physical Security]]
- `AI Security/` — [[Prompt Injection]]

## Certifications

`Certifications/` — préparation d'examens (notes structurées par question/sujet)

- **LFCS** — voir l'index `Certifications/LFCS/notes.md`
- **PNPT** — voir `Certifications/PNPT-cert/`
