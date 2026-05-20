---
title: "Kubernetes (K8s)"
domain: "Applied Sciences"
subdomain: "Computer Science > DevSecOps > Kubernetes"
tags: [sciences-appliquées, informatique, devsecops, kubernetes]
date: "2026-02-04"
---

# Kubernetes (K8s)

## Vue d'ensemble

Kubernetes est une plateforme open-source d'orchestration de conteneurs qui automatise le déploiement, la mise à l'échelle et la gestion d'applications conteneurisées.

## Architecture

### Composants du Control Plane

**API Server (kube-apiserver)**
- Point d'entrée du cluster
- Expose l'API Kubernetes
- Authentification et autorisation

**etcd**
- Base de données clé-valeur distribuée
- Stocke l'état du cluster

**Scheduler (kube-scheduler)**
- Assigne les Pods aux Nodes
- Prend en compte ressources et contraintes

**Controller Manager (kube-controller-manager)**
- Exécute les contrôleurs
- Maintient l'état désiré

**Cloud Controller Manager**
- Interface avec le cloud provider
- Gestion load balancers, volumes, etc.

### Composants des Nodes

**Kubelet**
- Agent sur chaque node
- Gère les Pods et conteneurs

**Kube-proxy**
- Proxy réseau
- Maintient les règles réseau

**Container Runtime**
- Docker, containerd, CRI-O
- Exécute les conteneurs

## Objets Kubernetes

### Pod

Plus petite unité déployable

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
```

### Deployment

Gère les ReplicaSets et Pods

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

### Service

Expose des Pods au réseau

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

**Types de Service:**
- **ClusterIP** (défaut) - IP interne au cluster
- **NodePort** - Expose sur port de chaque node
- **LoadBalancer** - Crée un LB externe
- **ExternalName** - Mapping DNS

### ConfigMap

Configuration découplée

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgres://db:5432"
  log_level: "info"
```

### Secret

Données sensibles encodées

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: cGFzc3dvcmQxMjM=  # base64
```

### PersistentVolume & PersistentVolumeClaim

**PersistentVolume (PV)**
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-data
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data"
```

**PersistentVolumeClaim (PVC)**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### Namespace

Isolation logique

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
```

## Commandes kubectl

### Gestion de base

```bash
# Info cluster
kubectl cluster-info

# Nodes du cluster
kubectl get nodes

# Tous les objets
kubectl get all

# Détails d'un objet
kubectl describe pod nom-pod

# Créer depuis fichier
kubectl apply -f deployment.yaml

# Supprimer
kubectl delete -f deployment.yaml
```

### Pods

```bash
# Lister pods
kubectl get pods
kubectl get pods -n namespace

# Logs d'un pod
kubectl logs nom-pod
kubectl logs -f nom-pod  # follow

# Shell dans pod
kubectl exec -it nom-pod -- /bin/bash

# Port forward
kubectl port-forward pod/nom-pod 8080:80
```

### Deployments

```bash
# Créer deployment
kubectl create deployment nginx --image=nginx

# Scaler
kubectl scale deployment nginx --replicas=5

# Mise à jour image
kubectl set image deployment/nginx nginx=nginx:1.22

# Rollout status
kubectl rollout status deployment/nginx

# Rollback
kubectl rollout undo deployment/nginx

# Historique
kubectl rollout history deployment/nginx
```

### Services

```bash
# Exposer un deployment
kubectl expose deployment nginx --port=80 --type=LoadBalancer

# Lister services
kubectl get services
```

### ConfigMaps & Secrets

```bash
# Créer ConfigMap
kubectl create configmap app-config --from-literal=key=value

# Créer Secret
kubectl create secret generic db-secret --from-literal=password=secret

# Voir contenu
kubectl get configmap app-config -o yaml
```

### Debugging

```bash
# Événements
kubectl get events

# Top (ressources)
kubectl top nodes
kubectl top pods

# Décrire pour debug
kubectl describe pod nom-pod
```

## Gestion de configuration

### Helm

Package manager pour Kubernetes

```bash
# Installer chart
helm install myapp stable/nginx

# Lister releases
helm list

# Mettre à jour
helm upgrade myapp stable/nginx

# Désinstaller
helm uninstall myapp
```

### Kustomize

Customisation de YAML sans templates

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
patchesStrategicMerge:
  - patch.yaml
```

```bash
kubectl apply -k ./
```

## Networking

### Ingress

Routage HTTP/HTTPS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
```

### Network Policies

Contrôle du trafic réseau

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow
spec:
  podSelector:
    matchLabels:
      app: api
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
```

## Scaling

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Pod Autoscaler (VPA)

Ajuste ressources CPU/mémoire

### Cluster Autoscaler

Ajoute/retire des nodes selon la charge

## Stratégies de déploiement

### Rolling Update (défaut)

Mise à jour progressive

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

### Blue-Green

Deux environnements, switch instantané

### Canary

Déploiement progressif à un sous-ensemble

## Sécurité

### RBAC (Role-Based Access Control)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

### Pod Security

- Security Context
- Pod Security Policies
- Pod Security Standards

### Secrets Management

- Kubernetes Secrets
- External Secrets Operator
- Sealed Secrets
- Vault integration

## Monitoring

### Métriques natives

```bash
kubectl top nodes
kubectl top pods
```

### Stack de monitoring

- **Prometheus** - Métriques
- **Grafana** - Visualisation
- **Alertmanager** - Alertes

### Logging

- **EFK Stack** (Elasticsearch, Fluentd, Kibana)
- **PLG Stack** (Prometheus, Loki, Grafana)

## Distributions Kubernetes

- **Minikube** - Local, développement
- **K3s** - Léger, Edge/IoT
- **Kind** - Kubernetes in Docker
- **EKS** - AWS Elastic Kubernetes Service
- **GKE** - Google Kubernetes Engine
- **AKS** - Azure Kubernetes Service
- **OpenShift** - Red Hat

## Best Practices

### Resource Management

```yaml
spec:
  containers:
  - name: app
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

### Health Checks

```yaml
spec:
  containers:
  - name: app
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
```

### Labels et Annotations

```yaml
metadata:
  labels:
    app: nginx
    env: production
    version: v1.0
  annotations:
    description: "Main web server"
```

## Outils essentiels

- **kubectl** - CLI officiel
- **k9s** - Terminal UI
- **Lens** - Desktop IDE
- **Stern** - Multi-pod log tailing
- **kubectx/kubens** - Context/namespace switching

## Ressources

- [Documentation officielle](https://kubernetes.io/docs)
- Kubernetes Academy
- CNCF Training
- KubeCon conférences

## Sujets à approfondir

- [ ] Service Mesh (Istio, Linkerd)
- [ ] GitOps (ArgoCD, Flux)
- [ ] Operators
- [ ] StatefulSets
- [ ] DaemonSets
- [ ] Jobs et CronJobs


*Dernière mise à jour: 2026-01-01*
