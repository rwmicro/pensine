---
title: "Sécurité Kubernetes"
domain: "Applied Sciences"
subdomain: "Computer Science > DevSecOps > Kubernetes"
tags: [sciences-appliquées, informatique, devsecops, kubernetes]
date: "2025-05-04"
---

# Sécurité Kubernetes

La sécurité Kubernetes se structure selon le modèle des **4C** : Cloud, Cluster, Container, Code. Chaque couche doit être sécurisée indépendamment — une vulnérabilité au niveau Code peut être atténuée par les couches supérieures, mais une mauvaise configuration Cluster expose toutes les applications.

## Modèle des 4C

```
Cloud (fournisseur, réseau physique, IAM cloud)
└── Cluster (API server, etcd, nœuds, RBAC)
    └── Container (image, runtime, isolation)
        └── Code (application, dépendances, secrets)
```

## RBAC (Role-Based Access Control)

RBAC contrôle qui peut faire quoi sur quelles ressources dans le cluster.

### Concepts

| Objet | Portée | Description |
|---|---|---|
| `Role` | Namespace | Permissions sur des ressources dans un namespace |
| `ClusterRole` | Cluster | Permissions sur des ressources cluster-wide (Nodes, PV...) |
| `RoleBinding` | Namespace | Attache un Role à un sujet (User, Group, ServiceAccount) |
| `ClusterRoleBinding` | Cluster | Attache un ClusterRole à un sujet globalement |

```yaml
# Role : autoriser la lecture des pods dans le namespace "prod"
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: prod
  name: lecteur-pods
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]

# RoleBinding : attacher ce Role à un ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: prod
  name: lecteur-pods-binding
subjects:
  - kind: ServiceAccount
    name: monitoring-sa
    namespace: prod
roleRef:
  kind: Role
  name: lecteur-pods
  apiGroup: rbac.authorization.k8s.io
```

### Principe du moindre privilège

```yaml
# Mauvaise pratique : droits wildcard
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]

# Bonne pratique : permissions minimales et explicites
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list"]
```

Vérifier les permissions d'un sujet :
```bash
kubectl auth can-i list pods --namespace prod --as system:serviceaccount:prod:monitoring-sa
kubectl auth can-i --list --namespace prod
```

## Network Policies

Par défaut, tous les pods peuvent communiquer entre eux. Les Network Policies définissent des règles de pare-feu au niveau des pods.

```yaml
# Politique : par défaut, bloquer tout le trafic entrant dans le namespace "prod"
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: prod
spec:
  podSelector: {}    # s'applique à tous les pods du namespace
  policyTypes:
    - Ingress

# Autoriser uniquement le trafic venant du namespace "frontend" vers les pods backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: prod
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: frontend
          podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

Les Network Policies nécessitent un CNI qui les supporte (Calico, Cilium, Weave — mais pas Flannel en configuration basique).

## Pod Security et SecurityContext

### SecurityContext au niveau Pod et Container

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-securise
spec:
  securityContext:
    runAsNonRoot: true         # le container ne peut pas tourner en root
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 2000              # groupe propriétaire des volumes montés
    seccompProfile:
      type: RuntimeDefault     # profil seccomp par défaut du runtime
  containers:
    - name: app
      image: monapp:1.0
      securityContext:
        allowPrivilegeEscalation: false   # impossible de devenir root (sudo, setUID)
        readOnlyRootFilesystem: true       # filesystem en lecture seule
        capabilities:
          drop: ["ALL"]                    # supprimer toutes les capabilities Linux
          add: ["NET_BIND_SERVICE"]        # n'ajouter que ce qui est strictement nécessaire
      volumeMounts:
        - name: tmp
          mountPath: /tmp                  # monter /tmp en écriture si readOnlyRootFilesystem
  volumes:
    - name: tmp
      emptyDir: {}
```

### Pod Security Admission (PSA) — remplacement de PodSecurityPolicy

PSA définit trois niveaux de sécurité appliqués par namespace :

| Niveau | Description |
|---|---|
| `privileged` | Aucune restriction |
| `baseline` | Empêche les configurations les plus dangereuses |
| `restricted` | Conformité maximale (non-root, capabilities droppées, seccomp) |

```bash
# Appliquer le niveau "restricted" au namespace "prod"
kubectl label namespace prod pod-security.kubernetes.io/enforce=restricted
kubectl label namespace prod pod-security.kubernetes.io/audit=restricted
kubectl label namespace prod pod-security.kubernetes.io/warn=restricted
```

## Gestion des secrets

### Problèmes avec les Secrets Kubernetes natifs

Les `Secret` Kubernetes sont encodés en base64 (pas chiffrés) et stockés en clair dans etcd par défaut.

```bash
# Un Secret est trivial à décoder
kubectl get secret mon-secret -o jsonpath='{.data.password}' | base64 -d
```

### Chiffrement at-rest de etcd

```yaml
# EncryptionConfiguration à passer à l'API server (--encryption-provider-config)
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <clé base64 de 32 octets>
      - identity: {}   # fallback pour la lecture des secrets non chiffrés
```

### Alternatives recommandées

| Outil | Approche |
|---|---|
| **HashiCorp Vault** | Serveur de secrets externe, rotation automatique |
| **External Secrets Operator** | Sync depuis Vault/AWS SM/Azure KV vers des Secrets K8s |
| **Sealed Secrets** (Bitnami) | Chiffrement asymétrique — le Secret chiffré peut être versionné dans git |
| **AWS Secrets Manager + IRSA** | Intégration native AWS pour les pods EKS |

## Sécurité des images

```bash
# Scanner une image avec Trivy (Aqua Security)
trivy image nginx:1.25
trivy image --severity CRITICAL,HIGH monapp:latest

# Intégration dans un pipeline CI
trivy image --exit-code 1 --severity CRITICAL monapp:$TAG
# exit-code 1 fait échouer le pipeline si des CVE critiques sont trouvées

# Vérifier la signature d'une image (Cosign)
cosign verify --certificate-identity keyless@cosign.dev \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  ghcr.io/org/image@sha256:...
```

Bonnes pratiques pour les images :
- Utiliser des images de base minimales (distroless, Alpine)
- Ne pas exécuter en root dans le container
- Épingler les images par digest SHA256 plutôt que par tag mutable
- Mettre en place un registre privé avec contrôle d'accès

## Audit Logs

Les audit logs de l'API server tracent toutes les requêtes.

```yaml
# Politique d'audit basique
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: None
    resources:
      - group: ""
        resources: ["events"]    # ne pas logger les events (trop verbeux)

  - level: Metadata
    resources:
      - group: ""
        resources: ["secrets", "configmaps"]

  - level: RequestResponse
    verbs: ["create", "update", "patch", "delete"]
    resources:
      - group: "rbac.authorization.k8s.io"
        resources: ["roles", "rolebindings", "clusterroles", "clusterrolebindings"]

  - level: Request
    omitStages: ["RequestReceived"]
```

Niveaux d'audit : `None` (rien) < `Metadata` (qui, quoi, quand) < `Request` (+ corps requête) < `RequestResponse` (+ corps réponse).

## Kubescape

Kubescape (ARMO) scanne un cluster ou des manifestes contre les benchmarks NSA/CISA et CIS.

```bash
# Installer
curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash

# Scanner le cluster courant
kubescape scan

# Scanner contre un framework spécifique
kubescape scan framework nsa
kubescape scan framework cis-aks-t1.2.0

# Scanner des manifestes avant déploiement
kubescape scan *.yaml

# Rapport HTML
kubescape scan --format html --output rapport.html
```

## Bonnes pratiques — récapitulatif

| Domaine | Pratique |
|---|---|
| RBAC | Moindre privilège, éviter les ClusterAdmin, auditer régulièrement |
| Réseau | Network Policies default-deny, segmenter par namespace |
| Pods | Non-root, readOnlyRootFilesystem, capabilities DROP ALL |
| Secrets | Chiffrement etcd at-rest + solution externe (Vault, ESO) |
| Images | Scanner les CVE, distroless, digest SHA256 |
| API server | Audit logs activés, désactiver l'accès anonyme |
| etcd | Chiffrement at-rest, TLS mutuel, accès réseau restreint |
| Nœuds | CIS Benchmark, mises à jour régulières du kubelet |
