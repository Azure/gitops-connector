# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from operators.argo_gitops_operator import ArgoGitopsOperator
from operators.flux_gitops_operator import FluxGitopsOperator
from operators.gitops_operator import GitopsOperatorInterface
from configuration.gitops_config import GitOpsConfig


FLUX_TYPE = "FLUX"
ARGOCD_TYPE = "ARGOCD"


class GitopsOperatorFactory:

    @staticmethod
    def new_gitops_operator(gitops_config: GitOpsConfig) -> GitopsOperatorInterface:
        gitops_operator_type = gitops_config.gitops_operator_type

        if gitops_operator_type == FLUX_TYPE:
            return FluxGitopsOperator(gitops_config)
        elif gitops_operator_type == ARGOCD_TYPE:
            return ArgoGitopsOperator(gitops_config)
        else:
            raise NotImplementedError(f'The GitOps operator {gitops_operator_type} is not supported')
