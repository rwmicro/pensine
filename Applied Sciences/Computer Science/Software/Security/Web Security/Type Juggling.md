---
title: Type Juggling
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [type-juggling, php, javascript, python, web, sécurité, authentication-bypass]
date: 2026-03-22
---

# Type Juggling

Le type juggling exploite le comportement des langages à typage dynamique qui convertissent implicitement les types lors de comparaisons. Une comparaison "lâche" peut produire des résultats inattendus exploitables pour bypasser des vérifications.

## PHP — Comparaison lâche (`==`)

PHP est particulièrement affecté. L'opérateur `==` effectue des conversions de type avant de comparer.

### Table de vérités dangereuses

```php
// Comparaisons qui retournent TRUE de manière inattendue
var_dump(0 == "a");           // TRUE (PHP < 8.0) — "a" converti en 0
var_dump(0 == "");            // TRUE (PHP < 8.0)
var_dump(0 == "0abc");        // TRUE — "0abc" converti en 0
var_dump(0 == false);         // TRUE
var_dump(0 == null);          // TRUE
var_dump("1" == "01");        // TRUE — comparaison numérique
var_dump("10" == "1e1");      // TRUE — 1e1 = 10.0
var_dump(100 == "1e2");       // TRUE — 1e2 = 100
var_dump("" == null);         // TRUE
var_dump("" == false);        // TRUE
var_dump([] == false);        // TRUE
var_dump([] == null);         // TRUE
var_dump("0" == false);       // TRUE
var_dump("0" == null);        // FALSE (subtilité)

// PHP 8.0+ — comportement changé (0 == "a" → FALSE)
// Mais les autres cas persistent
```

### Bypass d'authentification

```php
// Code vulnérable — vérification de token avec ==
$token = hash('md5', $secret);  // Ex: "0e830400451993494058024219903391"

if ($_POST['token'] == $token) {
    // Authentifié
}

// Si le hash MD5 commence par "0e" suivi de chiffres → PHP l'interprète comme 0 × 10^n = 0
// Envoyer token = 0 → 0 == "0e8304..." → TRUE !
// Ou envoyer un autre hash "magic" commençant par 0e

// Hashes MD5 "magic" (s'évaluent à 0 en comparaison lâche)
"0e462097431906509019562988736854"  // MD5 de "240610708"
"0e830400451993494058024219903391"  // MD5 de "QNKCDZO"
"0e00275209979520536065071126608"   // MD5 de "aabg7XSs"

// SHA1 magic hashes
"0e07766915004133176347055865026311692244"  // SHA1 de "10932435112"
```

```php
// Autre bypass — si password_verify est remplacé par ==
$stored = "0";  // Hash stocké mal formaté
if ($stored == hash_password($input)) {
    // Si l'entrée produit un hash commençant par 0 → bypass
}

// Type juggling sur les comparaisons de tableau
var_dump("php" == 0);   // TRUE (PHP < 8)
var_dump([1,2,3] == 0); // FALSE
```

### Bypass de strcmp()

```php
// Code vulnérable
if (strcmp($_POST['password'], $real_password) == 0) {
    // Authentifié
}

// Si password est un tableau : strcmp(array, string) → NULL
// NULL == 0 → TRUE !
// Envoyer : password[]=anything (PHP convertit en tableau)
```

### Type juggling avec JSON et json_decode

```php
// Code vulnérable — authentification via JSON
$data = json_decode($json_input);

if ($data->password == $stored_password) {
    // Authentifié
}

// Envoyer : {"password": 0} → 0 == "anystring" → TRUE (PHP < 8)
// Envoyer : {"password": true} → true == "anystring" → TRUE
```

### Contournement de switch

```php
// switch utilise == implicitement
switch ($role) {
    case "admin":
        // ...
    case "user":
        // ...
}

// Si $role = 0 → 0 == "admin" → TRUE (PHP < 8) → accès admin !
```

## JavaScript

```javascript
// == (abstract equality) — conversions implicites
0 == ""           // true
0 == "0"          // true
0 == false        // true
"" == false       // true
null == undefined  // true
null == false      // FALSE (subtilité)
NaN == NaN         // FALSE (NaN n'est jamais égal à lui-même)

[] == false        // true ([] converti en "" puis en 0)
[] == 0            // true
[""] == false      // true
["1"] == 1         // true
["1","2"] == "1,2" // true

// parseInt — conversions inattendues
parseInt("10abc")  // 10 (s'arrête au premier non-numérique)
parseInt("0x1a")   // 26 (hex)
parseInt("010")    // En ES5 : 8 (octal) ! → utiliser parseInt("010", 10)
```

### Bypass en Node.js

```javascript
// Comparaison de hashes avec ==
const hash = crypto.createHash('sha256').update(secret).digest('hex');
// Si hash commence par "0e..." → avec un JSON {"hash": 0} → 0 == "0e..." → true
// (moins fréquent en JS car parseInt différent)

// Type coercion avec des objets
const obj = {valueOf: () => 1};
obj == 1  // true
obj == true  // true

// null et undefined
null > 0   // false
null == 0  // false
null >= 0  // TRUE (inconsistance JavaScript !)
```

## Python

```python
# Python est plus strict mais a quelques cas
0 == False   # True
1 == True    # True
0 == 0.0     # True
"" == False  # False (Python est strict ici)

# Égalité de None
None == False  # False
None == 0      # False

# Mais
bool([]) == False  # True
bool("") == False  # True
bool(0) == False   # True

# Flask/Django — confusion de types dans les comparaisons de sessions
# Si la session contient is_admin = "0" (string)
# et que le code fait : if session['is_admin'] == 0 → False (OK)
# mais : if not session['is_admin'] → "0" est truthy → pas de bypass ici
# Cependant : if session['is_admin'] == False → "0" != False en Python → OK
```

## Cas réels et impact

```
WordPress < 3.8.4 (2014) :
  Comparaison lâche du hash de confirmation d'email
  → Bypass via magic hash "0e" → account takeover

Drupal CVE-2019-6339 :
  Type juggling dans la comparaison de tokens de réinitialisation
  → Bypass via hash magic

CTF — challenges courants :
  JSON {"admin": true} envoyé à un endpoint qui compare avec ==
  PHP : paramètre tableau au lieu d'une string pour bypasser strcmp
  Hash magic : soumettre un "token" qui avec == vaut 0
```

## Contre-mesures

```php
// PHP — toujours utiliser === (comparaison stricte de type ET valeur)
if ($_POST['token'] === $token) { ... }   // Sûr
if (strcmp($a, $b) === 0) { ... }         // Sûr (=== 0, pas == 0)

// Vérifier le type avant de comparer
if (!is_string($_POST['password'])) {
    die("Type invalide");
}

// hash_equals() pour comparer des tokens (temps constant + strict)
if (hash_equals($expected_token, $_POST['token'])) { ... }

// password_verify() pour les mots de passe (jamais ==)
if (password_verify($_POST['password'], $stored_hash)) { ... }

// json_decode avec l'option assoc=true et valider les types
$data = json_decode($input, true);
if (!is_string($data['password'])) {
    die("Type invalide");
}
```

```javascript
// JavaScript — toujours utiliser ===
if (input === expected) { ... }  // Strict equality

// Node.js — crypto.timingSafeEqual pour les tokens
const crypto = require('crypto');
const a = Buffer.from(userToken);
const b = Buffer.from(storedToken);
if (a.length === b.length && crypto.timingSafeEqual(a, b)) { ... }
```
