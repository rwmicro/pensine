---
title: "Kubernetes — Fonctionnement"
domain: "Applied Sciences"
subdomain: "Computer Science > DevSecOps > Kubernetes"
tags: [sciences-appliquées, informatique, devsecops, kubernetes]
date: "2025-05-04"
---

# Kubernetes — Fonctionnement

Kubernetes (K8s) est un **orchestrateur de conteneurs** : il automatise le déploiement, la montée en charge et la gestion des applications conteneurisées (Docker, etc.).

En résumé : là où Docker gère un conteneur sur une machine, Kubernetes gère des dizaines de conteneurs sur des dizaines de machines.

> [!important] Ce que Kubernetes garantit vraiment
> Kubernetes ne fait pas juste "démarrer des conteneurs" — il maintient en continu un **état désiré** : si un Pod meurt, un nœud tombe, ou une image doit changer, le Controller Manager corrige l'écart automatiquement, sans intervention humaine. C'est cette boucle de réconciliation permanente, pas le simple déploiement initial, qui est le cœur du système.

## Architecture

Kubernetes fonctionne avec un **cluster** composé de deux types de machines :

### Control Plane (cerveau)
Le cerveau du cluster, qui prend toutes les décisions.

| Composant | Rôle |
|-----------|------|
| **API Server** | Point d'entrée unique — toutes les commandes passent par lui |
| **etcd** | Base de données clé-valeur — stocke l'état du cluster |
| **Scheduler** | Décide sur quel nœud placer chaque Pod |
| **Controller Manager** | Surveille l'état et corrige les écarts (ex: relance un pod mort) |

### Worker Nodes (bras)
Les machines qui font tourner les applications.

| Composant | Rôle |
|-----------|------|
| **kubelet** | Agent sur chaque nœud, dialogue avec le Control Plane |
| **kube-proxy** | Gère le réseau entre Pods |
| **Container Runtime** | Lance les conteneurs (Docker, containerd, CRI-O) |


## Les objets principaux

### Pod
L'unité de base. Un Pod = un ou plusieurs conteneurs qui partagent réseau et stockage.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mon-pod
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
```

### Deployment
Gère les Pods : assure qu'il y en a toujours le bon nombre, gère les mises à jour.

> [!tip] Pourquoi ne jamais créer un Pod nu en production
> Un Pod créé directement n'est surveillé par aucun contrôleur — s'il meurt, rien ne le relance. Un Deployment ajoute cette surveillance (via un ReplicaSet) et gère en plus les mises à jour progressives et le rollback. Un Pod nu n'a de sens que pour du débogage ponctuel.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mon-app
spec:
  replicas: 3          # 3 copies du Pod
  selector:
    matchLabels:
      app: mon-app
  template:
    metadata:
      labels:
        app: mon-app
    spec:
      containers:
      - name: mon-app
        image: mon-image:v1
```

### Service
Expose les Pods sur le réseau (ils ont des IPs changeantes — le Service donne une IP stable).

| Type | Usage |
|------|-------|
| ClusterIP | Accessible seulement dans le cluster |
| NodePort | Accessible depuis l'extérieur via un port du nœud |
| LoadBalancer | Crée un load balancer cloud |

### ConfigMap & Secret
- **ConfigMap** : configuration non sensible (variables d'env, fichiers config)
- **Secret** : données sensibles (mots de passe, tokens) — encodées en base64

> [!warning] Piège
> Base64 est un **encodage**, pas un chiffrement — n'importe qui avec un accès en lecture au Secret peut le décoder en une commande (`base64 -d`). Un Secret Kubernetes natif protège seulement contre une lecture accidentelle, pas contre un accès malveillant à etcd ou à l'API. Voir [[Sécurité Kubernetes]] pour les vraies protections (chiffrement etcd, Vault).

### Namespace
Isolation logique dans le cluster (comme des dossiers pour organiser les ressources).


## Cycle de vie d'un déploiement

```
kubectl apply -f deployment.yaml
    ↓
API Server reçoit la demande
    ↓
Scheduler choisit les nœuds
    ↓
kubelet lance les conteneurs sur les nœuds
    ↓
Controller Manager surveille — relance si crash
    ↓
Service route le trafic vers les Pods sains
```


## Commandes essentielles

```bash
# Voir l'état du cluster
kubectl get nodes
kubectl get pods
kubectl get pods -A              # Tous les namespaces
kubectl get services

# Déployer
kubectl apply -f fichier.yaml

# Voir les logs
kubectl logs nom-du-pod
kubectl logs -f nom-du-pod       # En temps réel

# Entrer dans un pod
kubectl exec -it nom-du-pod -- /bin/bash

# Supprimer
kubectl delete pod nom-du-pod
kubectl delete -f fichier.yaml

# Scaler un déploiement
kubectl scale deployment mon-app --replicas=5
```
