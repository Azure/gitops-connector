import logging
from operators.gitops_operator_factory import GitopsOperatorFactory
from repositories.git_repository_factory import GitRepositoryFactory
from orchestrators.cicd_orchestrator_factory import CicdOrchestratorFactory


class GitopsConnector:

    def __init__(self):
        self._gitops_operator = GitopsOperatorFactory.new_gitops_operator()
        self._git_repository = GitRepositoryFactory.new_git_repository()
        self._cicd_orchestrator = CicdOrchestratorFactory.new_cicd_orchestrator(self._git_repository)


    def process_gitops_phase(self, phase_data):
        if self._gitops_operator.is_supported_message(phase_data):
            self._post_commit_statuses(phase_data)
            self._notify_orchestrator(phase_data)
        else:
            logging.debug(f'Message is not supported: {phase_data}')

    def _post_commit_statuses(self, phase_data):
        commit_statuses = self._gitops_operator.extract_commit_statuses(phase_data)
        for commit_status in commit_statuses:
            self._git_repository.post_commit_status(commit_status)
        
    def _notify_orchestrator(self, phase_data):
        is_finished, is_successful = self._gitops_operator.is_finished(phase_data)
        if is_finished:
            commit_id = self._gitops_operator.get_commit_id(phase_data)
            self._cicd_orchestrator.notify_on_deployment_completion(commit_id, is_successful)

    def notify_abandoned_pr_tasks(self):
        try:
            self._cicd_orchestrator.notify_abandoned_pr_tasks()
        except Exception as e:
            logging.error(f'Failed to notify abandoned PRs: {e}')


if __name__ == "__main__":
     git_ops_connector = GitopsConnector()  