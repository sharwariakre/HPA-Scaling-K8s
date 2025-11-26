# Kubernetes HPA Autoscaling and Locust Load Testing

This project demonstrates CPU-based Horizontal Pod Autoscaling (HPA) and automatic load distribution in Kubernetes using a Python/Flask microservice and Locust for load generation.

It satisfies the following technical requirements:
- TR5.1: Workloads must automatically scale based on CPU utilization.
- TR2.2: Requests must be automatically distributed across replicas by Kubernetes Services.

---

## Prerequisites

Before running the experiment, ensure the following are installed:

### Docker Desktop with Kubernetes enabled
Enable Kubernetes in:
Docker Desktop → Settings → Kubernetes → Enable Kubernetes

### kubectl installed
```bash
kubectl version --client
```
### pipx installed
```bash
brew install pipx
pipx ensurepath
pipx install locust
```

### watch installed
```bash
brew install watch
```

### Step 1: Build the Docker Image

docker build -t patient-api:latest ./patient-api

### Step 2: Deploy Kubernetes Resources
Apply Deployment, Service, and HPA:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

### Verify pods:
```bash
kubectl get pods
```

### Test the service:
```bash
curl http://localhost:30080/patient-summary
```
Expected output includes "status":"ok".

### Step 3: Install and Patch Metrics Server
HPA requires metrics-server for CPU metrics.

Install metrics-server
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```
Patch metrics-server for Docker Desktop

```bash
kubectl patch deployment metrics-server -n kube-system \
  --type='json' \
  -p='[{ "op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls" }]'
```
```bash
kubectl patch deployment metrics-server -n kube-system \
  --type='json' \
  -p='[{ "op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-preferred-address-types=InternalIP" }]'
```

Restart metrics-server:

```bash
kubectl rollout restart deployment metrics-server -n kube-system
```

Verify:
```bash
kubectl top nodes
kubectl top pods
```

If CPU data appears, metrics-server is working.

### Step 4: Start Locust for Load Generation
```bash
locust -f locust/locustfile.py --host=http://localhost:30080 --web-port 8090
```
Open Locust in a browser:

http://localhost:8090

Start test with:
Users: 20
Spawn rate: 5
Then increase:
Users: 50
Spawn rate: 10

### Step 5: Observe Autoscaling (TR5.1)
Open the following three terminals.

#### Terminal A (watch HPA)
```bash
kubectl get hpa -w
```
You should see CPU usage exceed target and replicas increase.

#### Terminal B (watch pods)
```bash
kubectl get pods -w
```
New pods will appear as HPA scales up.

#### Terminal C (monitor CPU)
```bash
watch -n 2 kubectl top pods
```
CPU should rise significantly (for example, 200m to 400m).
This proves autoscaling is triggered based on CPU load.

### Step 6: Validate Load Distribution (TR2.2)
When multiple pods are running, verify that traffic is load balanced.

Check which pods respond

for i in {1..20}; do curl -s http://localhost:30080/patient-summary; echo; done
You should see different pod names responding.

Verify CPU distribution

```bash
kubectl top pods
```

CPU usage should be similar across pods.
This demonstrates automatic request distribution across replicas.

### Step 7: Cool Down and Scale Down
Stop Locust.

Watch HPA scale down:

kubectl get hpa -w
Watch pods terminate:

bash
Copy code
kubectl get pods -w
Eventually the system returns to 1 replica.

Cleanup
Delete Kubernetes resources:

```bash
kubectl delete -f k8s/
```
Delete metrics-server:
```basg
kubectl delete deployment metrics-server -n kube-system
```
Summary
This experiment demonstrates:

Automatic scaling using Kubernetes HPA (TR5.1)

Even load distribution across replicas (TR2.2)

End-to-end load testing with Locust

CPU-driven autoscaling with metrics-server
