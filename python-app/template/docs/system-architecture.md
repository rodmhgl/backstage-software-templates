# System Architecture for ${{values.app_name}}

## Overview

The ${{values.app_name}} is a containerized Python Flask microservice that demonstrates cloud-native patterns including health checks, observability, and GitOps deployment. This service provides pod details and health status information, serving as a reference implementation for deploying Python applications on Kubernetes using modern DevOps practices.

```plantuml classes="uml myDiagram" alt="Diagram placeholder" title="Architecture Overview"
@startuml Architecture Overview
!includeurl https://raw.githubusercontent.com/RicardoNiepel/C4-PlantUML/master/C4_Container.puml

Person(dev, "Developer", "Platform users developing and maintaining the service")
Person(user, "End User", "External users consuming the service")
Person(ops, "Operations", "Platform team monitoring and operating the service")

System_Boundary(python_app_system, "${{values.app_name}} System") {
    Container(flask_app, "Flask Application", "Python 3.11 Alpine", "Provides health checks and pod details via REST API")
    Container(helm_chart, "Helm Chart", "Kubernetes Manifests", "Defines deployment, service, and ingress configuration")
}

System_Boundary(k8s_platform, "Kubernetes Platform") {
    Container(nginx_ingress, "NGINX Ingress", "Load Balancer", "Routes external traffic and terminates TLS")
    Container(cert_manager, "cert-manager", "Certificate Management", "Automatically provisions and manages TLS certificates")
    Container(argocd, "Argo CD", "GitOps Controller", "Continuously deploys applications from Git repositories")
}

System_Boundary(cicd_platform, "CI/CD Platform") {
    Container(github_actions, "GitHub Actions", "CI/CD Pipeline", "Builds container images and updates deployment manifests")
    Container(docker_hub, "Docker Hub", "Container Registry", "Stores and distributes container images")
}

System_Ext(github, "GitHub Repository", "Source code and configuration management")
System_Ext(azure_aks, "Azure AKS", "Kubernetes cluster hosting the application")
System_Ext(letsencrypt, "Let's Encrypt", "Certificate Authority for TLS certificates")

Rel(dev, github, "Commits code changes")
Rel(user, nginx_ingress, "HTTPS requests", "Accesses service endpoints")
Rel(ops, argocd, "Monitors deployments", "Reviews application status and performs rollbacks")

Rel(github, github_actions, "Triggers on code changes")
Rel(github_actions, docker_hub, "Pushes container images")
Rel(github_actions, github, "Updates Helm values with new image tags")

Rel(argocd, github, "Polls for configuration changes")
Rel(argocd, flask_app, "Deploys and manages")
Rel(nginx_ingress, flask_app, "Routes traffic to")
Rel(cert_manager, letsencrypt, "Requests certificates")
Rel(cert_manager, nginx_ingress, "Provides TLS certificates")

Rel(flask_app, azure_aks, "Queries Kubernetes API for pod information")
@enduml
```

## Business Impact

This service serves as a foundational template for Python microservices within the organization, providing a standardized approach to cloud-native application development. It enables development teams to rapidly deploy production-ready Python applications with built-in observability, security, and operational best practices. The template reduces time-to-market for new services and ensures consistency across the platform ecosystem.

## Architecture

### Components

#### Flask Application (${{values.app_name}})

- Runtime: Python 3.11 on Alpine Linux container
- Framework: Flask 3.0.3 web framework
- Endpoints: Health checks (`/api/v1/healthz`) and pod details (`/api/v1/details`)
- Resource Requirements: 50m CPU, 50M memory (configurable per environment)

#### Helm Chart

- Kubernetes deployment manifests with environment-specific value files
- Supports dev and prod configurations with different resource allocations
- Includes deployment, service, ingress, and optional autoscaling configurations

#### NGINX Ingress Controller

- Handles external traffic routing and TLS termination
- Configured with cert-manager integration for automatic certificate management
- Routes traffic to the Flask application based on hostname rules

#### Argo CD Application

- GitOps deployment controller monitoring the GitHub repository
- Automatically applies changes from the Helm chart to the Kubernetes cluster
- Provides deployment visibility and rollback capabilities

#### GitHub Actions CI/CD Pipeline

- Triggered on code changes to the `src/` directory
- Builds and pushes Docker images to Docker Hub registry
- Updates Helm chart values with new image tags for GitOps deployment

### Edge Description

#### User → NGINX Ingress

- **Overview:** HTTPS requests from external users to access service endpoints
- **Privacy:** No PII transmitted; service provides infrastructure metadata only

#### NGINX Ingress → Flask Application

- **Overview:** Internal cluster routing of HTTP requests to application pods
- **Privacy:** No PII; forwards infrastructure queries and health checks

#### Argo CD → GitHub Repository

- **Overview:** Polls repository for configuration changes to trigger deployments
- **Privacy:** No PII; accesses public deployment configurations

#### GitHub Actions → Docker Hub

- **Overview:** Pushes built container images to registry for deployment
- **Privacy:** No PII; contains application code and dependencies only

#### Flask Application → Kubernetes API

- **Overview:** Queries cluster API for pod hostname and metadata information
- **Privacy:** No PII; accesses pod infrastructure details via service account

#### cert-manager → Let's Encrypt

- **Overview:** Automated certificate provisioning and renewal for TLS
- **Privacy:** No PII; domain validation only

## Best By

2026-01-31

This architecture documentation should be reviewed and updated by January 31, 2026, to ensure it reflects current deployment patterns and platform capabilities.

## Technical Debt

**Container Base Image:** Currently using Alpine Linux for minimal size, but some Python packages may require compilation. Consider maintaining a pre-built base image with common dependencies to reduce build times.

**Health Check Implementation:** Basic health endpoint exists but lacks comprehensive dependency checks. Future iterations should validate database connections, external service availability, and resource constraints.

**Observability Gaps:** Missing structured logging, metrics collection, and distributed tracing. Integration with Prometheus, Grafana, and Jaeger should be considered for production readiness.

**Testing Coverage:** Template lacks automated testing pipeline. Unit tests, integration tests, and security scanning should be integrated into the CI/CD process.

## Scalability

The service is designed for horizontal scaling via Kubernetes Horizontal Pod Autoscaler (HPA) based on CPU utilization. Current configuration supports 1-100 replicas with 80% CPU threshold for scaling decisions.

**Current Capacity:** Single replica handles approximately 100 requests/second with 50m CPU allocation.

**Projected Growth:** For 1-2 year timeframe, the template pattern should support 1000+ concurrent users per service instance with proper resource allocation and autoscaling configuration.

**Scaling Considerations:**

- Stateless design enables unlimited horizontal scaling
- Resource requests may need adjustment based on application-specific requirements
- Consider implementing custom metrics for more sophisticated autoscaling

## Security

**Container Security:** Application runs as non-root user in minimal Alpine Linux container, reducing attack surface. Base image is regularly updated through automated dependency scanning.

**Network Security:** All external communication encrypted via TLS 1.2+. Internal cluster communication uses Kubernetes network policies to restrict pod-to-pod access.

**Secret Management:** Sensitive configuration managed via Kubernetes secrets. Container registry credentials and ArgoCD authentication tokens stored securely.

**Data Handling:** Service does not process or store personal user data. Only infrastructure metadata (pod names, timestamps) is exposed through API endpoints.

**Access Control:** Kubernetes RBAC controls service account permissions. Deployment access restricted to authorized platform teams via ArgoCD and GitHub repository permissions.

## Resources

- **Live Service:** [https://${{values.app_name}}-${{values.app_env}}.azurelaboratory.com](https://${{values.app_name}}-${{values.app_env}}.azurelaboratory.com)
- **Health Endpoint:** [https://${{values.app_name}}-${{values.app_env}}.azurelaboratory.com/api/v1/healthz](https://${{values.app_name}}-${{values.app_env}}.azurelaboratory.com/api/v1/healthz)
- **ArgoCD Dashboard:** [https://argocd.azurelaboratory.com/applications/${{values.app_name}}-${{values.app_env}}](https://argocd.azurelaboratory.com/applications/${{values.app_name}}-${{values.app_env}})
- **Source Repository:** [https://github.com/azurelaboratory/${{values.app_name}}](https://github.com/azurelaboratory/${{values.app_name}})
- **Container Registry:** [https://hub.docker.com/r/rodstewart/${{values.app_name}}](https://hub.docker.com/r/rodstewart/${{values.app_name}})
- **Helm Chart Documentation:** `/charts/${{values.app_name}}/README.md`
- **Operational Runbook:** `/docs/runbook.md`
- **Development Guide:** `/docs/development.md`
- **Architectural Decision Records:** `/docs/adr/index.md`
