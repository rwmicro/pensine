---
title: "Kubernetes (K8s)"
domain: "Applied Sciences"
subdomain: "Computer Science > DevSecOps > Kubernetes"
tags: [sciences-appliquées, informatique, devsecops, kubernetes]
date: "2026-02-04"
prerequis: ["[[Docker]]"]
---

# Kubernetes (K8s)

Au début des années 2010, Google fait déjà tourner des milliards de conteneurs par semaine, sur des centaines de milliers de machines, grâce à un système interne nommé Borg. Aucun humain ne décide sur quel serveur tourne tel service : on déclare ce qu'on veut, et Borg se débrouille, relançant ailleurs ce qui tombe en panne. En 2014, des ingénieurs de Google en publient une réécriture ouverte, **Kubernetes** (du grec *kubernêtês*, « timonier », abrégé en K8s pour les huit lettres entre le K et le s), puis la confient en 2015 à une fondation neutre, la CNCF. Dix ans plus tard, c'est la plateforme standard pour orchestrer des conteneurs.

Là où [[Docker]] fait tourner des conteneurs sur une machine, Kubernetes les gère sur une flotte de machines : il décide où les placer, les redémarre quand ils tombent, répartit le trafic entre eux, ajuste leur nombre selon la charge et les met à jour sans interruption.

## Le principe : déclarer un état désiré

Kubernetes ne fonctionne pas par commandes (« lance trois serveurs web ») mais par déclarations (« je veux qu'il y ait en permanence trois serveurs web »). On décrit l'état désiré dans des fichiers YAML, on les soumet au cluster, et des **contrôleurs** comparent sans cesse l'état réel à cet état désiré pour corriger les écarts. Si un nœud tombe et emporte un des trois serveurs, le contrôleur constate qu'il n'en reste que deux et en recrée un ailleurs. Cette boucle de réconciliation est la clé de tout le reste.

## L'architecture d'un cluster

Un cluster se compose d'un **plan de contrôle** (*control plane*), qui prend les décisions, et de **nœuds** (*nodes*), qui exécutent les conteneurs.

Au cœur du plan de contrôle se trouve l'**API Server** (`kube-apiserver`) : c'est le seul point d'entrée, que l'on passe par `kubectl` ou par un autre outil, et il se charge de l'authentification et des autorisations. L'état du cluster est stocké dans **etcd**, une base clé-valeur distribuée et répliquée : perdre etcd, c'est perdre le cluster, d'où l'importance de le sauvegarder. Le **Scheduler** choisit sur quel nœud placer chaque nouveau Pod, en fonction des ressources disponibles et des contraintes déclarées. Le **Controller Manager** fait tourner les contrôleurs qui maintiennent l'état désiré, et le **Cloud Controller Manager** dialogue avec le fournisseur de cloud pour créer des load balancers ou des disques.

Sur chaque nœud tourne le **kubelet**, l'agent qui reçoit la liste des Pods à exécuter et veille à ce qu'ils tournent, **kube-proxy**, qui programme les règles réseau permettant de joindre les Services, et un **runtime de conteneurs** conforme à l'interface CRI, comme containerd ou CRI-O. Docker lui-même n'est plus utilisé directement comme runtime depuis la version 1.24 (2022), mais les images construites avec Docker fonctionnent toujours, car elles suivent le même standard OCI.

## Les objets de base

L'unité de base n'est pas le conteneur mais le **Pod** : un ou plusieurs conteneurs qui partagent la même adresse IP et peuvent partager des volumes, et qui sont toujours placés ensemble sur le même nœud. Dans la grande majorité des cas, un Pod contient un seul conteneur. Les Pods sont jetables : on ne les crée presque jamais à la main.

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

On crée plutôt un **Deployment**, qui déclare combien de copies (*replicas*) d'un Pod on veut et à partir de quel modèle. Le Deployment gère un ReplicaSet, qui maintient le nombre de Pods, et pilote les mises à jour. Les **labels**, ces étiquettes clé-valeur, servent à relier les objets entre eux : le Deployment retrouve ses Pods grâce à son `selector`.

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
        image: nginx:1.27
        ports:
        - containerPort: 80
```

Puisque les Pods naissent et meurent avec des adresses IP changeantes, on ne les contacte jamais directement. Un **Service** offre une adresse stable et un nom DNS devant un groupe de Pods sélectionnés par leurs labels, et répartit le trafic entre eux. Un Service de type `ClusterIP` (par défaut) n'est joignable que depuis le cluster ; `NodePort` l'expose sur un port de chaque nœud ; `LoadBalancer` demande au fournisseur de cloud un équilibreur de charge externe ; `ExternalName` n'est qu'un alias DNS vers un nom extérieur.

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

Les **Namespaces** découpent un cluster en espaces logiques, par équipe ou par environnement ; ils servent de cadre aux droits d'accès et aux quotas, mais n'isolent pas le réseau par défaut.

D'autres contrôleurs couvrent des besoins particuliers : un **StatefulSet** pour les applications qui ont besoin d'une identité et d'un stockage stables (bases de données), un **DaemonSet** pour faire tourner un Pod sur chaque nœud (agents de logs ou de sécurité), des **Jobs** et **CronJobs** pour des tâches ponctuelles ou planifiées.

## Configuration, secrets et stockage

Une même image doit pouvoir tourner en test et en production avec des réglages différents. On sort donc la configuration de l'image : une **ConfigMap** contient des paramètres ordinaires, un **Secret** des données sensibles, et les deux s'injectent dans les Pods sous forme de variables d'environnement ou de fichiers.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgres://db:5432"
  log_level: "info"
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: cGFzc3dvcmQxMjM=  # base64
```

Il faut bien comprendre que le base64 d'un Secret est un simple encodage, pas un chiffrement : quiconque peut lire l'objet lit le mot de passe. La protection repose sur les droits d'accès (RBAC), sur le chiffrement d'etcd au repos, et souvent sur un gestionnaire externe, via External Secrets Operator, Sealed Secrets (des secrets chiffrés qu'on peut committer dans Git) ou HashiCorp Vault.

Pour les données persistantes, Kubernetes sépare l'offre et la demande. Un **PersistentVolume** (PV) représente un espace de stockage réel, disque cloud, partage NFS ou répertoire d'un nœud ; un **PersistentVolumeClaim** (PVC) est la demande qu'exprime une application (« 5 Go en lecture-écriture »), que le cluster satisfait avec un PV adapté. En pratique, une **StorageClass** crée les PV automatiquement à la demande.

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

## Piloter le cluster avec kubectl

`kubectl` est le client en ligne de commande de l'API. La commande centrale est `kubectl apply -f`, qui soumet un état désiré ; on la relance après chaque modification du fichier, et Kubernetes calcule lui-même ce qui doit changer.

```bash
kubectl apply -f deployment.yaml
kubectl get pods -n production
kubectl get all
kubectl describe pod nom-pod          # Détails et événements : le premier réflexe en cas de problème
kubectl logs -f nom-pod
kubectl exec -it nom-pod -- /bin/sh
kubectl port-forward pod/nom-pod 8080:80

kubectl scale deployment nginx --replicas=5
kubectl set image deployment/nginx nginx=nginx:1.27
kubectl rollout status deployment/nginx
kubectl rollout undo deployment/nginx  # Revenir à la version précédente

kubectl get events --sort-by=.lastTimestamp
kubectl top pods                       # Nécessite metrics-server
```

## Exposer et isoler le réseau

Pour publier plusieurs applications web derrière une seule adresse, on utilise un **Ingress**, qui route les requêtes HTTP selon le nom de domaine et le chemin vers différents Services. Il faut pour cela un *Ingress controller* (comme ingress-nginx ou Traefik) installé dans le cluster. L'API Gateway, plus récente, est appelée à lui succéder.

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

Par défaut, tous les Pods d'un cluster peuvent se parler. Les **NetworkPolicies** restreignent ce trafic, à condition que le plugin réseau (CNI) les applique, comme le font Calico ou Cilium. L'exemple suivant n'autorise l'accès aux Pods `api` qu'aux Pods `frontend` :

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

## Ressources, santé et mise à l'échelle

Chaque conteneur devrait déclarer ses besoins. Les `requests` sont ce que le Scheduler réserve pour placer le Pod ; les `limits` sont le plafond qu'il ne pourra pas dépasser.

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"      # un quart de cœur
  limits:
    memory: "128Mi"
    cpu: "500m"
```

> [!warning] Piège
> Sans `limits`, un conteneur peut consommer toute la mémoire du nœud et faire tomber d'autres Pods avec lui (OOMKiller au niveau du nœud, pas seulement du conteneur). Sans `requests`, le Scheduler ne peut pas garantir qu'un nœud a assez de ressources avant d'y placer le Pod. Les deux sont nécessaires, pas seulement l'un ou l'autre.

Kubernetes ne sait pas, par lui-même, si une application fonctionne vraiment : un processus peut tourner tout en étant bloqué. Les **sondes** (*probes*) le lui disent.

```yaml
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

> [!important] Liveness vs Readiness — pas la même question
> `livenessProbe` répond à « ce conteneur est-il bloqué et doit-il être redémarré ? » — un échec entraîne un restart. `readinessProbe` répond à « ce conteneur peut-il recevoir du trafic maintenant ? » — un échec le retire juste du Service sans le redémarrer. Confondre les deux (ex. mettre la même logique sur les deux) peut provoquer des redémarrages en boucle pour un problème qui ne demandait qu'un retrait temporaire du trafic.

La mise à l'échelle peut ensuite être automatique, à trois niveaux. Le **Horizontal Pod Autoscaler** ajoute ou retire des Pods selon une métrique, ici l'utilisation CPU moyenne ; le **Vertical Pod Autoscaler** ajuste les requêtes de CPU et de mémoire de chaque Pod ; le **Cluster Autoscaler** ajoute ou retire des nœuds quand les Pods ne trouvent plus de place ou que des machines restent vides.

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

## Déployer sans interruption

Par défaut, un Deployment se met à jour en **rolling update** : il remplace les Pods progressivement, en créant les nouveaux avant de supprimer les anciens, dans les limites fixées par `maxSurge` (Pods en trop autorisés) et `maxUnavailable` (Pods manquants tolérés).

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

Deux autres stratégies se construisent par-dessus. En **blue-green**, la nouvelle version tourne entièrement à côté de l'ancienne, puis on bascule tout le trafic d'un coup. En **canary**, on envoie d'abord une petite fraction des utilisateurs vers la nouvelle version, et on élargit si tout va bien ; des outils comme Argo Rollouts ou un service mesh (Istio, Linkerd) automatisent ce dosage.

> [!tip] Comment choisir
> Rolling Update convient à la majorité des cas (aucune infra supplémentaire). Blue-Green permet un rollback instantané (juste re-basculer le routage) mais double temporairement les ressources. Canary limite le rayon d'impact d'un bug en le testant sur un sous-ensemble réel d'utilisateurs avant généralisation — le plus prudent, mais aussi le plus lent à déployer complètement.

## Gérer les manifestes : Helm et Kustomize

Une application réelle compte des dizaines de fichiers YAML, à décliner par environnement. **Helm**, le gestionnaire de paquets de Kubernetes, regroupe ces fichiers dans un *chart* paramétrable par des valeurs, installable et versionné comme un paquet.

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install myapp bitnami/nginx
helm upgrade myapp bitnami/nginx --set replicaCount=3
helm list
helm uninstall myapp
```

**Kustomize**, intégré à `kubectl`, prend le parti inverse : pas de gabarits, mais une base de manifestes ordinaires sur laquelle chaque environnement applique des correctifs.

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
patches:
  - path: patch.yaml
```

```bash
kubectl apply -k ./
```

Dans une démarche **GitOps**, ces manifestes vivent dans un dépôt Git, et un outil comme Argo CD ou Flux synchronise en permanence le cluster avec le dépôt : on déploie en fusionnant une pull request.

## Sécurité

L'accès à l'API est contrôlé par **RBAC** : un `Role` définit des droits (verbes sur des ressources) dans un namespace, un `RoleBinding` les attribue à un utilisateur ou à un compte de service. Comme partout, le principe du moindre privilège s'applique, et les comptes de service des Pods ne devraient avoir que les droits dont l'application a besoin.

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

Le comportement des Pods eux-mêmes se durcit par le `securityContext` (exécution en utilisateur non root, système de fichiers en lecture seule, suppression des capacités Linux). Les **Pod Security Standards**, appliqués par l'admission controller *Pod Security Admission*, imposent ces règles par namespace selon trois niveaux, `privileged`, `baseline` et `restricted`. Ils ont remplacé les anciennes PodSecurityPolicies, supprimées en version 1.25 (2022).

## Observer le cluster

`kubectl top` donne les consommations instantanées, mais la surveillance réelle repose sur une pile dédiée : Prometheus pour collecter les métriques, Alertmanager pour les alertes, Grafana pour les tableaux de bord. Pour les journaux, on utilise soit la pile EFK (Elasticsearch, Fluentd, Kibana), soit Loki, souvent avec Grafana Alloy ou Promtail pour la collecte.

## Où faire tourner Kubernetes

Pour apprendre et développer, Minikube et Kind (Kubernetes dans des conteneurs Docker) créent un cluster local en quelques minutes ; K3s est une distribution légère adaptée aux petites machines et à l'*edge*. En production, la plupart des entreprises utilisent un service managé, où le fournisseur gère le plan de contrôle : EKS chez AWS, GKE chez Google, AKS chez Azure. OpenShift, de Red Hat, ajoute une couche d'outils d'entreprise. Au quotidien, des interfaces comme k9s (dans le terminal) ou Lens, et des utilitaires comme `kubectx`/`kubens` ou `stern` (logs de plusieurs Pods à la fois), simplifient beaucoup le travail.

## Ressources

- [Documentation officielle de Kubernetes](https://kubernetes.io/docs), avec ses tutoriels interactifs.
- Les formations et certifications de la CNCF (CKA, CKAD, CKS) et les conférences KubeCon.
- Pour aller plus loin : service mesh (Istio, Linkerd), GitOps (Argo CD, Flux), opérateurs.
