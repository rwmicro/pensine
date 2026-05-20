---
title: "OAuth 2.0, OIDC et SAML"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-25"
---

# OAuth 2.0, OIDC et SAML

OAuth 2.0 est un framework d'**autorisation** (délégation d'accès) — il permet à une application d'accéder à des ressources au nom d'un utilisateur sans que celui-ci ne partage ses credentials. OpenID Connect (OIDC) ajoute une couche d'**authentification** sur OAuth 2.0. SAML est un standard plus ancien remplissant un rôle similaire dans les environnements d'entreprise.

## La danse à quatre acteurs

OAuth résout un problème précis : "comment laisser une app tierce accéder à mes données sans lui donner mon mot de passe ?". Quatre rôles distincts, qui interagissent dans un ordre strict.

```
                    ┌────────────────────────┐
                    │   Resource Owner       │
                    │   (Alice, l'utilisateur)│
                    └─────────┬──────────────┘
                              │
                              │ "Je veux laisser
                              │  l'app X accéder à
                              │  mon calendrier."
                              ▼
   ┌──────────────────┐                    ┌──────────────────────┐
   │  Client          │                    │ Authorization Server │
   │  (l'app X qui    │ ──── 1. redirect ──►│ (Google, Auth0,      │
   │   veut accéder)  │                    │  Keycloak, etc.)     │
   │                  │ ◄──── 2. code ──── │                      │
   │                  │ ──── 3. code  ────►│ (Alice s'authentifie │
   │                  │ ◄──── 4. token ─── │  + consent)          │
   └────────┬─────────┘                    └──────────────────────┘
            │
            │ 5. Authorization: Bearer eyJ...
            ▼
   ┌──────────────────┐
   │ Resource Server  │
   │ (Google Calendar │
   │  API)            │
   └──────────────────┘
```

**Pourquoi quatre acteurs et pas trois ?** Parce que séparer l'Authorization Server du Resource Server permet à un même Authorization Server (ex. Google) de protéger plusieurs APIs distinctes (Gmail, Drive, Calendar), et de gérer les consentements de façon centralisée. C'est aussi ce qui rend OAuth réutilisable comme système SSO via OIDC.

## OAuth 2.0

### Acteurs

| Rôle | Description | Exemple |
|---|---|---|
| **Resource Owner** | L'utilisateur propriétaire des données | Alice |
| **Client** | L'application qui demande l'accès | Application tierce |
| **Authorization Server** | Émet les tokens après consentement | Google, Auth0, Keycloak |
| **Resource Server** | L'API protégée | Google Calendar API |

### Tokens

- **Access Token** : credential d'accès à courte durée de vie, présenté à l'API
- **Refresh Token** : credential longue durée pour obtenir un nouveau access token
- **Authorization Code** : code échangeable contre les tokens (utilisé une seule fois)

### Flows (Grant Types)

#### Authorization Code + PKCE (recommandé pour apps publiques)

```
1. Client → Authorization Server
   GET /authorize?
     response_type=code
     &client_id=app123
     &redirect_uri=https://app.com/callback
     &scope=openid profile email
     &state=random_csrf_token          ← protection CSRF
     &code_challenge=S256_hash         ← PKCE
     &code_challenge_method=S256

2. Utilisateur s'authentifie et consent

3. Authorization Server → Client
   GET https://app.com/callback?code=AUTH_CODE&state=random_csrf_token

4. Client → Authorization Server (échange code contre tokens)
   POST /token
   grant_type=authorization_code
   &code=AUTH_CODE
   &redirect_uri=https://app.com/callback
   &client_id=app123
   &code_verifier=PKCE_VERIFIER        ← PKCE

5. Authorization Server → Client
   {
     "access_token": "eyJ...",
     "token_type": "Bearer",
     "expires_in": 3600,
     "refresh_token": "def50200...",
     "id_token": "eyJ..."              ← OIDC uniquement
   }

6. Client → Resource Server
   GET /api/calendrier
   Authorization: Bearer eyJ...
```

**PKCE** (Proof Key for Code Exchange) : le client génère un `code_verifier` aléatoire, en calcule le hash SHA-256 (`code_challenge`), l'envoie à l'étape 1, puis prouve la possession à l'étape 4. Empêche l'interception du code d'autorisation.

#### Client Credentials (machine à machine)

```
POST /token
grant_type=client_credentials
&client_id=service_a
&client_secret=secret
&scope=api:read

→ {"access_token": "...", "expires_in": 3600}
```

Pas d'utilisateur impliqué. Utilisé pour les communications entre services.

#### Device Authorization (appareils sans navigateur)

```
1. Device → Authorization Server : demande un device_code
2. Authorization Server → Device : device_code + user_code + verification_uri
3. Device affiche : "Allez sur example.com/activate et entrez : ABCD-1234"
4. Utilisateur s'authentifie sur son téléphone/ordinateur
5. Device poll l'Authorization Server avec le device_code jusqu'à approbation
```

Utilisé par les Smart TV, CLI tools (GitHub CLI, AWS CLI).

#### Implicit et Resource Owner Password (dépréciés)

- **Implicit** : retourne l'access token directement dans le fragment URI — vulnérable à la fuite de tokens, remplacé par PKCE
- **ROPC** : l'application reçoit les credentials utilisateur — viole le principe de délégation

## OpenID Connect (OIDC)

OIDC étend OAuth 2.0 avec un **ID Token** (JWT) qui contient des claims sur l'identité de l'utilisateur.

### ID Token (JWT)

```json
// Header
{
  "alg": "RS256",
  "kid": "key_id_123",
  "typ": "JWT"
}

// Payload (claims)
{
  "iss": "https://accounts.google.com",   // issuer
  "sub": "110169484474386276334",          // subject (user ID unique)
  "aud": "app123.apps.googleusercontent.com",  // audience (client_id)
  "exp": 1735689600,                       // expiration
  "iat": 1735686000,                       // issued at
  "nonce": "random_nonce",                 // protection replay
  "email": "alice@example.com",
  "email_verified": true,
  "name": "Alice Dupont",
  "picture": "https://..."
}
```

### Endpoints OIDC

```bash
# Discovery document (OpenID Configuration)
GET https://accounts.google.com/.well-known/openid-configuration
→ {
    "issuer": "https://accounts.google.com",
    "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
    "token_endpoint": "https://oauth2.googleapis.com/token",
    "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
    "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs"   ← clés publiques
  }
```

## SAML 2.0

SAML utilise des assertions XML signées, typiquement dans un contexte SSO entreprise (Okta, ADFS, Azure AD).

### Flow SSO (SP-initiated)

```
1. Utilisateur → Service Provider (SP) : accède à app.company.com
2. SP → Navigateur : redirect vers Identity Provider (IdP)
   avec SAMLRequest (XML base64 encodé)
3. Navigateur → IdP : présente le SAMLRequest
4. IdP : authentifie l'utilisateur (login/MFA)
5. IdP → Navigateur : POST vers SP avec SAMLResponse (assertion XML signée)
6. SP : valide la signature, extrait les attributs, crée la session
```

```xml
<!-- SAMLResponse — assertion XML signée par l'IdP -->
<saml:Assertion>
  <saml:Issuer>https://idp.company.com</saml:Issuer>
  <saml:Subject>
    <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">
      alice@company.com
    </saml:NameID>
  </saml:Subject>
  <saml:Conditions NotBefore="..." NotOnOrAfter="...">
    <saml:AudienceRestriction>
      <saml:Audience>https://app.company.com</saml:Audience>
    </saml:AudienceRestriction>
  </saml:Conditions>
  <saml:AttributeStatement>
    <saml:Attribute Name="groups">
      <saml:AttributeValue>admin</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
  <Signature>...</Signature>
</saml:Assertion>
```

## Vulnérabilités courantes

### OAuth

**Authorization Code Interception**

```
Si redirect_uri n'est pas strictement validée :
Attaquant redirige vers redirect_uri=https://attaquant.com/callback
→ Vole le code d'autorisation
→ Contre-mesure : PKCE, validation exacte du redirect_uri
```

**CSRF sur le flow OAuth**

```
Le paramètre state n'est pas validé :
Attaquant forge une URL de callback avec son propre code
→ Victime lié au compte de l'attaquant (account linking attack)
→ Contre-mesure : valider state côté client, le lier à la session
```

**Open Redirect dans redirect_uri**

```
GET /authorize?redirect_uri=https://app.com/callback%2F%2E%2E%2F%2E%2E%2Fattaquant.com
→ Certains serveurs acceptent les variantes URL encodées
→ Contre-mesure : whitelist stricte, pas de pattern matching
```

**Token Leakage via Referer**

```
Si l'access token est dans l'URL (fragment ou query) :
https://app.com/dashboard#access_token=secret
→ Le Referer header peut l'exposer
→ Contre-mesure : Authorization Code flow, tokens dans le body
```

### SAML

**XML Signature Wrapping (XSW)**

L'attaquant duplique le nœud signé et insère un nœud malveillant. Si le SP valide la signature du nœud original mais lit les attributs du nœud malveillant, il peut s'authentifier en tant qu'admin.

```xml
<!-- SAML Response modifiée par XSW -->
<saml:Assertion ID="malicious">
  <!-- attributs de l'attaquant -->
  <saml:NameID>attaquant@evil.com</saml:NameID>
</saml:Assertion>
<saml:Assertion ID="original">
  <!-- assertion originale signée (non modifiée) -->
  <saml:NameID>alice@company.com</saml:NameID>
  <Signature><!-- signature valide --></Signature>
</saml:Assertion>
```

**Commentaires XML dans NameID**

```xml
<!-- Certains parseurs ignèrent les commentaires XML -->
<saml:NameID>admin<!--commentaire-->@company.com</saml:NameID>
→ Parseur A lit : "admin@company.com"  (authentification admin)
→ Parseur B lit : "admin@company.com"  (logique métier)
```

## Bonnes pratiques

| Pratique | Description |
|---|---|
| Toujours utiliser PKCE | Même pour les clients confidentiels |
| Valider l'audience (`aud`) | Vérifier que le token est bien destiné à votre application |
| Valider l'issuer (`iss`) | Vérifier la source du token |
| Short-lived access tokens | < 15 minutes, refresh tokens rotatifs |
| Stocker les tokens en mémoire | Pas en localStorage (XSS) |
| Valider `state` et `nonce` | Protection CSRF et replay |
| Scopes minimaux | Principe du moindre privilège |

## Comparatif

| Dimension | OAuth 2.0 | OIDC | SAML 2.0 |
|---|---|---|---|
| But | Autorisation | Authentification + autorisation | Authentification (SSO) |
| Format token | Opaque ou JWT | JWT (ID Token) | XML |
| Transport | JSON/HTTP | JSON/HTTP | XML/HTTP POST |
| Cas d'usage | API, apps mobiles | Login social, apps web | SSO entreprise, ADFS |
| Complexité | Moyenne | Moyenne | Élevée |

## Pièges courants

- **`state` oublié** : sans validation de `state`, un attaquant peut forger un callback OAuth qui lie le compte de la victime à son propre compte (account linking attack). Toujours générer un `state` aléatoire et le vérifier au retour.
- **`redirect_uri` validé en pattern matching** : une whitelist regex `^https://app.com/.*` peut être bypass avec `https://app.com.attaquant.com`. Toujours validation exacte (string match), jamais regex.
- **PKCE oublié sur apps publiques** : pour les SPA et mobiles, sans PKCE, le code d'autorisation interceptable peut être échangé par un attaquant. Toujours `code_challenge` + `code_verifier`.
- **Implicit flow encore utilisé** : `response_type=token` retourne le token dans le fragment URL → fuite via Referer, historique navigateur. Déprécié depuis OAuth 2.1, à remplacer par Authorization Code + PKCE.
- **ROPC pour les apps mobiles** : Resource Owner Password Credentials grant fait que l'app reçoit le mot de passe utilisateur. Antithèse d'OAuth. À ne JAMAIS utiliser sauf cas legacy précis.
- **Scopes trop larges** : demander `*` ou `admin` quand on n'a besoin que de `read:profile` est une mauvaise pratique qui maximise l'impact d'une compromission. Principe du moindre privilège.
- **ID Token utilisé comme access token** : l'ID Token (OIDC) prouve l'identité, pas l'autorisation. Il n'est pas destiné aux APIs. Toujours utiliser l'access token pour appeler les APIs.
- **JWKS endpoint non caché** : la rotation de clés exige que le client interroge `/jwks.json` régulièrement. Mais beaucoup de clients cachent indéfiniment → une clé compromise reste utilisable.
- **SAML XSW (XML Signature Wrapping)** : le SP valide la signature d'un nœud mais lit les attributs d'un autre. Toujours valider que **les attributs lus appartiennent au nœud signé**.
- **SAML commentaires XML dans NameID** : certains parseurs ignorent les commentaires, d'autres les considèrent. `admin<!--x-->@victim.com` peut être lu différemment selon la couche. Normaliser avant comparaison.
- **OAuth illicit consent grant** : un attaquant crée une app OAuth qui demande des scopes étendus, envoie le lien de consentement à la victime → si elle accepte sans regarder, l'attaquant a un access token persistant. Particulièrement critique sur Microsoft 365.
