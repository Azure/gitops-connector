import utils
import logging
from operators.argo_gitops_operator import ArgoGitopsOperator
from operators.flux_gitops_operator import FluxGitopsOperator
from operators.gitops_operator import GitopsOperatorInterface

FLUX_TYPE = "FLUX"
ARGOCD_TYPE = "ARGOCD"

class GitopsOperatorFactory:

    @staticmethod
    def new_gitops_operator() -> GitopsOperatorInterface:
        gitops_operator_type = utils.getenv("GITOPS_OPERATOR_TYPE", FLUX_TYPE)

        if gitops_operator_type == FLUX_TYPE:
            return FluxGitopsOperator()
        elif gitops_operator_type == ARGOCD_TYPE:
            return ArgoGitopsOperator()
        else:
            raise NotImplementedError(f'The GitOps operator {gitops_operator_type} is not supported')
    


