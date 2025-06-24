# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import logging
import requests
from orchestrators.cicd_orchestrator import CicdOrchestratorInterface
from repositories.git_repository import GitRepositoryInterface
from clients.github_client import GitHubClient
from configuration.gitops_config import GitOpsConfig


class GitHubCicdOrchestrator(CicdOrchestratorInterface):

    def __init__(self, git_repository: GitRepositoryInterface, gitops_config: GitOpsConfig):
        super().__init__(git_repository)
        self.gitops_repo_name = gitops_config.github_gitops_repo_name
        self.github_client = GitHubClient(gitops_config)
        self.headers = self.github_client.get_rest_api_headers()
        self.rest_api_url = self.github_client.get_rest_api_url()

    def notify_on_deployment_completion(self, commit_id, is_successful):
        if is_successful:
            source_commit_id, run_id, commit_message = self._get_source_commit_id_run_id_commit_mesage(commit_id)
            self._send_repo_dispatch_event(source_commit_id, run_id, commit_message)

    def notify_abandoned_pr_tasks(self):
        pass

    def _get_source_commit_id_run_id_commit_mesage(self, manifest_commitid):
        commitMessage = self.git_repository.get_commit_message(manifest_commitid)
        commitMessageArray = commitMessage.split('/')
        runid = commitMessageArray[2]
        if len(commitMessageArray) > 3:
            commitid = commitMessageArray[3]
        logging.info(f'CommitId {commitid}')
        return commitid, runid, commitMessage

    def _send_repo_dispatch_event(self, commmit_id, run_id, commit_message):
        url = f'{self.rest_api_url}/{self.gitops_repo_name}/dispatches'
        event_type = 'sync-success'
        data = {'event_type': event_type, 'client_payload': {'sha': commmit_id, 'runid': run_id, 'commitmessage': commit_message}}
        logging.info(f'Dispatch event: url {url}; data {data}')
        response = requests.post(url=url, headers=self.headers, json=data)
        # Throw appropriate exception if request failed
        response.raise_for_status()
