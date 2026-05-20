---
title: "DevSecOps Pipeline (CI/CD Security)"
domain: "Applied Sciences"
subdomain: "Computer Science > DevSecOps > CI-CD"
tags: [sciences-appliquées, informatique, devsecops]
date: "2026-02-25"
---

# DevSecOps Pipeline (CI/CD Security)

Le DevSecOps intègre la sécurité dans chaque étape du pipeline CI/CD plutôt que de l'appliquer uniquement à la fin. L'objectif est de détecter les vulnérabilités le plus tôt possible ("shift left") quand leur correction est moins coûteuse.

## Philosophie Shift Left

```
Traditionnel : Code → Build → Test → Deploy → [Sécurité]
DevSecOps    : [Sécurité] à chaque étape du pipeline
```

Le coût de correction d'une vulnérabilité multiplie par 10 à chaque étape :
- Trouvée pendant le développement : 1x
- Trouvée en test : 10x
- Trouvée en production : 100x

## Étapes du pipeline sécurisé

```
Commit → SAST → SCA → Build → DAST → Image Scan → Deploy → RASP/monitoring
  ↑         ↑      ↑      ↑      ↑         ↑
Secrets  Linting  CVE  Artefact  API      Container
Scan    statique  Deps  signing  Tests    vulns
```

## 1. Pre-commit (poste du développeur)

### Détection de secrets

Empêcher le commit de secrets (clés API, tokens, mots de passe) dans le dépôt.

```bash
# git-secrets (AWS)
git secrets --install
git secrets --register-aws

# gitleaks — analyse le dépôt complet ou les diffs
gitleaks detect --source . --verbose
gitleaks protect --staged   # hook pre-commit

# detect-secrets (Yelp) — baseline + audit
detect-secrets scan > .secrets.baseline
detect-secrets audit .secrets.baseline
```

Configuration `.gitleaks.toml` :
```toml
[rules]
  [[rules.rules]]
    description = "AWS Access Key"
    regex = '''AKIA[0-9A-Z]{16}'''
    tags = ["aws", "credentials"]

[allowlist]
  paths = [".secrets.baseline"]
  regexes = ["EXAMPLE_KEY_.*"]
```

### Linting de sécurité

```bash
# Bash : shellcheck
shellcheck script.sh

# Python : bandit (détecte les mauvaises pratiques de sécurité)
bandit -r ./src -ll    # -ll = sévérité medium et haute uniquement

# Terraform : tfsec, checkov
tfsec .
checkov -d . --framework terraform

# Docker : hadolint
hadolint Dockerfile
```

## 2. SAST (Static Application Security Testing)

Analyse le code source sans l'exécuter.

### Outils

| Outil | Langages | Type |
|---|---|---|
| **Semgrep** | 30+ langages | Open source, règles personnalisables |
| **SonarQube / SonarCloud** | 30+ | Open core, intégration IDE |
| **CodeQL** (GitHub) | C/C++, Java, Python, JS... | Requêtes logiques sur l'AST |
| **Checkmarx** | Entreprise | Commercial |
| **Snyk Code** | 30+ | Commercial (tier gratuit) |
| **Bandit** | Python | Open source |
| **SpotBugs + FindSecBugs** | Java | Open source |

### Semgrep en pratique

```bash
# Scan avec les règles de sécurité de la communauté
semgrep --config p/security-audit .
semgrep --config p/owasp-top-ten .
semgrep --config p/python .

# Règle personnalisée
cat > regles/no-hardcoded-creds.yaml << 'EOF'
rules:
  - id: no-hardcoded-password
    patterns:
      - pattern: password = "..."
      - pattern-not: password = ""
    message: "Hardcoded password detected: $MATCH"
    severity: ERROR
    languages: [python]
EOF

semgrep --config regles/ .
```

### CodeQL (GitHub Actions)

```yaml
# .github/workflows/codeql.yml
name: CodeQL Analysis
on: [push, pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python, javascript
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
```

## 3. SCA (Software Composition Analysis)

Analyse les dépendances tierces pour détecter les CVEs connues.

### Outils

| Outil | Type | Notes |
|---|---|---|
| **OWASP Dependency-Check** | Open source | Java, .NET, Python, Node |
| **Snyk** | Commercial (tier gratuit) | Fix automatique, PR |
| **Trivy** | Open source | Dépendances + images Docker |
| **Renovate / Dependabot** | Open source | Mise à jour automatique des dépendances |

```bash
# Trivy — scan des dépendances Python
trivy fs --security-checks vuln requirements.txt

# OWASP Dependency-Check
dependency-check --project "MonApp" --scan ./src --format HTML

# Snyk
snyk test --severity-threshold=high
snyk monitor   # enregistre le projet pour monitoring continu
```

### Intégration GitLab CI

```yaml
# .gitlab-ci.yml
dependency_scan:
  image: owasp/dependency-check:latest
  stage: test
  script:
    - /usr/share/dependency-check/bin/dependency-check.sh
        --project "MonApp"
        --scan .
        --format JSON
        --failOnCVSS 7
  artifacts:
    reports:
      dependency_scanning: dependency-check-report.json
  allow_failure: false
```

## 4. Signature des artefacts

Garantir l'intégrité des artefacts tout au long de la supply chain.

```bash
# Signer une image Docker avec Cosign (Sigstore)
cosign generate-key-pair
cosign sign --key cosign.key monregistre.io/monapp:1.0

# Vérifier
cosign verify --key cosign.pub monregistre.io/monapp:1.0

# SBOM (Software Bill of Materials) — inventaire de toutes les dépendances
syft monregistre.io/monapp:1.0 -o spdx-json > sbom.json
grype sbom:sbom.json   # scanner les CVEs depuis le SBOM
```

## 5. DAST (Dynamic Application Security Testing)

Teste l'application en cours d'exécution, en envoyant des requêtes malveillantes.

```yaml
# OWASP ZAP en mode API scan
zap_scan:
  image: zaproxy/zap-stable
  stage: dast
  script:
    - zap-api-scan.py
        -t https://staging.monapp.com/api/openapi.json
        -f openapi
        -r zap-report.html
        -x zap-report.xml
        -l PASS
  artifacts:
    paths: [zap-report.html]
```

```bash
# Nikto — scan de serveur web
nikto -h https://staging.monapp.com -o nikto-report.html

# sqlmap — test d'injection SQL (environnement autorisé uniquement)
sqlmap -u "https://staging.monapp.com/api/users?id=1" --level=3
```

## 6. Scan d'images Docker

```yaml
# GitLab CI — scan Trivy
container_scan:
  image: aquasec/trivy:latest
  stage: scan
  script:
    - trivy image
        --exit-code 1
        --severity CRITICAL,HIGH
        --no-progress
        --format table
        $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  allow_failure: false
```

```bash
# Rapport JSON pour intégration
trivy image --format json --output trivy-report.json monapp:latest

# Vérifier la configuration du Dockerfile
trivy config Dockerfile

# Scan du filesystem complet
trivy fs --security-checks vuln,config .
```

## 7. Pipeline GitLab CI complet

```yaml
stages:
  - secrets
  - sast
  - sca
  - build
  - scan
  - dast
  - deploy

secrets_detection:
  stage: secrets
  image: zricethezav/gitleaks:latest
  script:
    - gitleaks detect --source . --exit-code 1

semgrep_sast:
  stage: sast
  image: returntocorp/semgrep:latest
  script:
    - semgrep --config p/security-audit --error .

dependency_check:
  stage: sca
  image: owasp/dependency-check
  script:
    - dependency-check.sh --project app --scan . --failOnCVSS 7

build_image:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

trivy_scan:
  stage: scan
  image: aquasec/trivy
  script:
    - trivy image --exit-code 1 --severity CRITICAL $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

zap_dast:
  stage: dast
  image: zaproxy/zap-stable
  script:
    - zap-api-scan.py -t $STAGING_URL/openapi.json -f openapi -l PASS

deploy_prod:
  stage: deploy
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  when: manual
  only:
    - main
```

## Supply Chain Security

La compromission de la chaîne d'approvisionnement logicielle (SolarWinds, XZ Utils, Log4Shell) est une menace majeure.

### SLSA (Supply chain Levels for Software Artifacts)

Framework de niveaux de sécurité pour la supply chain :

| Niveau | Exigences |
|---|---|
| SLSA 1 | Build scriptable, provenance générée |
| SLSA 2 | Build service (CI), provenance signée |
| SLSA 3 | Build isolé, pas de modification possible des sources pendant le build |
| SLSA 4 | Build hermétique, revue de code à deux personnes |

### Bonnes pratiques supply chain

```yaml
# Épingler les actions GitHub par digest SHA (pas par tag)
# Mauvais (le tag peut être modifié)
- uses: actions/checkout@v4

# Bon (digest immuable)
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

# Épingler les images Docker par digest dans les Dockerfiles
FROM python:3.12-slim@sha256:abc123...

# SBOM pour chaque artefact livré
- uses: anchore/sbom-action@v0
  with:
    image: ${{ env.IMAGE }}
    artifact-name: sbom.spdx.json
```

## Métriques de sécurité pipeline

| Métrique | Description |
|---|---|
| Vulnérabilités détectées/sprint | Tendance de la dette de sécurité |
| Mean Time to Fix (MTTF) vulnérabilité | Vitesse de remédiation |
| % builds bloqués par sécurité | Adoption réelle du shift left |
| Couverture SCA | % dépendances analysées |
| Secrets exposés détectés | Nombre de commits bloqués par pre-commit |
