# gitops-connector

GitOps Connector integrates a GitOps operator with CI/CD orchestrator

## Source Code

* <https://github.com/azure/gitops-connector>

## Installation

### Install GitOps Connector with Helm

Prepare **values.yaml** file and run the following command:

```console
helm repo add gitops-connector https://azure.github.io/gitops-connector
helm upgrade gitops-connector gitops-connector \
  --install \
  --namespace gitops-connector \
  --values values.yaml
```

## Values

### Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| gitRepositoryType | string | `""` | Git Repository Type (`AZDO` or `GITHUB`) |
| ciCdOrchestratorType | string | `""` | CI/CD Orchestrator Type (`AZDO` or `GITHUB`) |
| gitOpsOperatorType | string | `""` | GitOps Operator Type (`FLUX` or `ARGOCD`) |
| gitOpsAppURL | string | `""` | Call back URL from the Commit Status Window e.g. `https://github.com/kaizentm/gitops-manifests/commit; https://github.com/microsoft/spektate` |
| orchestratorPAT | string | `""` | GitHub or Azure DevOps personal access token |
| azdoGitOpsRepoName | string | `""` | Azure DevOps Mainifests repository name. Required if `gitRepositoryType` is `AZDO` |
| azdoOrgUrl | string | `""` | Azure DevOps Organization URL. Required if `gitRepositoryType` or `ciCdOrchestratorType` is `AZDO`. e.g. `https://dev.azure.com/organization/project` |
| azdoPrRepoName | string | `""` | If `ciCdOrchestratorType` is `AZDO` and when PRs are not issued to the manifests repo, but to a separate HLD repo. Optional. |
| gitHubGitOpsManifestsRepoName | string | `""` | GitHub Mainifests repository name. Required if `gitRepositoryType` is `GITHUB` |
| gitHubOrgUrl | string | `""` | GitHub Organization URL. Required if `gitRepositoryType` or `ciCdOrchestratorType` is `GITHUB`. e.g. `https://api.github.com/owner/repo` |
| gitHubGitOpsRepoName | string | `""` | GitHub Actions repository name. Required if `ciCdOrchestratorType` is `GITHUB` |
| subscribers | object | `{}` | Optional list of subscriber endpoints to send raw JSON to |

### Common

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| nameOverride | string | `""` | Partially override resource names (adds suffix) |
| fullnameOverride | string | `""` | Fully override resource names |
| extraObjects | tpl/list | `[]` | Array of extra objects to deploy with the release |

### Parameters

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| image.repository | string | `"ghcr.io/azure/gitops-connector"` | Image repository |
| image.pullPolicy | string | `"IfNotPresent"` | Image pull policy |
| image.tag | string | `""` | Overrides the image tag whose default is the chart appVersion |
| imagePullSecrets | list | `[]` | Image pull secrets |
| env | tpl/list | `[]` | Additional environment variables |
| envFrom | tpl/list | `[]` | Additional environment variables from a secret or configMap |
| resources | object | `{}` | Container Resources requests and limits |
| securityContext | object | `{}` | Container Security Context |
| podAnnotations | tpl/object | `{}` | Additional annotations for pod |
| podLabels | tpl/object | `{}` | Additional labels for pod |
| podSecurityContext | object | `{}` | Pod Security Context |
| affinity | object | `{}` | Pod Affinity configuration |
| nodeSelector | object | `{}` | Pod Node Selector configuration |
| tolerations | list | `[]` | Pod Tolerations configuration |
| volumes | tpl/list | `[]` | Additional volumes to the pod |
| volumeMounts | tpl/list | `[]` | Additional volumeMounts to the container |
| service.type | string | `"ClusterIP"` | Service type |
| service.port | int | `8080` | Port to expose |
| serviceAccount.create | bool | `true` | Specifies whether a service account should be created |
| serviceAccount.automount | bool | `false` | Specifies whether a service account token should be mounted |
| serviceAccount.annotations | tpl/object | `{}` | Annotations to add to the service account |
| serviceAccount.name | string | `""` | The name of the service account to use. If not set and create is true, a name is generated using the fullname template |
