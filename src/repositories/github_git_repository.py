# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import requests
import logging
from clients.github_client import GitHubClient
from repositories.git_repository import GitRepositoryInterface
from configuration.gitops_config import GitOpsConfig


class GitHubGitRepository(GitRepositoryInterface):

    MAX_DESCR_LENGTH = 140

    def __init__(self, gitops_config: GitOpsConfig):
        self.gitops_repo_name = gitops_config.github_gitops_manifests_repo_name
        self.github_client = GitHubClient(gitops_config)
        self.headers = self.github_client.get_rest_api_headers()
        self.rest_api_url = self.github_client.get_rest_api_url()

    def post_commit_status(self, commit_status):
        url = f'{self.rest_api_url}/{self.gitops_repo_name}/statuses/{commit_status.commit_id}'

        github_state = self._map_to_github_state(commit_status.state)
        message = commit_status.message
        if len(message) > self.MAX_DESCR_LENGTH:
            message = message[:self.MAX_DESCR_LENGTH]

        data = {'state': github_state, 'description': message, 'context': commit_status.status_name}
        logging.info(f'Url {url}: Headers {self.headers}: Data {data}')
        response = requests.post(url=url, headers=self.headers, json=data)
        # Throw appropriate exception if request failed
        response.raise_for_status()

    def is_commit_finished(self, commit_id):
        url = f'{self.rest_api_url}/{self.gitops_repo_name}/commits/{commit_id}/status'

        response = requests.get(url=url, headers=self.headers)
        # Throw appropriate exception if request failed
        response.raise_for_status()

        responseJSON = response.json()

        # logging.debug(f'Url {url}: Headers {self.headers}: Response {responseJSON}')

        state = responseJSON['state']

        logging.info(f'Commit {commit_id}: {state}')

        return state == 'failure' or state == 'success'

    def _map_to_github_state(self, reason):
        state_map = {
            "Suspended": "error",
            "ReconciliationSucceeded": "success",
            "ReconciliationFailed": "failure",
            "Progressing": "pending",
            "DependencyNotReady": "pending",
            "PruneFailed": "failure",
            "ArtifactFailed": "failure",
            "BuildFailed": "failure",
            "HealthCheckFailed": "failure",
            "ValidationFailed": "failure",
            "NotApplicable": "success",
            "info": "pending",
            "error": "failure",

            "Succeeded": "success",
            "Failed": "failure",
            "Error": "error",
            "Inconclusive": "pending",
            "Running": "pending",
            "OutOfSync": "pending",
            "Synced": "success",
            "Unknown": "success",
            "Progressing": "pending",
            "Degraded": "error",
            "Healthy": "success",
            "Missing": "failure"

        }
        return state_map[reason]

    def get_commit_message(self, commit_id):
        url = f'{self.rest_api_url}/{self.gitops_repo_name}/commits/{commit_id}'

        response = requests.get(url=url, headers=self.headers)
        # Throw appropriate exception if request failed
        response.raise_for_status()

        responseJSON = response.json()
        commitMessage = responseJSON['commit']['message']

        return commitMessage

    def get_pr_num(self, commit_id) -> str:
        pass

    def get_pr_metadata(self, commit_id):
        pass

    def get_prs(self, pr_status):
        pass
