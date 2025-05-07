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

### Single Instance vs Multiple Instances

The gitops-connector supports operation in two different modes;  Single Instance and Multiple Instances.

### Single Instance Configuration

This behaves in the same way as the original.  Configuration is for one combination of gitops operator, respository and orchestrator, and config data is supplied via helm chart values as shown below.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| singleInstance.gitRepositoryType | string | `""` | Git Repository Type (`AZDO` or `GITHUB`) |
| singleInstance.ciCdOrchestratorType | string | `""` | CI/CD Orchestrator Type (`AZDO` or `GITHUB`) |
| singleInstance.gitOpsOperatorType | string | `""` | GitOps Operator Type (`FLUX` or `ARGOCD`) |
| singleInstance.gitOpsAppURL | string | `""` | Call back URL from the Commit Status Window e.g. `https://github.com/kaizentm/gitops-manifests/commit; https://github.com/microsoft/spektate` |
| singleInstance.azdoGitOpsRepoName | string | `""` | Azure DevOps Mainifests repository name. Required if `gitRepositoryType` is `AZDO` |
| singleInstance.azdoOrgUrl | string | `""` | Azure DevOps Organization URL. Required if `gitRepositoryType` or `ciCdOrchestratorType` is `AZDO`. e.g. `https://dev.azure.com/organization/project` |
| singleInstance.azdoPrRepoName | string | `""` | If `ciCdOrchestratorType` is `AZDO` and when PRs are not issued to the manifests repo, but to a separate HLD repo. Optional. |
| singleInstance.gitHubGitOpsManifestsRepoName | string | `""` | GitHub Mainifests repository name. Required if `gitRepositoryType` is `GITHUB` |
| singleInstance.gitHubOrgUrl | string | `""` | GitHub Organization URL. Required if `gitRepositoryType` or `ciCdOrchestratorType` is `GITHUB`. e.g. `https://api.github.com/owner/repo` |
| singleInstance.gitHubGitOpsRepoName | string | `""` | GitHub Actions repository name. Required if `ciCdOrchestratorType` is `GITHUB` |
| singleInstance.subscribers | object | `{}` | Optional list of subscriber endpoints to send raw JSON to |

### Multiple Instances Configuration

Setting `singleInstance: null` in the helm chart's values file deploys a CRD for `gitopsconfig` resources and informs the gitops-connector to watch for these to automatically configure named instances of each combination of supported operator, repository and orchestrator.

Each alert (Flux) or notification (ArgoCD) must send a `gitops_connector_config_name` property with a value that matches a named configuration defined by a gitsopsconfig manifest.  See her for an example of a manifest:

```
apiVersion: example.com/v1
kind: GitOpsConfig
metadata:
  name: my-gitops-repo-stage-dev
spec:
  gitRepositoryType: "AZDO"
  ciCdOrchestratorType: "AZDO"
  gitOpsOperatorType: "ARGOCD"
  gitOpsAppURL: "https://dev.azure.com/myorg/MyProject/_git/my-gitops-repo"
  azdoGitOpsRepoName: "my-gitops-repo"
  azdoPrRepoName: "my-gitops-repo"
  azdoOrgUrl: "https://dev.azure.com/myorg/MyProject"
```

For this configuration to be used for processing a message from a gitop operator, setup the required Alert or Notification as follows.

#### ArgoCD Notifications Setup
```
data:
  trigger.sync-operation-status: |
    - when: app.status.operationState.phase in ['Error', 'Failed']
      send: [sync-operation-status-change]
    - when: app.status.operationState.phase in ['Succeeded']
      send: [sync-operation-status-change]
    - when: app.status.operationState.phase in ['Running']
      send: [sync-operation-status-change]
    - when: app.status.health.status in ['Progressing']
      send: [sync-operation-status-change]
    - when: app.status.health.status in ['Healthy'] && app.status.operationState.phase in ['Succeeded']
      send: [sync-operation-status-change]
    - when: app.status.health.status in ['Unknown', 'Suspended', 'Degraded', 'Missing', 'Healthy']
      send: [sync-operation-status-change]
  service.webhook.gitops-connector: |
    url: http://gitops-connector.gitops:8080/gitopsphase
    headers:
    - name: Content-Type
      value: application/json
  template.sync-operation-status-change: |
    webhook:
      gitops-connector:
        method: POST
        body: |
          {
            "commitid": "{{.app.status.operationState.operation.sync.revision}}",
            "phase": "{{.app.status.operationState.phase}}",
            "sync_status": "{{.app.status.sync.status}}",
            "health": "{{.app.status.health.status}}",
            "message": "{{.app.status.operationState.message}}",
            "resources": {{toJson .app.status.resources}},
            "gitops_connector_config_name": "{{ index .app.metadata.annotations "gitops-connector-config-name" }}"
          }
```

This config expects the monitored Application manifest to have an annotation of `gitops-connector-config-name` set with the value of the named configuration that should handle the notifications.

#### FluxV2 Alert Setup
```
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Provider
metadata:
  name: my-gitops-repo-connector
  namespace: flux-system
spec:
  type: generic
  address: http://gitops-connector:8080/gitopsphase
  
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Alert
metadata:
  name: my-gitops-repo-connector
  namespace: flux-system
spec:
  eventMetadata:
    gitops_connector_config_name: my-gitops-repo-stage-dev
  eventSeverity: info
  providerRef:
    name: my-gitops-repo-connector
  eventSources:
    - kind: GitRepository
      name: my-gitops-repo-source
    - kind: Kustomization
      name: my-gitops-repo-kustomization
```

### Common

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| orchestratorPAT | string | `""` | GitHub or Azure DevOps personal access token |
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
| serviceAccount.automount | bool | `true` | Specifies whether a service account token should be mounted |
| serviceAccount.annotations | tpl/object | `{}` | Annotations to add to the service account |
| serviceAccount.name | string | `""` | The name of the service account to use. If not set and create is true, a name is generated using the fullname template |

