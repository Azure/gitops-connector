from abc import ABC, abstractmethod
from repositories.git_repository import GitRepositoryInterface


class CicdOrchestratorInterface(ABC):

    def __init__(self, git_repository: GitRepositoryInterface):
        self.git_repository = git_repository

    @abstractmethod
    def notify_on_deployment_completion(self, commit_id, is_successful):
        pass

    @abstractmethod
    def notify_abandoned_pr_tasks(self):
        pass
