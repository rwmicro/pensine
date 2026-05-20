---
title: "Sécurité Informatique"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-04"
---

# Sécurité Informatique

## Vue d'ensemble

La sécurité informatique englobe la protection des systèmes, réseaux et données contre les menaces, attaques et accès non autorisés.

## Contenu de cette section

- [[Networking/Réseaux]] - Sécurité réseau et protocoles
- [[Shodan/Shodan]] - Moteur de recherche pour appareils connectés
- [[SOC Analysis]] - Security Operations Center
- [[Risk Analysis]] - Analyse de risques

## Principes fondamentaux

### Triade CIA

**Confidentialité (Confidentiality)**
- Protection contre accès non autorisé
- Chiffrement des données
- Contrôle d'accès

**Intégrité (Integrity)**
- Protection contre modification non autorisée
- Hashing et checksums
- Signatures numériques

**Disponibilité (Availability)**
- Accessibilité des systèmes
- Redondance
- Protection contre DoS/DDoS

### Defense in Depth

Multiples couches de sécurité:
1. Périmètre (firewall, WAF)
2. Réseau (segmentation, IDS/IPS)
3. Host (antivirus, hardening)
4. Application (secure coding, HTTPS)
5. Données (encryption, DLP)

## Types de menaces

### Malware

**Virus**
- S'attache à fichiers légitimes
- Se réplique

**Worms**
- Auto-réplication
- Propagation réseau

**Trojans**
- Déguisés en logiciels légitimes
- Backdoors

**Ransomware**
- Chiffre les données
- Demande rançon

**Spyware**
- Collecte d'informations
- Keyloggers

### Attaques réseau

**DDoS (Distributed Denial of Service)**
- Saturation de ressources
- Botnet

**Man-in-the-Middle**
- Interception de communications
- ARP spoofing, DNS spoofing

**Packet Sniffing**
- Capture de trafic réseau
- Wireshark, tcpdump

**Port Scanning**
- Découverte de services
- Nmap

### Attaques applicatives

**SQL Injection**
```sql
' OR '1'='1' --
```

**XSS (Cross-Site Scripting)**
```javascript
<script>alert('XSS')</script>
```

**CSRF (Cross-Site Request Forgery)**
- Exécution d'actions non autorisées

**XXE (XML External Entity)**
- Exploitation du parser XML

**SSRF (Server-Side Request Forgery)**
- Faire des requêtes depuis le serveur

### Social Engineering

**Phishing**
- Emails frauduleux
- Sites web contrefaits

**Spear Phishing**
- Ciblé sur individus spécifiques

**Pretexting**
- Scénarios inventés

**Baiting**
- USB infectées, téléchargements

## Cryptographie

### Chiffrement symétrique

**Algorithmes**
- AES (Advanced Encryption Standard)
- ChaCha20
- 3DES (obsolète)

**Utilisation**
- Données au repos
- Chiffrement de disques

### Chiffrement asymétrique

**Algorithmes**
- RSA
- ECC (Elliptic Curve)
- EdDSA

**Utilisation**
- Échange de clés
- Signatures numériques
- HTTPS/TLS

### Hashing

**Algorithmes**
- SHA-256, SHA-3
- bcrypt, scrypt (passwords)
- Argon2 (moderne)

**Utilisations**
- Vérification d'intégrité
- Stockage de mots de passe
- Signatures

### TLS/SSL

**Handshake**
1. Client Hello
2. Server Hello + Certificate
3. Key Exchange
4. Finished

**Versions**
- TLS 1.3 (actuel)
- TLS 1.2 (acceptable)
- SSL 3.0, TLS 1.0/1.1 (obsolètes)

## Authentication & Authorization

### Authentication

**Facteurs**
1. Something you know (password)
2. Something you have (token, phone)
3. Something you are (biometric)

**MFA (Multi-Factor Authentication)**
- Combinaison de 2+ facteurs
- TOTP (Time-based OTP)
- Hardware tokens (YubiKey)

**Protocoles**
- OAuth 2.0
- OpenID Connect
- SAML
- Kerberos

### Authorization

**RBAC (Role-Based Access Control)**
- Users → Roles → Permissions

**ABAC (Attribute-Based Access Control)**
- Basé sur attributs contextuels

**ACL (Access Control Lists)**
- Listes de permissions par ressource

### Session Management

**Tokens**
- JWT (JSON Web Tokens)
- Opaque tokens
- Refresh tokens

**Cookies**
- Secure flag
- HttpOnly flag
- SameSite attribute

## Sécurité réseau

### Firewall

**Types**
- Packet filtering
- Stateful inspection
- Application layer (WAF)
- Next-gen (NGFW)

**Configuration**
- Default deny
- Whitelist approach
- DMZ for public services

### VPN (Virtual Private Network)

**Protocoles**
- OpenVPN
- WireGuard
- IPSec
- IKEv2

### IDS/IPS

**IDS (Intrusion Detection System)**
- Surveillance et alertes
- Snort, Suricata

**IPS (Intrusion Prevention System)**
- Détection + blocage actif

### Segmentation

- VLANs
- Network ACLs
- Zero Trust Network

Voir: [[Networking/Réseaux]]

## Sécurité des applications

### Secure Coding

**OWASP Top 10**
1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable Components
7. Authentication Failures
8. Software and Data Integrity
9. Security Logging Failures
10. SSRF

**Input Validation**
- Whitelist approach
- Sanitization
- Parameterized queries

**Output Encoding**
- Context-aware encoding
- Prevention XSS

### Dependency Management

**Scanning**
- npm audit
- Snyk
- Dependabot
- OWASP Dependency-Check

**Best Practices**
- Keep dependencies updated
- Lock file versions
- Minimal dependencies

### Secrets Management

- Never commit secrets
- Environment variables
- Secret managers (Vault, AWS Secrets Manager)
- Rotation policies

## Security Testing

### Types de tests

**SAST (Static Application Security Testing)**
- Analyse de code source
- SonarQube, Checkmarx

**DAST (Dynamic Application Security Testing)**
- Tests en exécution
- Burp Suite, OWASP ZAP

**IAST (Interactive AST)**
- Combinaison SAST/DAST

**Penetration Testing**
- Simulation d'attaques
- Red team / Blue team

### Vulnerability Scanning

- Nessus
- OpenVAS
- Qualys
- Regular scans

## Incident Response

### Phases

1. **Preparation**
   - Plans et procédures
   - Outils et formation

2. **Detection & Analysis**
   - Monitoring
   - Log analysis
   - Alert triage

3. **Containment**
   - Isolation
   - Limitation des dégâts

4. **Eradication**
   - Suppression de la menace
   - Patching

5. **Recovery**
   - Restauration des services
   - Monitoring accru

6. **Post-Incident**
   - Lessons learned
   - Documentation
   - Amélioration

### DFIR (Digital Forensics & Incident Response)

Voir: [[Defensive/SOC Analysis/DFIR]]

## Compliance & Standards

### Frameworks

**ISO 27001**
- ISMS (Information Security Management System)

**NIST Cybersecurity Framework**
- Identify, Protect, Detect, Respond, Recover

**CIS Controls**
- 18 contrôles de sécurité critiques

### Regulations

**RGPD (GDPR)**
- Protection des données personnelles
- Droit à l'oubli
- Privacy by design

**PCI DSS**
- Payment Card Industry
- Protection des données de carte

**HIPAA**
- Healthcare data (US)

## Outils essentiels

### Network
- Wireshark - Packet analysis
- Nmap - Port scanning
- tcpdump - Packet capture
- See: [[Shodan/Shodan]]

### Web Security
- Burp Suite - Pen testing
- OWASP ZAP - Vulnerability scanner
- Nikto - Web scanner

### Password
- John the Ripper
- Hashcat
- KeePass - Password manager

### Forensics
- Volatility - Memory analysis
- Autopsy - Disk forensics
- FTK - Forensic toolkit

## Best Practices

### Pour développeurs

1. **Never trust user input**
2. **Use prepared statements**
3. **Hash passwords with salt**
4. **Enable HTTPS everywhere**
5. **Keep dependencies updated**
6. **Implement proper logging**
7. **Use security headers**
8. **Follow principle of least privilege**

### Pour administrateurs

1. **Patch management**
2. **Backup strategy (3-2-1 rule)**
3. **Network segmentation**
4. **Log centralization**
5. **Access control reviews**
6. **Security awareness training**
7. **Incident response plan**

### Security Headers

```
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=()
```

## Veille et ressources

- CVE (Common Vulnerabilities and Exposures)
- CERT advisories
- OWASP
- SANS Institute
- Krebs on Security
- Security conferences (DEF CON, Black Hat)

## Sujets à approfondir

- [ ] Blockchain security
- [ ] IoT security
- [ ] Cloud security
- [ ] Container security
- [ ] API security
- [ ] Mobile security