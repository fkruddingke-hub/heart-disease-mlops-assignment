# Kubernetes deployment

The manifests target local Minikube with its NGINX Ingress add-on. They use two
replicas, health probes, resource limits, a non-root/read-only security context,
and a CPU-based autoscaler.

## Minikube workflow

Prerequisites: Docker, `kubectl`, and `minikube`.

```bash
minikube start --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server

eval "$(minikube docker-env)"
docker build -t heart-disease-api:1.0.0 .

kubectl apply -f deployment/kubernetes/namespace.yaml
kubectl apply -f deployment/kubernetes/deployment.yaml
kubectl apply -f deployment/kubernetes/service.yaml
kubectl apply -f deployment/kubernetes/ingress.yaml
kubectl apply -f deployment/kubernetes/hpa.yaml

kubectl -n heart-disease rollout status deployment/heart-disease-api
kubectl -n heart-disease get pods,service,ingress,hpa
```

For a reliable local access test independent of DNS:

```bash
kubectl -n heart-disease port-forward service/heart-disease-api 8080:80
curl http://127.0.0.1:8080/health
curl -X POST http://127.0.0.1:8080/predict \
  -H 'Content-Type: application/json' \
  --data @examples/sample_request.json
```

To demonstrate the Ingress, obtain `minikube ip`, map `heart-disease.local` to
that address in `/etc/hosts`, and call `http://heart-disease.local/heart/health`.

## Cloud adaptation

Push the image to the chosen registry, replace the image name in
`deployment.yaml`, set `imagePullPolicy: Always`, configure the cloud ingress
controller and TLS, then apply the same manifests. Never commit registry or
cloud credentials.

## Removal

```bash
kubectl delete namespace heart-disease
minikube stop
```

