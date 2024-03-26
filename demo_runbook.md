# Demo Runbook
## Stage 1.<span style="color:Green"> Setting up Kind Cluster </span> ✨

Setting up **Kind** Environment

```shell
# echo $PWD
# ray_istio_mtls_demo

# Creating kind cluster
kind create cluster --image=kindest/node:v1.23.0 --name ray-under-istio-cluster

# Getting Cluster Info
kubectl cluster-info --context kind-ray-under-istio-cluster


```

## Stage 2. <span style="color:Green"> Setting up ISTIO </span> ⛵

1. Setting up **ISTIO** 
```shell
# Download
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.17.2  sh -

# Setting Path
cd istio-1.17.2
export PATH=$PWD/bin:$PATH
cd ..

# Checking version
istioctl version
# 1.17.2
```

2. Check **ISTIO** is all good
```shell
istioctl x precheck
```
Output will be:
```jsunicoderegexp
✔ No issues found when checking the cluster. Istio is safe to install or upgrade!
  To get started, check out https://istio.io/latest/docs/setup/getting-started/
```

3. Setting up Demo profile
```shell
istioctl install --set values.global.proxy.holdApplicationUntilProxyStarts=true
# Try  meshConfig.defaultConfig.holdApplicationUntilProxyStarts also
```

Output will be:
```jsunicoderegexp
This will install the Istio 1.17.2 default profile with ["Istio core" "Istiod" "Ingress gateways"] components into the cluster. Proceed? (y/N) y
✔ Istio core installed
✔ Istiod installed
✔ Ingress gateways installed
✔ Installation complete
Making this installation the default for injection and validation.

Thank you for installing Istio 1.17.  Please take a few minutes to tell us about your install/upgrade experience!  https://forms.gle/hMHGiwZHPU7UQRWe9
```
4. Verifying installation 
```shell
istioctl version
```

Output will be:
```jsunicoderegexp
client version: 1.17.2
control plane version: 1.17.2
data plane version: 1.17.2 (1 proxies)
```

5. Staring prometheus and Kiali agent to view traffic in service mesh
```shell
# Prometheus
kubectl apply -f istio-1.17.2/samples/addons/prometheus.yaml
```
output
```jsunicoderegexp
serviceaccount/prometheus created
configmap/prometheus created
clusterrole.rbac.authorization.k8s.io/prometheus created
clusterrolebinding.rbac.authorization.k8s.io/prometheus created
service/prometheus created
deployment.apps/prometheus created
```
```shell
# Kiali
kubectl apply -f istio-1.17.2/samples/addons/kiali.yaml
```
output
```jsunicoderegexp
configmap/kiali created
clusterrole.rbac.authorization.k8s.io/kiali-viewer created
clusterrole.rbac.authorization.k8s.io/kiali created
clusterrolebinding.rbac.authorization.k8s.io/kiali created
role.rbac.authorization.k8s.io/kiali-controlplane created
rolebinding.rbac.authorization.k8s.io/kiali-controlplane created
service/kiali created
deployment.apps/kiali created
```
Validating Pods
```shell
kubectl get pod -n istio-system
```

output
```jsunicoderegexp
NAME                                    READY   STATUS    RESTARTS   AGE
istio-egressgateway-856866df45-t2rxg    1/1     Running   0          15m
istio-ingressgateway-77bfcf8995-2tmgr   1/1     Running   0          15m
istiod-8cd868b5-vrz4l                   1/1     Running   0          15m
kiali-648847c8c4-5jsww                  1/1     Running   0          74s
prometheus-7b8b9dd44c-zc94c             2/2     Running   0          2m44s

```

Now port forwarding kiali service 
```shell
nohup kubectl port-forward svc/kiali 20001:20001 -n istio-system &
```

## Stage 3.  <span style="color:Green"> Setting up Ray Environment </span> ☀️
1. Creating **Namespace** and enabling **sidecare injection** in **ray-under-istio**   
```shell
# Creating namespace
kubectl create namespace ray-under-istio

# Enable sidecar injection
kubectl label namespace ray-under-istio istio-injection=enabled
kubectl label namespace default istio-injection=enabled

# Verifying
kubectl get namespace -L istio-injection
```
output
```jsunicoderegexp
NAME                 STATUS   AGE   ISTIO-INJECTION
default              Active   8h    enabled
istio-system         Active   8h
kube-node-lease      Active   8h
kube-public          Active   8h
kube-system          Active   8h
local-path-storage   Active   8h
ray-under-istio      Active   18m   enabled
```
2. Enabling Strict MTLS

```shell
kubectl apply -f ns-selective-peer-auth.yaml
```


3. Enabling kuberay operator
```shell
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update
kubectl config set-context --current --namespace=ray-under-istio
# Loading images 
kind load docker-image  quay.io/kuberay/operator:nightly rayproject/ray:2.9.0 --name ray-under-istio-cluster
#Installing kuberay operator
helm install kuberay-operator kuberay-master/helm-chart/kuberay-operator --version 1.0.0
```

output
```jsunicoderegexp
NAME: kuberay-operator
LAST DEPLOYED: Tue Mar 19 06:04:48 2024
NAMESPACE: ray-under-istio
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

Verifying

```shell
kubectl get pods
```
 output
```jsunicoderegexp
NAME                                READY   STATUS    RESTARTS   AGE
kuberay-operator-678c7d7997-smwm4   2/2     Running   0          63s
```

## Stage 4.  <span style="color:Green"> RayCluster under ISTIO example </span> ☁️
1. Applying RayCluster Yaml 
```shell
# echo $PWD
# ray_istio_mtls_demo
kubectl apply -f ray-cluster.complete.yaml
# evaluation
kubectl get po --selector=ray.io/cluster=raycluster-complete
```
2. Setting ray dashboard
```shell
kubectl port-forward svc/raycluster-complete-head-svc  --address 0.0.0.0 8265:8265
```

3. Running application
```shell
#kubectl exec -it raycluster-complete-head-45f9l -- bash
#run python
# Paste test.py

```