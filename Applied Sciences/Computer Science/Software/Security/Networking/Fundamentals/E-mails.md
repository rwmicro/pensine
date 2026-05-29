---
title: "Sécurité des e-mails"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals"
tags: [sciences-appliquées, informatique, sécurité, réseau, email]
date: "2025-03-14"
---

# Sécurité des e-mails

## Protocoles de messagerie et leurs ports

|**Protocole**|**Rôle**|**Port par défaut**|**Port sécurisé (SSL/TLS)**|
|---|---|---|---|
|SMTP (Simple Mail Transfer Protocol)|Envoi d'e-mails|25|465 (SSL) / 587 (TLS)|
|IMAP (Internet Message Access Protocol)|Consultation des e-mails sur un serveur|143|993 (SSL)|
|POP3 (Post Office Protocol v3)|Récupération des e-mails depuis un serveur|110|995 (SSL)|

## Façons de sécuriser un e-mail

### Sécurisation de la connexion

- **Utilisation des protocoles sécurisés** : Préférer SMTP avec TLS/SSL, IMAP avec SSL (port 993) ou POP3 avec SSL (port 995).
- **Authentification obligatoire** : Activer l'authentification SMTP pour éviter l'envoi de mails frauduleux.
- **Chiffrement des connexions** : Opter pour STARTTLS ou SSL/TLS pour sécuriser les échanges entre le client et le serveur.

### Protection contre le phishing et le spam

- **Filtrage anti-spam** : Activer les filtres proposés par les fournisseurs de messagerie.
- **Utilisation de listes noires et blanches** : Bloquer les expéditeurs suspects et autoriser les sources fiables.
- **Éducation des utilisateurs** : Sensibiliser sur les dangers des liens et pièces jointes suspectes.

### Authenticité et intégrité des e-mails

- **DKIM (DomainKeys Identified Mail)** : Vérifie que l'e-mail n’a pas été modifié en transit grâce à une signature cryptographique.
- **SPF (Sender Policy Framework)** : Définit les serveurs autorisés à envoyer des mails au nom d’un domaine.
- **DMARC (Domain-based Message Authentication, Reporting & Conformance)** : Combine SPF et DKIM pour améliorer la protection contre l’usurpation d’identité.

### Chiffrement du contenu des e-mails

- **PGP (Pretty Good Privacy) / GPG (Gnu Privacy Guard)** : Chiffrement de bout en bout des e-mails.
- **S/MIME (Secure/Multipurpose Internet Mail Extensions)** : Signature et chiffrement des e-mails avec des certificats numériques.

### Bonnes pratiques utilisateur

- **Utilisation de mots de passe forts** : Privilégier des mots de passe complexes et uniques.
- **Double authentification (2FA)** : Activer l'authentification à deux facteurs pour sécuriser l’accès à la messagerie.
- **Vérification des destinataires et pièces jointes** : Toujours s’assurer de l’adresse de destination et de la nature des fichiers envoyés.
