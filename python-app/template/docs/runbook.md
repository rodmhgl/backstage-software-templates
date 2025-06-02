# Operational Runbook

## Service Health Monitoring

### Health Check Commands

```bash
# Basic health check
curl https://${{values.app_name}}.azurelaboratory.com/api/v1/healthz

# Detailed service info
curl https://${{values.app_name}}.azurelaboratory.com/api/v1/details

# Check pod status
kubectl get pods -l app.kubernetes.io/name=${{values.app_name}}

# View recent logs
kubectl logs -l app.kubernetes.io/name=${{values.app_name}} --tail=50
```

## Common Issues & Troubleshooting

### Issue: Service Returning 502/503 Errors

**Symptoms**: Users getting gateway errors, health checks failing

**Investigation Steps:**

1. Check pod status: `kubectl get pods -l app.kubernetes.io/name=${{values.app_name}}`
2. Examine pod logs: `kubectl logs <pod-name>`
3. Verify service endpoints: `kubectl get endpoints ${{values.app_name}}`

**Common Causes:**

- Pod crash loop (check resources/limits)
- Readiness probe failing
- Service selector mismatch

### Issue: TLS Certificate Problems

**Symptoms**: Browser security warnings, curl SSL errors

**Investigation Steps:**

1. Check certificate status: `kubectl get certificate ${{values.app_name}}-tls`
2. Examine cert-manager logs: `kubectl logs -n cert-manager deployment/cert-manager`
3. Verify DNS resolution: `nslookup ${{values.app_name}}.azurelaboratory.com`

### Issue: Deployment Stuck

**Symptoms**: Argo CD shows "Progressing" status indefinitely

**Investigation Steps:**

1. Check Argo CD application: Visit [Argo CD Dashboard](https://argocd.azurelaboratory.com)
2. Review deployment events: `kubectl describe deployment ${{values.app_name}}`
3. Check image pull status: `kubectl describe pod <pod-name>`

## Scaling Operations

### Manual Scaling

```bash
# Scale to 3 replicas
kubectl scale deployment ${{values.app_name}} --replicas=3

# Or via Helm
helm upgrade ${{values.app_name}} ./charts/${{values.app_name}} --set replicaCount=3
```

### Monitoring Scaling Metrics

- CPU/Memory usage in Azure Monitor
- Request latency and throughput
- Pod restart frequency

## Emergency Procedures

### Rolling Back Deployment

```bash
# Via Argo CD (recommended)
# Use the Argo CD UI to rollback to previous version

# Via kubectl (emergency only)
kubectl rollout undo deployment/${{values.app_name}}

# Check rollout status
kubectl rollout status deployment/${{values.app_name}}
```

### Service

```bash
# Force pod restart
kubectl rollout restart deployment/${{values.app_name}}
```
