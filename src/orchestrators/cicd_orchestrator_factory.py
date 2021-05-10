import utils
import logging
from orchestrators.cicd_orchestrator import CicdOrchestratorInterface
from repositories.git_repository import GitRepositoryInterface
from orchestrators.azdo_cicd_orchestrator import AzdoCicdOrchestrator


GITHUB_TYPE = "GITHUB"
AZDO_TYPE = "AZDO"

class CicdOrchestratorFactory:

    @staticmethod
    def new_cicd_orchestrator(git_repository: GitRepositoryInterface) -> CicdOrchestratorInterface:
        cicd_orchestrator_type = utils.getenv("CICD_ORCHESTRATOR_TYPE", AZDO_TYPE)

        if cicd_orchestrator_type == AZDO_TYPE:
            return AzdoCicdOrchestrator(git_repository)
        # elif cicd_orchestrator_type == GITHUB_TYPE:
        #     return GitHubCicdOrchestrator()
        else:
            raise NotImplementedError(f'The CI/CD orchestrator {cicd_orchestrator_type} is not supported')
    


