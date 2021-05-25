# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import utils
from orchestrators.cicd_orchestrator import CicdOrchestratorInterface
from repositories.git_repository import GitRepositoryInterface
from orchestrators.azdo_cicd_orchestrator import AzdoCicdOrchestrator
from orchestrators.github_cicd_orchestrator import GitHubCicdOrchestrator


GITHUB_TYPE = "GITHUB"
AZDO_TYPE = "AZDO"


class CicdOrchestratorFactory:

    @staticmethod
    def new_cicd_orchestrator(git_repository: GitRepositoryInterface) -> CicdOrchestratorInterface:
        cicd_orchestrator_type = utils.getenv("CICD_ORCHESTRATOR_TYPE", AZDO_TYPE)

        if cicd_orchestrator_type == AZDO_TYPE:
            return AzdoCicdOrchestrator(git_repository)
        elif cicd_orchestrator_type == GITHUB_TYPE:
            return GitHubCicdOrchestrator(git_repository)
        else:
            raise NotImplementedError(f'The CI/CD orchestrator {cicd_orchestrator_type} is not supported')
