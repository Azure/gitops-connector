from operators.gitops_operator import GitopsOperatorInterface
from operators.git_commit_status import GitCommitStatus

class ArgoGitopsOperator(GitopsOperatorInterface):

    def extract_commit_statuses(self, phase_data):
        commit_statuses = []

        commit_id = self.get_commit_id(phase_data)
        phase_status, sync_status, health_status = self._get_statuses(phase_data)

        phase_status = self._new_git_commit_status(commit_id = commit_id, status_name = 'Phase',
             state = phase_status, message = phase_data['phase'] + ": " + phase_data['message'])
        commit_statuses.append(phase_status) 

        (health_summary, sync_summary) = self._get_deployment_status_summary(phase_data['resources'])

        sync_status = self._new_git_commit_status(commit_id = commit_id, status_name = 'Sync',
             state = sync_status, message = sync_summary)
        commit_statuses.append(sync_status)

        health_status = self._new_git_commit_status(commit_id = commit_id, status_name = 'Health',
             state = health_status, message = health_summary)
        commit_statuses.append(health_status)

        return commit_statuses

    def is_finished(self, phase_data):
        phase_status, _, health_status = self._get_statuses(phase_data)

        is_finished = phase_status != 'Inconclusive' and phase_status != 'Running' and \
                      health_status != 'Progressing' 
        
        is_successful = phase_status == 'Succeeded' and health_status == 'Healthy'             

        return is_finished, is_successful

    def get_commit_id(self, phase_data) -> str:
        return phase_data['commitid']

    def _get_statuses(self, phase_data):
        return phase_data['phase'], phase_data['sync_status'], phase_data['health']

    def _new_git_commit_status(self, commit_id, status_name, state, message: str):
        return GitCommitStatus(commit_id=commit_id, status_name=status_name,
             state=state, message=message, callback_url=self.callback_url, gitops_operator='ArgoCD') 

    def is_supported_message(self, phase_data) -> bool:
        return True
