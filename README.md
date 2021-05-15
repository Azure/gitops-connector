![build](https://github.com/kaizentm/gitops-connector/actions/workflows/ci.yaml/badge.svg)
![deploy](https://github.com/kaizentm/gitops-connector/actions/workflows/cd.yaml/badge.svg)
![publish](https://github.com/kaizentm/gitops-connector/actions/workflows/publish.yaml/badge.svg)

# GitOps Connector

GitOps Connector is a custom component with the goal of enriching the integration of a GitOps operator and a CI/CD orchestrator so the user experience in the entire CI/CD process is smoother and more observable. The whole process can be handled and monitored from a CI/CD orchestrator.

![publish](./img/gitops-connector.png)

During the reconciliation process a GitOps operator notifies on every phase change and every health check the GitOps connector. This component serves as an adapter, it "knows" how to communicate to a Git repository and it updates the Git commit status so the synchronization progress is visible in the Manifests repository. When the reconciliation including health check has successfully finished or failed the connector notifies a CI/CD orchestrator, so the CD pipelines/workflows may perform corresponding actions such as testing, post-deployment activities and moving on to the next stage in the deployment chain.

## GitOps operators

The GitOps Connector supports the following Git Ops operators:
- [FluxCD](https://fluxcd.io)
- [ArgoCD](https://argoproj.github.io/argo-cd/)

## Git Commit Status Update 

The GitOps Connector supports the following Git repositories:
- [Azure Repos](https://azure.microsoft.com/services/devops/repos/)
- [GitHub](https://github.com)

## Notification on Deployment Completion
-
### Azure Pipelines
-
### GitHub Actions
-

## Installation
-
## Contribution
-
See how Azure DevOps GitOps Connector is involved in the overall GitOps process in [GitOps with Azure DevOps and ArgoCD/Flux](../docs/azdo-gitops.md)
