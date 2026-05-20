---
title: "Email Security (SPF, DKIM, DMARC)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité, email, dns]
date: "2026-04-16"
---

# Email Security (SPF, DKIM, DMARC)

L'email est le vecteur d'attaque numéro 1 en entreprise. Plus de 90 % des compromissions commencent par un email (phishing, BEC, malware). La sécurité email repose sur trois mécanismes d'authentification complémentaires — SPF, DKIM et DMARC — qui vérifient que l'expéditeur est bien celui qu'il prétend être.

## Le problème fondamental

Le protocole SMTP (1982) n'a **aucune authentification native** de l'expéditeur. N'importe quel serveur SMTP peut envoyer un email avec n'importe quelle adresse `From:`. C'est comme envoyer une lettre postale avec un faux nom d'expéditeur : le protocole ne vérifie pas.

Les trois mécanismes SPF, DKIM et DMARC ont été ajoutés progressivement (2003–2015) pour combler cette lacune, en s'appuyant sur le **DNS** comme source de vérité.

## SPF — Sender Policy Framework

### Principe

SPF permet au propriétaire d'un domaine de déclarer dans le DNS **quels serveurs sont autorisés à envoyer des emails** pour ce domaine. Le serveur récepteur vérifie l'IP de l'expéditeur contre cette liste.

### Enregistrement DNS

```dns
example.com.  IN TXT  "v=spf1 ip4:203.0.113.0/24 include:_spf.google.com include:sendgrid.net -all"
```

| Mécanisme | Signification |
|---|---|
| `v=spf1` | Version du protocole |
| `ip4:203.0.113.0/24` | Autoriser cette plage IP |
| `include:_spf.google.com` | Autoriser les serveurs de Google Workspace |
| `include:sendgrid.net` | Autoriser le service d'envoi tiers |
| `-all` | **Rejeter** tout le reste (hard fail) |
| `~all` | Marquer comme suspect mais accepter (soft fail) |
| `?all` | Neutre (ne rien faire) — inutile |

### Limites de SPF

- SPF vérifie le **Return-Path** (enveloppe SMTP), pas le **From:** affiché à l'utilisateur. Un attaquant peut avoir un Return-Path légitime mais un From: usurpé.
- **Limite de 10 lookups DNS** — les `include:` s'enchaînent et comptent chacun. Au-delà de 10, le SPF échoue silencieusement. Outil de vérification : `mxtoolbox.com/spf.aspx`.
- **Transfert d'email** : quand un mail est forwarded, l'IP source change et SPF échoue → c'est ARC (Authenticated Received Chain) qui corrige ce cas.

## DKIM — DomainKeys Identified Mail

### Principe

DKIM ajoute une **signature cryptographique** dans les en-têtes de chaque email sortant. Le serveur récepteur vérifie cette signature avec la clé publique publiée dans le DNS du domaine expéditeur.

### Flux

1. Le serveur expéditeur signe le corps et certains en-têtes avec une **clé privée** (RSA 2048 bits ou Ed25519)
2. La signature est ajoutée dans l'en-tête `DKIM-Signature:`
3. Le serveur récepteur extrait le **sélecteur** (`s=`) et le **domaine** (`d=`) de la signature
4. Il requête `<sélecteur>._domainkey.<domaine>` dans le DNS pour obtenir la clé publique
5. Il vérifie la signature → si valide, le contenu n'a pas été modifié et l'expéditeur possède bien la clé privée

### En-tête DKIM

```
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
 d=example.com; s=selector1;
 h=from:to:subject:date:message-id;
 bh=base64_hash_du_corps;
 b=base64_signature;
```

### Enregistrement DNS

```dns
selector1._domainkey.example.com.  IN TXT  "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4..."
```

### Avantages sur SPF

- Vérifie l'**intégrité** du message (pas seulement l'origine)
- Survit aux **transferts d'email** (la signature voyage avec le mail)
- Lie la signature au **domaine du From:** affiché (quand aligné)

## DMARC — Domain-based Message Authentication, Reporting & Conformance

### Principe

DMARC est la **couche de politique** qui lie SPF et DKIM au domaine visible par l'utilisateur (le `From:` dans l'en-tête). Sans DMARC, SPF et DKIM fonctionnent mais le serveur récepteur n'a pas d'instruction sur quoi faire en cas d'échec.

### Vérification DMARC

Un email passe DMARC si **au moins un** des deux mécanismes réussit ET est **aligné** :

| Mécanisme | Passe si | Alignement |
|---|---|---|
| SPF | L'IP source est autorisée par le SPF du Return-Path | Le domaine du Return-Path matche le domaine du From: |
| DKIM | La signature est valide | Le `d=` de la signature DKIM matche le domaine du From: |

L'alignement peut être **strict** (domaine identique) ou **relaxed** (sous-domaine accepté, par défaut).

### Enregistrement DNS

```dns
_dmarc.example.com.  IN TXT  "v=DMARC1; p=reject; sp=reject; rua=mailto:dmarc-reports@example.com; ruf=mailto:dmarc-forensic@example.com; adkim=r; aspf=r; pct=100"
```

| Tag | Signification |
|---|---|
| `p=` | Politique : `none` (observer), `quarantine` (spam), `reject` (rejeter) |
| `sp=` | Politique pour les sous-domaines |
| `rua=` | Adresse pour les rapports agrégés (XML quotidien) |
| `ruf=` | Adresse pour les rapports forensiques (détail par message échoué) |
| `adkim=` | Alignement DKIM : `r` (relaxed) ou `s` (strict) |
| `aspf=` | Alignement SPF : `r` ou `s` |
| `pct=` | Pourcentage de messages soumis à la politique (pour déploiement progressif) |

### Déploiement progressif recommandé

1. **Phase 1 — Observation** : `p=none` avec `rua=` — collecter les rapports pendant 2-4 semaines pour identifier tous les flux légitimes
2. **Phase 2 — Quarantaine partielle** : `p=quarantine; pct=10` — appliquer à 10 % puis monter progressivement
3. **Phase 3 — Rejet** : `p=reject; pct=100` — tout email non authentifié est rejeté

Les rapports DMARC (XML) sont illisibles bruts. Outils d'analyse : **DMARC Analyzer**, **Valimail**, **dmarcian**, **Postmark DMARC**.

## BIMI — Brand Indicators for Message Identification

Extension récente (2021+) de DMARC : si un domaine a `p=quarantine` ou `p=reject`, il peut publier un **logo vérifié** (SVG) qui s'affiche à côté du nom de l'expéditeur dans les clients mail compatibles (Gmail, Apple Mail).

```dns
default._bimi.example.com.  IN TXT  "v=BIMI1; l=https://example.com/logo.svg; a=https://example.com/vmc.pem"
```

Nécessite un **VMC** (Verified Mark Certificate) délivré par une autorité (DigiCert, Entrust) — coûteux, réservé aux grandes marques.

## ARC — Authenticated Received Chain

Résout le problème du forwarding : quand un intermédiaire (mailing list, forwarding rule) modifie le mail, SPF et DKIM peuvent échouer. ARC permet à chaque intermédiaire de signer un état d'authentification qui peut être vérifié par le destinataire final.

## MTA-STS — SMTP MTA Strict Transport Security

Force le chiffrement TLS entre les serveurs SMTP. Sans MTA-STS, un attaquant peut downgrader la connexion en clair (attaque STARTTLS stripping).

```dns
_mta-sts.example.com.  IN TXT  "v=STSv1; id=20240101"
```

Politique publiée sur `https://mta-sts.example.com/.well-known/mta-sts.txt` :
```
version: STSv1
mode: enforce
mx: mail.example.com
max_age: 86400
```

## Outils de vérification

| Outil | Usage |
|---|---|
| `dig TXT example.com` | Vérifier SPF |
| `dig TXT selector._domainkey.example.com` | Vérifier DKIM |
| `dig TXT _dmarc.example.com` | Vérifier DMARC |
| **MXToolbox** (`mxtoolbox.com`) | Audit complet email (SPF, DKIM, DMARC, blacklists) |
| **mail-tester.com** | Envoyer un mail de test et recevoir un score de délivrabilité |
| **Google Admin Toolbox** (`toolbox.googleapps.com`) | Check headers, dig |
| **dmarcian.com** | Analyse rapports DMARC |

## En-têtes à lire dans un email suspect

```
Authentication-Results: mx.google.com;
    dkim=pass header.d=example.com header.s=selector1;
    spf=pass (google.com: domain of bounce@example.com designates 203.0.113.5 as permitted sender);
    dmarc=pass (p=REJECT sp=REJECT) header.from=example.com
```

Si l'un des trois affiche `fail` ou `none`, l'email est suspect.

## Récapitulatif

```
SPF   → "qui a le droit d'envoyer ?"       (IP autorisées)
DKIM  → "le message est-il intact ?"        (signature cryptographique)
DMARC → "que faire si ça échoue ?"          (politique + alignement + reporting)
```

Les trois ensemble forment une défense robuste. Un domaine sans DMARC en `reject` est **usurpable** par n'importe quel serveur SMTP.
