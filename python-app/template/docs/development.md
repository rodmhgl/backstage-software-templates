# Development Guide

## Local Development Setup

### Prerequisites

- Python 3.11+
- Docker
- kubectl configured for your cluster
- Helm 3.x

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/app.py

# Test endpoints
curl http://localhost:5000/api/v1/healthz
curl http://localhost:5000/api/v1/details
```

### Building Container

```bash
# Build image
docker build -t ${{values.app_name}}:local .

# Run container
docker run -p 5000:5000 ${{values.app_name}}:local

# Test containerized app
curl http://localhost:5000/api/v1/healthz
```

## Deployment Process

### Development Environment

```bash
# Deploy to dev namespace
helm install ${{values.app_name}}-dev ./charts/${{values.app_name}} \
  --namespace dev \
  --set image.tag=dev-$(git rev-parse --short HEAD) \
  --set ingress.hosts[0].host=${{values.app_name}}-dev.azurelaboratory.com
```

### Production Deployment

Production deployments are handled via GitOps:

1. Update `charts/${{values.app_name}}/values.yaml` with new image tag
2. Commit changes to main branch
3. Argo CD automatically deploys changes

## Testing

### Unit Tests

```bash
# Run tests (when implemented)
python -m pytest tests/

# With coverage
python -m pytest --cov=src tests/
```

### Integration Tests

```bash
# Test against running service
curl -f https://${{values.app_name}}.azurelaboratory.com/api/v1/healthz || exit 1
```

## Code Quality

### Pre-commit Hooks

The project uses pre-commit hooks for code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Standards

- Follow PEP 8 for Python code style
- Use type hints where applicable
- Maintain test coverage above 80%
- All endpoints must include proper error handling
