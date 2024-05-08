# Demo Runbook
## Stage 1.<span style="color:Green"> Setting up Kind Cluster </span> 

Setting up **Kind** Environment

```shell
# echo $PWD
# ray-observability

# Creating kind cluster
kind create cluster --image=kindest/node:v1.23.0 --name ray-observability

# Getting Cluster Info
kubectl cluster-info --context kind-ray-observability


```

## Stage 2. <span style="color:Green"> Setting up Prometheus and grafana installations </span>  

1. Setting up **Prometheus** 
```shell
# Download
BIN_PATH=/Users/npatodi/code/observability/kuberay-master
LOG_PATH=/Users/npatodi/code/observability/logs/
cd ${BIN_PATH}
./install/prometheus/install.sh

kubectl get all -n prometheus-system

#NAME                                                         READY   STATUS    RESTARTS   AGE
#pod/alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          2m1s
#pod/prometheus-grafana-84ccb68cc-dd98w                       3/3     Running   0          2m18s
#pod/prometheus-kube-prometheus-operator-895b579fc-xkhfm      1/1     Running   0          2m18s
#pod/prometheus-kube-state-metrics-77b6c5d54b-jxrr6           1/1     Running   0          2m18s
#pod/prometheus-prometheus-kube-prometheus-prometheus-0       2/2     Running   0          2m1s
#pod/prometheus-prometheus-node-exporter-rxqxj                1/1     Running   0          2m18s

```

## Stage 3.  <span style="color:Green"> Setting up KubeRay and Ray Serve </span> 

2. Enabling kuberay operator
```shell
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update
kubectl create namespace ray-observability
kubectl config set-context --current --namespace=ray-observability
# Loading  all required images 
kind load docker-image  quay.io/kuberay/operator:nightly rayproject/ray:2.9.0 rayproject/rayobserve:2.9.1  --name ray-observability
#Installing kuberay operator
helm install kuberay-operator helm-chart/kuberay-operator --version 1.0.0

kubectl get po
#NAME                               READY   STATUS    RESTARTS   AGE
#kuberay-operator-cc5475d57-xpxfd   1/1     Running   0          19s

```

3. Starting Ray Serve
```shell
#cd ${BIN_PATH}/ray-operator/config/samples/
#kubectl apply -f ray-cluster.embed-grafana.yaml
cd /Users/npatodi/code/observability/serve
# Explain Ray Observe code
kubectl apply -f ray-serve-observe-exp.yaml
kubectl get po
```
Output will be:
```jsunicoderegexp
kuberay-operator-cc5475d57-tvhhk                       1/1     Running   2 (16h ago)   17h
rs-obs-exp-raycluster-tn8jx-head-rnnvb                 1/1     Running   0             2s
rs-obs-exp-raycluster-tn8jx-worker-small-group-mfdtb   1/1     Running   0             2s
```

4. Check for service availability
```shell
k get svc
```
Output will be:
```jsunicoderegexp
NAME                                   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                                                             AGE
kuberay-operator                       ClusterIP   10.96.65.209   <none>        8080/TCP                                                            17h
rs-obs-exp-head-svc                    ClusterIP   10.96.4.108    <none>        44217/TCP,10001/TCP,44227/TCP,8265/TCP,6379/TCP,8080/TCP,8000/TCP   21s
rs-obs-exp-raycluster-tn8jx-head-svc   ClusterIP   10.96.128.46   <none>        44217/TCP,10001/TCP,44227/TCP,8265/TCP,6379/TCP,8080/TCP,8000/TCP   2m55s
rs-obs-exp-serve-svc                   ClusterIP   10.96.74.150   <none>        8000/TCP                                                            21s
```

5. Enabling serve and pushing some request it
```shell
nohup kubectl port-forward --address 0.0.0.0 svc/rs-obs-exp-head-svc 8000:8000 >${LOG_PATH}/serve.log&
for i in $( seq 1 25 ); do
  curl -X POST -H "Content-Type: application/json" \localhost:8000/fruit -d '{"amount":'$i',"fruit":"mango_'$i'"}'
  echo ""
  sleep 1
done
```

## Stage 4.  <span style="color:Green"> Setting up Ray Observability </span> 
6. Enabling Prometheus UI
```shell
# Enable Prom UI
nohup kubectl port-forward --address 0.0.0.0 prometheus-prometheus-kube-prometheus-prometheus-0 -n prometheus-system 9090:9090> ${LOG_PATH}/prom.log &
open -a 'Google Chrome' http://localhost:9090/alerts
```
7. Enabling metric port from Head node
```shell
nohup kubectl port-forward --address 0.0.0.0 svc/rs-obs-exp-head-svc 8080:8080 >${LOG_PATH}/raymetric.log&

curl localhost:8080
```

8. Port Forward Grafana and enabling Dashboards
```shell
# Enable Grafana
nohup kubectl port-forward --address 0.0.0.0 deployment/prometheus-grafana -n prometheus-system 3000:3000 > ${LOG_PATH}/grafana.log &
open -a 'Google Chrome' http://localhost:3000/
# Check ${YOUR_IP}:3000/login for the Grafana login page (e.g. 127.0.0.1:3000/login).
# The default username is "admin" and the password is "prom-operator"
#import dashboard from file from /Users/npatodi/code/observability/serve/grafana_dashboard

```

9. Enable Ray dashboard
```shell
nohup kubectl port-forward --address 0.0.0.0 svc/rs-obs-exp-head-svc 8265:8265 >${LOG_PATH}/dashboard.log &

open -a 'Google Chrome' http://localhost:8265/
```


## Stage 5.  <span style="color:Green"> Cleaningup </span> 

```shell
kind delete clusters ray-observability
```