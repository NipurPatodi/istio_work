# Demo Runbook
## Stage 1.<span style="color:Green"> Setting up Kind Cluster </span> ✨

Setting up **Git Repo** Environment

```shell
eksctl delete cluster --name ray-obs-cluster    --region us-east-1 --node-type t2.xlarge
sudo yum install git -y
git clone https://github.com/ray-project/kuberay.git

curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh

```

## Stage 2. <span style="color:Green"> Setting up Prometheus </span> ⛵

1. Setting up **Prometheus** 
```shell
# Download
BIN_PATH=/home/ec2-user/sw/kuberay
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

## Stage 3.  <span style="color:Green"> Setting up Ray Environment </span> ☀️

2. Enabling kuberay operator
```shell
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update
kubectl create namespace ray-observability
kubectl config set-context --current --namespace=ray-observability
#Installing kuberay operator
helm install kuberay-operator helm-chart/kuberay-operator --version 1.0.0

kubectl get po
#NAME                               READY   STATUS    RESTARTS   AGE
#kuberay-operator-cc5475d57-xpxfd   1/1     Running   0          19s

```

3. Starting Ray Serve
```shell
#copying file from local 
cd /Users/npatodi/Desktop/eks
scp -i eks-keytab.pem /Users/npatodi/code/observability/serve/ray-serve-observe-exp-aws.yaml ec2-user@ec2-100-27-210-137.compute-1.amazonaws.com:/home/ec2-user/sw/

# Now login to server
ssh -i eks-keytab.pem ec2-user@ec2-100-27-210-137.compute-1.amazonaws.com
kubectl apply -f ray-serve-observe-exp-aws.yaml
kubectl get po
```
Output will be:
```jsunicoderegexp
NAME                                                   READY   STATUS    RESTARTS   AGE
kuberay-operator-8b9dc7c9b-rc4sx                       1/1     Running   0          18m
rs-obs-exp-raycluster-nnlkg-head-9vjwz                 1/1     Running   0          2m20s
rs-obs-exp-raycluster-nnlkg-worker-small-group-mfczw   0/1     Running   0          2m20s
```

## Stage 3.  <span style="color:Green"> Setting up Ray Observability </span> ☀️
Check for service availability
```shell
k get svc
```
Output will be:
```jsunicoderegexp
kuberay-operator                       ClusterIP   10.100.172.58    <none>        8080/TCP                                                            17m
rs-obs-exp-head-svc                    ClusterIP   10.100.226.102   <none>        44217/TCP,10001/TCP,44227/TCP,8265/TCP,6379/TCP,8080/TCP,8000/TCP   90s
rs-obs-exp-raycluster-nnlkg-head-svc   ClusterIP   10.100.160.205   <none>        44217/TCP,10001/TCP,44227/TCP,8265/TCP,6379/TCP,8080/TCP,8000/TCP   112s
rs-obs-exp-serve-svc                   ClusterIP   10.100.170.76    <none>        8000/TCP                                                            90s
```
Port forward Prometheus
```shell
# Enable Prom UI
nohup kubectl port-forward --address 0.0.0.0 prometheus-prometheus-kube-prometheus-prometheus-0 -n prometheus-system 9090:9090> prom.log &
open -a 'Google Chrome' http://localhost:9090/alerts
```
Port Forward Grafana
```shell
# Enbale Grafana
nohup kubectl port-forward --address 0.0.0.0 deployment/prometheus-grafana -n prometheus-system 3000:3000 > Grafana.log &
open -a 'Google Chrome' http://localhost:3000/
# Check ${YOUR_IP}:3000/login for the Grafana login page (e.g. 127.0.0.1:3000/login).
# The default username is "admin" and the password is "prom-operator"
#import dashboard from file
```

Enable Ray dashboard
```shell
nohup kubectl port-forward --address 0.0.0.0 svc/rs-obs-exp-head-svc 8265:8265 >dashboard.log &

open -a 'Google Chrome' http://localhost:8265/
```

Output will be:
```jsunicoderegexp
# HELP ray_object_store_num_local_objects Number of objects currently in the object store.
# TYPE ray_object_store_num_local_objects gauge
ray_object_store_num_local_objects{Component="raylet",NodeAddress="10.244.0.14",SessionName="session_2024-05-05_03-41-28_108055_14",Version="2.9.0",WorkerId=""} 0.0
# HELP ray_object_manager_num_pull_requests Number of active pull requests for objects.
# TYPE ray_object_manager_num_pull_requests gauge
ray_object_manager_num_pull_requests{Component="raylet",NodeAddress="10.244.0.14",SessionName="session_2024-05-05_03-41-28_108055_14",Version="2.9.0",WorkerId=""} 0.0
```
5. Verifying service 
```shell
kubectl get service
#NAME                                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                                                    AGE
#kuberay-operator                    ClusterIP   10.96.188.213   <none>        8080/TCP                                                   11m
#raycluster-embed-grafana-head-svc   ClusterIP   10.96.140.115   <none>        44217/TCP,10001/TCP,44227/TCP,8265/TCP,6379/TCP,8080/TCP   9m42s

nohup kubectl port-forward --address 0.0.0.0 svc/rs-obs-exp-head-svc 8000:8000 >Serve.log&

#check 
curl -X POST -H "Content-Type: application/json" \localhost:8000/fruit -d '{"amount":23,"fruit":"mango"}'
#fruit mango is sold at prime prize 23 ... congratulation
```

6. Enabling Promethous and Grafana
```shell
nohup kubectl port-forward --address 0.0.0.0 raycluster-embed-grafana-head-tdkzg 8080:8080 >raymetric.log&


```
7. Enabling Grafana metric
```shell
http://127.0.0.1:3000/?orgId=1
# Note: You need to update `RAY_GRAFANA_IFRAME_HOST` if you expose Grafana to a different port.

# Check ${YOUR_IP}:3000/login for the Grafana login page (e.g. 127.0.0.1:3000/login).
# The default username is "admin" and the password is "prom-operator".
```

8. Enabling Dashboard
```shell
 #nohup kubectl port-forward --address 0.0.0.0 svc/raycluster-embed-grafana-head-svc 8265:8265 >dashboard.log &
nohup kubectl port-forward --address 0.0.0.0 svc/rs-obs-exp-raycluster-s567m-head-svc 8265:8265 >dashboard.log &

# Visit http://127.0.0.1:8265/#/metrics in your browser.
```


## Cleanup

```shell
kind delete clusters ray-observability
```