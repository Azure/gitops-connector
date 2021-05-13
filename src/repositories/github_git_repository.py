import os
import requests
import json
import utils
import logging
from clients.github_client import GitHubClient
from repositories.git_repository import GitRepositoryInterface


class GitHubGitRepository(GitRepositoryInterface):

    MAX_DESCR_LENGTH = 140

    def __init__(self):
        self.gitops_repo_name = utils.getenv("GITHUB_GITOPS_MANIFEST_REPO_NAME")  # gitops-manifests
        self.github_client = GitHubClient()
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

    def _map_to_github_state(self, reason): 
        state_map = {
            "Suspended": "error",
            "ReconciliationSucceeded": "success",
            "ReconciliationFailed": "failure",
            "Progressing": "pending",
            "DependencyNotReady": "error",
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
