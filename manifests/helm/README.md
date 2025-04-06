GitOps connector Helm Chart template.  

1. add a gitops_connector_config_name: "<name of config>" to the Alert's eventMetadata,  
2. set singleInstance: null in values.yaml or at the helm install,  
3. apply a gitopsconfig manifest to the cluster where gitops-connector is running - ensure the name is the same name used in step 1.  
  
NOTE: The helm chart creates a service account, role and role binding to support the connector watching and updating the gitopsconfig resource. The operator also automatically patches (hence the updating) a finalizer into the resource to ensure when it is deleted that a proper cleanup occurs before the manifest is removed from the cluster.