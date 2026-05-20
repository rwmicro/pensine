---
title: Clickjacking et UI Redressing
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [clickjacking, ui-redressing, iframe, csp, sécurité, web]
date: 2026-03-22
---

# Clickjacking et UI Redressing

Le clickjacking (ou UI redressing) est une attaque qui trompe l'utilisateur en lui faisant cliquer sur des éléments d'une page qu'il ne voit pas, superposés sous une interface apparemment anodine.

## Principe

```html
<!-- Page de l'attaquant -->
<html>
<body>
  <!-- Interface visible : jeu ou formulaire innocent -->
  <div style="position: absolute; z-index: 1;">
    <p>Cliquez ici pour gagner un cadeau !</p>
    <button style="position: absolute; top: 150px; left: 200px;">CLIQUER</button>
  </div>

  <!-- Iframe invisible par-dessus : la vraie cible -->
  <iframe
    src="https://banque.com/virement?montant=500&dest=attaquant"
    style="opacity: 0;          /* invisible */
           position: absolute;
           z-index: 2;          /* au-dessus de l'interface visible */
           top: 100px;
           left: 150px;
           width: 300px;
           height: 200px;">
  </iframe>
</body>
</html>
```

La victime pense cliquer sur le bouton du jeu, mais clique en réalité sur le bouton "Confirmer le virement" de la banque, chargée dans l'iframe invisible.

## Variantes

### Likejacking

```html
<!-- Faire liker une page Facebook sans que l'utilisateur le sache -->
<iframe src="https://facebook.com/plugins/like.php?href=page_attaquant"
        style="opacity: 0; position: absolute; ...">
</iframe>
```

### Cursorjacking

Remplacer le curseur de la souris par un curseur décalé : l'utilisateur voit son curseur à un endroit mais clique à un autre endroit réel.

### Filejacking

```html
<!-- Forcer un clic sur "input type=file" pour ouvrir le sélecteur de fichiers -->
<!-- Puis piéger l'utilisateur pour qu'il glisse un fichier sensible -->
<input type="file" style="opacity: 0; position: absolute; ..." />
```

### Drag-and-drop jacking

Exploite les événements drag-and-drop pour faire glisser du contenu sensible (token, fichier) vers un contrôle contrôlé par l'attaquant.

### Multi-step clickjacking

```
Étape 1 : Clique ici → désactive l'authentification 2FA
Étape 2 : Clique ici → confirme le changement d'email
Étape 3 : Clique ici → confirme avec le bouton final
→ Compte compromis en 3 clics "innocents"
```

## Conditions requises

Pour qu'une page soit vulnérable au clickjacking :
1. La cible doit être embeddable dans un `<iframe>` (pas de `X-Frame-Options`)
2. L'action sensible ne doit pas nécessiter de saisie clavier
3. L'action sensible doit être possible depuis un compte authentifié (cookies envoyés dans l'iframe)

## Test de vulnérabilité

```bash
# Vérifier les en-têtes HTTP
curl -I https://site.com | grep -i "x-frame-options\|content-security-policy"

# Si aucun des deux n'est présent → potentiellement vulnérable

# Test HTML rapide
cat > test.html << 'EOF'
<html><body>
<iframe src="https://site.com/page-sensible" width="800" height="600"></iframe>
</body></html>
EOF
# Ouvrir dans le navigateur : si la page s'affiche dans l'iframe → vulnérable
```

```python
# Script de test automatisé
import requests

def check_clickjacking(url):
    r = requests.get(url)
    xfo = r.headers.get('X-Frame-Options', '').upper()
    csp = r.headers.get('Content-Security-Policy', '')

    if not xfo and 'frame-ancestors' not in csp:
        print(f"VULNERABLE: {url}")
        print("  Aucune protection contre le clickjacking")
    elif xfo in ('DENY', 'SAMEORIGIN'):
        print(f"PROTECTED (X-Frame-Options: {xfo}): {url}")
    elif 'frame-ancestors' in csp:
        print(f"PROTECTED (CSP frame-ancestors): {url}")
    else:
        print(f"WEAK ({xfo}): {url}")
```

## Relation avec CSRF

Le clickjacking peut contourner les protections CSRF dans certains cas :
- Si le token CSRF est transmis via un formulaire dans l'iframe, il reste valide
- Le clickjacking force la soumission du formulaire avec le token légitime de la victime

```
CSRF token présent → clickjacking peut quand même fonctionner
(si l'action peut être déclenchée par un seul clic)

Cookie SameSite=Strict → protège contre CSRF et réduit l'impact du clickjacking
(mais pas une protection absolue si le site est en même domaine)
```

## Contre-mesures

### X-Frame-Options (ancien, mais encore largement supporté)

```
X-Frame-Options: DENY           # Aucun iframe autorisé
X-Frame-Options: SAMEORIGIN     # Iframe autorisé uniquement depuis le même domaine
X-Frame-Options: ALLOW-FROM https://partenaire.com  # Déprécié, non supporté partout
```

```python
# Flask
@app.after_request
def set_xframe_options(response):
    response.headers['X-Frame-Options'] = 'DENY'
    return response

# Django (dans settings.py)
X_FRAME_OPTIONS = 'DENY'
```

### Content Security Policy — frame-ancestors (recommandé)

Plus flexible et moderne que X-Frame-Options.

```
Content-Security-Policy: frame-ancestors 'none';
Content-Security-Policy: frame-ancestors 'self';
Content-Security-Policy: frame-ancestors 'self' https://partenaire.com;
```

```python
# Flask — CSP complet
response.headers['Content-Security-Policy'] = (
    "default-src 'self'; "
    "frame-ancestors 'none';"  # Aucun embedding autorisé
)
```

### Frame busting JavaScript (déprécié et contournable)

```javascript
// Technique ancienne — ne pas utiliser seule
if (top !== self) {
    top.location = self.location;
}

// Facilement contournée avec l'attribut sandbox de l'iframe
<iframe src="cible.com" sandbox="allow-scripts">
// allow-scripts sans allow-top-navigation → le frame busting échoue
```

### Attribut sandbox (côté intégrateur)

```html
<!-- Si vous devez embarquer du contenu tiers de manière sécurisée -->
<iframe src="https://partenaire.com/widget"
        sandbox="allow-scripts allow-same-origin"
        <!-- sans allow-forms → les formulaires ne peuvent pas être soumis -->
        <!-- sans allow-top-navigation → ne peut pas rediriger la page parente -->
>
</iframe>
```

## Impact et reporting

Le clickjacking seul est souvent "medium" en bug bounty. Il monte en criticité quand :
- L'action forcée est un changement de mot de passe, email ou d'autres données de compte
- Il peut être chaîné pour un Account Takeover
- Il affecte des fonctions d'administration

Preuves à fournir dans un rapport :
```html
<!-- PoC minimal à fournir -->
<html>
<body style="background:grey;">
<p>Clickjacking PoC — [Nom Entreprise] — [Date]</p>
<p>La cible est chargée dans une iframe ci-dessous (normalement opacity:0)</p>
<iframe src="https://cible.com/action-sensible"
        style="opacity:0.5; border:2px solid red;"
        width="600" height="400">
</iframe>
</body>
</html>
```
