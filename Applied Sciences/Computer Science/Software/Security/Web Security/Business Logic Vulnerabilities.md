---
title: Business Logic Vulnerabilities
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [business-logic, logique-métier, web, bug-bounty, sécurité]
date: 2026-03-22
---

# Business Logic Vulnerabilities

Les vulnérabilités de logique métier sont des failles dans la conception et l'implémentation des flux applicatifs. Contrairement aux injections ou au XSS, elles ne sont pas détectables par des scanners automatiques — elles nécessitent de comprendre comment l'application est censée fonctionner, puis de trouver comment l'en faire dévier.

## Catégories principales

### 1. Manipulation de prix et de transactions

```
Scénarios :
- Modifier le prix d'un article dans la requête POST de paiement
- Appliquer des réductions en cascade non prévues
- Acheter avec un solde négatif
- Contourner la vérification de paiement

Test :
POST /checkout
{"item_id": 123, "quantity": 1, "price": 0.01}   # prix modifié
                                                    # si le serveur fait confiance au prix client

POST /checkout
{"item_id": 123, "quantity": -1}   # quantité négative → solde crédité ?
```

### 2. Contournement des étapes d'un workflow

```
Workflow normal :
1. /cart → 2. /shipping → 3. /payment → 4. /confirmation

Test : accéder directement à /confirmation sans passer par /payment
→ Si la commande est validée → contournement du paiement

Test : passer les étapes dans le mauvais ordre
/payment → /shipping → /confirmation
→ Certaines applications ne vérifient pas l'ordre
```

### 3. Abus de la logique de récompense

```
- Parrainage : créer des comptes fictifs pour accumuler des récompenses
- Cashback : acheter + retourner + garder le cashback
- Codes promo : réutiliser un code (voir Race Conditions.md)
- Points de fidélité : acheter, gagner des points, rembourser, garder les points
```

### 4. Manipulation des états

```
# État machine vulnérable
Commande : pending → processing → shipped → delivered

Test :
- Annuler une commande déjà "shipped" → remboursement sans retour ?
- Modifier une commande "processing" → changer l'adresse livraison après paiement
- Passer une commande de "pending" directement à "delivered" via API

PUT /orders/123/status
{"status": "delivered"}  # L'utilisateur peut-il modifier directement ?
```

### 5. Privilege escalation via paramètre

```
# Paramètre de rôle dans la requête
POST /register
{"username": "alice", "email": "alice@example.com", "role": "admin"}

# Modification de profil
PUT /users/me
{"email": "alice@example.com", "is_admin": true}

# Paramètre dans le JWT payload (si mal signé)
{"user": "alice", "role": "user"} → {"user": "alice", "role": "admin"}
```

### 6. Excessive Data Exposure (Mass Assignment)

```python
# Code vulnérable — assigne toutes les propriétés du JSON reçu
class User(Model):
    username = Column(String)
    email = Column(String)
    is_admin = Column(Boolean, default=False)

@app.route('/profile', methods=['PUT'])
def update_profile():
    data = request.json
    user.update(**data)  # ← Tout est accepté, y compris is_admin

# Payload d'exploit
PUT /profile
{"username": "alice", "is_admin": true}
```

### 7. Contournement des limites

```
# Limite de téléchargement
GET /download/file.zip
# Si la vérification est sur le nombre de clics (pas de tokens robustes) :
# Script qui clique 1000 fois → contourne la limite

# Limite de vues
GET /premium-content/1
# Modifier un cookie de comptage : views=0 → accès illimité

# Limite temporelle
# Modifier la date dans un cookie non signé
session_data = {"trial_started": "2020-01-01"}  # Forcer une date ancienne
```

### 8. Référence à des ressources non autorisées

```
# L'IDOR classique est simple, mais la logique métier peut créer des variantes :

# Accès via import/export
POST /export
{"report_type": "all_users"}   # Si l'utilisateur non-admin peut exporter

# Accès via fonctionnalité de partage
POST /share
{"item_id": 999, "share_with": "me@attaquant.com"}
# L'item 999 appartient à un autre utilisateur, mais la fonctionnalité de partage
# n'est pas soumise aux mêmes vérifications d'autorisation

# Accès via la recherche
GET /search?query=admin@site.com
# Retourne les commandes de admin@site.com → fuite de données
```

## Méthodologie de test

```
1. Mapper le workflow complet
   → Quelles sont les étapes ? Quelles requêtes sont envoyées ?
   → Quelles vérifications sont faites à chaque étape ?

2. Identifier les hypothèses implicites
   → "L'utilisateur ne modifiera pas les paramètres cachés"
   → "L'utilisateur suivra les étapes dans l'ordre"
   → "L'utilisateur ne passera pas deux commandes simultanément"

3. Tester chaque hypothèse
   → Modifier les paramètres (prix, quantité, rôle)
   → Sauter des étapes ou les inverser
   → Utiliser plusieurs onglets / sessions simultanées

4. Tester les cas limites
   → Valeurs négatives, zéro, très grandes valeurs
   → Chaînes vides, null, valeurs de type incorrect
   → États inattendus (commande annulée puis réactivée)

5. Tester avec plusieurs rôles
   → Actions d'admin réalisables depuis un compte normal
   → Actions d'un utilisateur A réalisables depuis le compte B
```

## Exemples réels (rendus publics)

```
- Twitter (2020) : API donnait accès au vrai nom de comptes pseudonymes
  via un endpoint de recherche non documenté

- Shopify (2019) : bug bounty $5000
  Ajouter des items à une commande d'un autre marchand

- HackerOne (2019) : manipulation de paramètre de prix
  dans un workflow de soumission de rapport

- Uber (2016) : codes promo applicables un nombre illimité de fois
  (sans race condition → simple réutilisation)
```

## Rapport et impact

Les vulnérabilités de logique métier sont souvent bien rémunérées car :
- Non détectables par les scanners automatiques
- Requièrent une vraie compréhension de l'application
- Peuvent avoir un impact financier direct et mesurable

```
Structure de rapport :
1. Résumé : "Un attaquant peut acheter des articles pour 0,01€"
2. Étapes précises de reproduction
3. Impact business (ex: "Perte potentielle illimitée de revenus")
4. Preuve (captures d'écran ou logs de la requête modifiée)
5. Remédiation suggérée
```
