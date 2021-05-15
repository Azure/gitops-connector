![build](https://github.com/kaizentm/gitops-connector/actions/workflows/ci.yaml/badge.svg)
![deploy](https://github.com/kaizentm/gitops-connector/actions/workflows/cd.yaml/badge.svg)
![publish](https://github.com/kaizentm/gitops-connector/actions/workflows/publish.yaml/badge.svg)

# GitOps Connector

GitOps Connector is a custom component with the goal of enriching the integration between Azure DevOps and ArgoCD so the user experience in the entire CI/CD process is smoother and more observable. The whole process can be handled and monitored from Azure DevOps UI.

Azure DevOps GitOps Connector listens for the messages coming from [Argo CD Notifications](https://argoproj.github.io/argo-cd/operator-manual/notifications/) and it takes corresponding actions with Azure DevOps such as Git Commit status updates and resuming/failing a CD pipeline agentless task waiting for the sync result.
It may also receive the messages from Azure DevOps webhooks when a PR to the manifest repo is merged or abandoned to start the ArgoCD sync process or fail the CD pipeline respectively. In addition to the webhooks (the Azdo->K8s connection may be restricted) the connector monitors the abandoned PRs and cancels corresponding CD pipelines waiting for the sync results.

See how Azure DevOps GitOps Connector is involved in the overall GitOps process in [GitOps with Azure DevOps and ArgoCD/Flux](../docs/azdo-gitops.md)
