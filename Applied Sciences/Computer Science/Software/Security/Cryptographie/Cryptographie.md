---
title: "Cryptographie"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-25"
---

# Cryptographie

La cryptographie est la science de la protection de l'information par transformation mathématique. Elle garantit quatre propriétés fondamentales : **confidentialité** (seuls les destinataires légitimes peuvent lire), **intégrité** (les données n'ont pas été altérées), **authenticité** (l'identité des parties est vérifiée), **non-répudiation** (l'émetteur ne peut nier avoir envoyé).

## Concepts fondamentaux

**Texte en clair (cleartext)** : données non chiffrées, lisibles directement.

**Plaintext** : données à chiffrer ou venant d'être déchiffrées (sous-ensemble du cleartext).

**Stéganographie** : technique qui dissimule l'existence même du message en l'intégrant dans un fichier apparemment anodin (image, audio, vidéo). Distinct de la cryptographie qui rend le message illisible mais visible.

### Chiffrements par flux vs par bloc

| Type | Description | Caractéristiques |
|------|-------------|-----------------|
| **Stream cipher** | Chiffre un caractère à la fois | Rapide sur textes courts, plus vulnérable aux attaques |
| **Block cipher** | Chiffre des blocs (typiquement 8-16 octets) à la fois | Plus sûr car chaque bloc est randomisé indépendamment |

Le **chiffrement par substitution monoalphabétique** est le stream cipher le plus simple (chaque lettre remplacée par une autre). La variante **homoalphabétique** mappe un caractère vers plusieurs ciphertexts différents pour plus de sécurité.

## Chiffrement symétrique

Une seule clé est partagée entre l'émetteur et le destinataire pour chiffrer et déchiffrer.

### AES (Advanced Encryption Standard)

AES est le standard mondial depuis 2001 (NIST). Il opère sur des blocs de 128 bits avec des clés de 128, 192 ou 256 bits.

```
Plaintext (128 bits)
→ AddRoundKey
→ [SubBytes → ShiftRows → MixColumns → AddRoundKey] × N rounds
→ SubBytes → ShiftRows → AddRoundKey
→ Ciphertext (128 bits)
```

Les **modes d'opération** déterminent comment AES est appliqué à des messages longs :

| Mode | Sécurité | Parallélisable | Usage |
|---|---|---|---|
| ECB | Faible (blocs identiques → chiffrement identique) | Oui | Déconseillé |
| CBC | Bonne | Déchiffrement seulement | TLS 1.2, chiffrement fichiers |
| CTR | Bonne | Oui | Streaming |
| GCM | Bonne + authentification intégrée | Oui | TLS 1.3, recommandé |
| CCM | Bonne + authentification | Non | IoT |

GCM (Galois/Counter Mode) est le mode recommandé car il fournit **AEAD** (Authenticated Encryption with Associated Data) : chiffrement + MAC en une seule opération.

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

cle = AESGCM.generate_key(bit_length=256)
nonce = os.urandom(12)   # 96 bits pour GCM, NE JAMAIS réutiliser avec la même clé
aesgcm = AESGCM(cle)

chiffre = aesgcm.encrypt(nonce, b"message secret", b"données associées")
clair   = aesgcm.decrypt(nonce, chiffre, b"données associées")
```

### ChaCha20-Poly1305

Alternative à AES-GCM résistante aux attaques par timing sur le matériel sans accélération AES (utilisée dans TLS 1.3 et WireGuard).

## Chiffrement asymétrique

Deux clés mathématiquement liées : la clé publique chiffre (ou vérifie), la clé privée déchiffre (ou signe).

### RSA

Basé sur la difficulté de factoriser le produit de deux grands nombres premiers.

```
1. Choisir deux grands premiers p et q
2. n = p × q (module public)
3. φ(n) = (p-1)(q-1)
4. Choisir e premier avec φ(n) [souvent 65537]
5. Calculer d tel que e×d ≡ 1 (mod φ(n))

Clé publique : (e, n)
Clé privée   : (d, n)

Chiffrement  : c = m^e mod n
Déchiffrement: m = c^d mod n
```

Taille de clé recommandée : **2048 bits minimum** (4096 pour les données long terme).

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Génération
cle_privee = rsa.generate_private_key(public_exponent=65537, key_size=2048)
cle_publique = cle_privee.public_key()

# Chiffrement OAEP (padding sécurisé)
chiffre = cle_publique.encrypt(
    b"message",
    padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
)

# Déchiffrement
clair = cle_privee.decrypt(chiffre, padding.OAEP(...))
```

En pratique, RSA ne chiffre pas directement les données (trop lent) — il chiffre une **clé symétrique** AES. C'est le principe des enveloppes chiffrées.

### Échange de clés Diffie-Hellman (DH)

Permet à deux parties de s'accorder sur un secret partagé sur un canal public, sans jamais échanger ce secret.

```
Alice choisit a (secret) → A = g^a mod p (public)
Bob   choisit b (secret) → B = g^b mod p (public)

Alice calcule : B^a mod p = g^(ab) mod p
Bob   calcule : A^b mod p = g^(ab) mod p

Secret partagé = g^(ab) mod p  ← identique des deux côtés
```

**ECDH** (Elliptic Curve Diffie-Hellman) offre la même sécurité avec des clés beaucoup plus courtes (256 bits ECDH ≈ 3072 bits DH classique).

### Courbes elliptiques (ECC)

L'opération de base est l'addition de points sur une courbe `y² = x³ + ax + b` dans un corps fini. La sécurité repose sur la difficulté du problème du logarithme discret elliptique (ECDLP).

Courbes recommandées : **P-256** (secp256r1), **P-384**, **Curve25519** (X25519 pour DH, Ed25519 pour signatures).

## Fonctions de hachage cryptographique

Une fonction de hachage produit une empreinte de taille fixe depuis une entrée de taille quelconque. Elle doit être :
- **À sens unique** : impossible de retrouver l'entrée depuis le hash
- **Résistante aux collisions** : difficile de trouver deux entrées avec le même hash
- **Effet avalanche** : un bit modifié change ~50% des bits du hash

| Algorithme | Taille | Statut |
|---|---|---|
| MD5 | 128 bits | Cassé (collisions triviales) — ne pas utiliser pour la sécurité |
| SHA-1 | 160 bits | Cassé (SHAttered, 2017) — déprécié |
| SHA-256 | 256 bits | Sûr — recommandé |
| SHA-3 (Keccak) | 256/384/512 | Sûr — standard NIST depuis 2015 |
| BLAKE2b | 512 bits | Sûr, très rapide |
| BLAKE3 | 256 bits | Sûr, le plus rapide |

```python
import hashlib

# SHA-256
h = hashlib.sha256(b"message").hexdigest()

# Avec sel (pour les mots de passe — voir bcrypt/argon2)
sel = os.urandom(32)
h = hashlib.pbkdf2_hmac("sha256", b"mot_de_passe", sel, 600000)
```

### Hachage de mots de passe

Le hachage de mots de passe nécessite des fonctions **intentionnellement lentes** avec sel :

| Algorithme | Paramètres | Recommandation |
|---|---|---|
| `bcrypt` | work factor (coût) | Éprouvé, standard actuel |
| `scrypt` | N, r, p | Résistant aux GPUs (mémoire intensive) |
| `Argon2id` | memory, iterations, parallelism | Gagnant PHC 2015, recommandé OWASP |

```python
import bcrypt

sel = bcrypt.gensalt(rounds=12)
hash_mdp = bcrypt.hashpw(b"motdepasse", sel)
bcrypt.checkpw(b"motdepasse", hash_mdp)   # True
```

## Signatures numériques

Une signature numérique garantit authenticité et non-répudiation : seul le propriétaire de la clé privée peut signer, n'importe qui avec la clé publique peut vérifier.

```
Signer   : signature = sign(hash(message), clé_privée)
Vérifier : verify(hash(message), signature, clé_publique) → True/False
```

### RSA-PSS et ECDSA

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

# Génération d'une clé ECDSA (P-256)
cle_privee = ec.generate_private_key(ec.SECP256R1())
cle_publique = cle_privee.public_key()

# Signature
signature = cle_privee.sign(b"document", ec.ECDSA(hashes.SHA256()))

# Vérification
cle_publique.verify(signature, b"document", ec.ECDSA(hashes.SHA256()))
# Lève InvalidSignature si invalide
```

### Ed25519

Courbe de Bernstein — plus rapide, plus simple à implémenter correctement qu'ECDSA, résistante à certaines attaques par canaux cachés. Utilisée dans SSH, TLS 1.3, Signal.

## MAC (Message Authentication Code)

Un MAC vérifie l'intégrité et l'authenticité sans nécessiter de cryptographie asymétrique.

### HMAC

```
HMAC(K, m) = H((K ⊕ opad) || H((K ⊕ ipad) || m))
```

```python
import hmac, hashlib

cle = b"cle_secrete"
mac = hmac.new(cle, b"message", hashlib.sha256).hexdigest()

# Vérification à temps constant (évite les timing attacks)
hmac.compare_digest(mac, mac_recu)
```

## Infrastructure à Clé Publique (PKI)

La PKI résout le problème de distribution des clés publiques : comment savoir que la clé publique d'Alice appartient vraiment à Alice ?

```
Root CA (auto-signé, offline, très protégé)
└── CA intermédiaire (online, signe les certificats)
    └── Certificat du serveur (lié à un nom de domaine)
```

Un certificat X.509 contient :
- Clé publique du sujet
- Nom de domaine (Subject Alternative Names)
- Dates de validité
- Signature de la CA émettrice

```bash
# Inspecter un certificat
openssl x509 -in cert.pem -text -noout

# Générer une clé et un CSR (Certificate Signing Request)
openssl genrsa -out cle.pem 2048
openssl req -new -key cle.pem -out demande.csr

# Vérifier la chaîne de confiance
openssl verify -CAfile ca-chain.pem cert.pem

# Tester TLS d'un serveur
openssl s_client -connect exemple.fr:443 -brief
```

## Protocoles de sécurité

### TLS (Transport Layer Security)

TLS 1.3 (RFC 8446, 2018) supprime les algorithmes faibles et réduit la latence.

Algorithmes autorisés dans TLS 1.3 :
- **Échange de clés** : ECDHE (X25519, P-256), DHE
- **Authentification** : RSA-PSS, ECDSA, Ed25519
- **Chiffrement** : AES-128-GCM, AES-256-GCM, ChaCha20-Poly1305
- **Hash** : SHA-256, SHA-384

### JWT (JSON Web Token)

```
Header.Payload.Signature
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWxpY2UifQ.signature
```

Vulnérabilités communes :
- **`alg: none`** : certaines libs acceptent un JWT sans signature
- **Confusion RS256/HS256** : un JWT signé RS256 peut être falsifié si le serveur accepte HS256 avec la clé publique comme secret
- **Absence de vérification de l'expiration** (`exp`)

## PGP et sécurité des emails

**PGP (Pretty Good Privacy)** est un système de chiffrement asymétrique populaire pour les emails et fichiers. La clé publique est partagée librement ; la clé privée reste secrète.

Contrairement au chiffrement symétrique, PGP évite le problème d'échange de clé secrète sur un canal non sécurisé.

### Gpg4win (Windows)

Suite d'outils basés sur GnuPG supportant OpenPGP et S/MIME :

| Composant | Rôle |
|-----------|------|
| GnuPG | Moteur de chiffrement (OpenPGP) |
| Kleopatra | Interface de gestion des clés et certificats |
| GpgOL | Extension Microsoft Outlook |
| GpgEX | Extension Windows Explorer |
| Claws Mail | Client email intégrant GnuPG |

### Modèles d'authentification des clés publiques

| Modèle | Standard | Principe |
|--------|----------|----------|
| **Autorité centrale** | S/MIME | Clés authentifiées par une CA accréditée (hiérarchique) |
| **Web of trust** | OpenPGP | Les utilisateurs signent mutuellement leurs clés (décentralisé) |

### Signatures numériques (email)

Processus : `hash(message)` → chiffrement du hash avec la **clé privée** de l'émetteur → signature. Le destinataire déchiffre avec la clé publique et compare le hash.

Algorithmes supportés : RSA, DSA.

## Attaques cryptographiques courantes

| Attaque | Cible | Description |
|---|---|---|
| Brute force | Clés courtes, mots de passe | Essai exhaustif |
| Birthday attack | Fonctions de hachage | Chercher des collisions en O(√N) |
| Padding oracle | CBC sans MAC | Déduire le plaintext bit par bit via les erreurs de déchiffrement |
| Timing attack | Comparaisons de secrets | Mesurer le temps d'exécution pour inférer des bits |
| Downgrade attack | Protocoles (SSL/TLS) | Forcer une version plus ancienne et vulnérable |
| Side-channel | Implémentations matérielles | Consommation électrique, rayonnement EM, cache CPU |
| MITM | Échange de clés sans PKI | Intercepter et remplacer les clés publiques |

## Cryptographie Post-Quantique

Les ordinateurs quantiques, via l'algorithme de Shor, pourraient factoriser les grands entiers en temps polynomial — cassant RSA, DSA et ECDSA. L'algorithme de Grover réduit de moitié la sécurité des algorithmes symétriques (AES-128 → sécurité équivalente à ~64 bits).

**Horizon estimé :** un ordinateur quantique cryptographiquement pertinent (CRQC) dans 10-20 ans. La menace "harvest now, decrypt later" est immédiate : des données chiffrées aujourd'hui peuvent être collectées et déchiffrées plus tard.

### Algorithmes standardisés par le NIST (2024)

Le NIST a finalisé sa sélection d'algorithmes post-quantiques en 2024 après 8 ans de compétition :

| Algorithme | Type | Base mathématique | Usage |
|---|---|---|---|
| **CRYSTALS-Kyber (ML-KEM)** | KEM (échange de clés) | Lattices | Remplacement de ECDH/RSA pour l'échange de clés |
| **CRYSTALS-Dilithium (ML-DSA)** | Signature | Lattices | Remplacement de ECDSA/RSA-PSS |
| **FALCON (FN-DSA)** | Signature | NTRU Lattices | Signatures compactes (IoT, TLS) |
| **SPHINCS+ (SLH-DSA)** | Signature | Hash-based | Basé uniquement sur des fonctions de hachage |

**Problèmes des lattices :** dureté calculatoire basée sur le problème SVP (Shortest Vector Problem) et LWE (Learning With Errors) — résistants aux algorithmes quantiques connus.

### Hybridation (recommandée pendant la transition)

Combiner un algorithme classique et un algorithme post-quantique : la sécurité est garantie si l'un des deux tient.

```
TLS 1.3 hybride : X25519 (ECDH classique) + Kyber768 (post-quantique)
→ L'attaquant doit casser les deux simultanément
→ Google, Cloudflare, Signal ont déjà déployé des variantes hybrides
```

```python
# Kyber768 avec la librairie pqcrypto (exemple)
from pqcrypto.kem.kyber768 import generate_keypair, encrypt, decrypt

# Génération de clés
public_key, secret_key = generate_keypair()

# Encapsulation (échange de clé)
ciphertext, shared_secret_sender = encrypt(public_key)

# Décapsulation
shared_secret_receiver = decrypt(secret_key, ciphertext)

assert shared_secret_sender == shared_secret_receiver
# shared_secret peut servir de clé AES-256 pour le chiffrement symétrique
```

### Migration vers le post-quantique

```
Priorité de migration (ANSSI recommandations) :

1. Haute priorité (données sensibles à long terme) :
   → Données classifiées, données médicales, données financières
   → Commencer maintenant avec des solutions hybrides

2. Priorité moyenne :
   → PKI interne (rootCA, serveurs, code signing)
   → Renouveler les certificats avec algorithmes hybrides

3. Standard :
   → TLS pour le web (suivi par les navigateurs)
   → Suivre les déploiements des vendeurs

Inventaire à faire :
- Quels algorithmes asymétriques sont utilisés ? (RSA, ECDSA, DH)
- Où sont les données à longue durée de vie ?
- Quels systèmes ne peuvent pas être mis à jour ? (HSM, OT/ICS, IoT)
```

### Algorithmes symétriques : situation confortable

AES-256 reste sécurisé contre les ordinateurs quantiques (Grover réduit à 128 bits de sécurité effective — encore largement suffisant). SHA-256 est également considéré comme sûr.

```
Recommandation immédiate pour la symétrie :
AES-256-GCM (au lieu de AES-128) → déjà résistant au quantique
SHA-384 ou SHA-512 (au lieu de SHA-256) → marge de sécurité accrue
```
