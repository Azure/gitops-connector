import kopf
import logging
from kubernetes import config as k8s_config
from threading import Thread
from configuration.gitops_config import GitOpsConfig
from typing import Callable, Optional, List
from configuration.gitops_connector_manager import GitOpsConnectorManager

class GitOpsConfigOperator:
    def __init__(self, connector_manager: GitOpsConnectorManager):
        self.configurations = {}  # Store configuration objects indexed by resource name
        self.connector_manager = connector_manager

    def run(self):
        logging.info("Starting GitOps Operator")
        k8s_config.load_incluster_config()  # In-cluster Kubernetes config

        # Start Kopf event handlers
        kopf.run()

    def create(self, spec, name):
        logging.info(f"GitOpsConfig created: {name}")
        config = self.parse_config(spec, name)
        self.configurations[name] = config

        self.connector_manager.add_or_update_configuration(config)
        logging.info(f"Configuration added for {name}: {config}")

    def update(self, spec, name):
        logging.info(f"GitOpsConfig updated: {name}")
        config = self.parse_config(spec, name)
        self.configurations[name] = config

        self.connector_manager.add_or_update_configuration(config)
        logging.info(f"Configuration updated for {name}: {config}")

    def delete(self, name):
        logging.info(f"GitOpsConfig deleted: {name}")
        if name in self.configurations:
            config = self.configurations[name]
            self.connector_manager.remove_configuration(config)
            del self.configurations[name]
        logging.info(f"Configuration removed for {name}")

    def parse_config(self, spec, name):
        """Parse the CRD spec into a GitOpsConfig object."""
        return GitOpsConfig(
            name=name,
            git_repository_type=spec.get("gitRepositoryType"),
            cicd_orchestrator_type=spec.get("ciCdOrchestratorType"),
            gitops_operator_type=spec.get("gitOpsOperatorType"),
            gitops_app_url=spec.get("gitOpsAppURL"),
            azdo_gitops_repo_name=spec.get("azdoGitOpsRepoName"),
            azdo_pr_repo_name=spec.get("azdoPrRepoName"),
            azdo_org_url=spec.get("azdoOrgUrl"),
            github_gitops_repo_name=spec.get("gitHubGitOpsRepoName"),
            github_gitops_manifests_repo_name=spec.get("gitHubGitOpsManifestsRepoName"),
            github_org_url=spec.get("gitHubOrgUrl"),
        )

    def get_configuration(self, name):
        """Get the configuration object by name."""
        return self.configurations.get(name)
    
    # def get_gitops_connector(self, name):
    #     """Get the gitops_connector object by name."""
    #     return self.connector_manager.connectors.get(name)

    def stop_all(self):
        self.connector_manager.stop_all()