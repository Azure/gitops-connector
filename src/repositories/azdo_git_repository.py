# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import json
import requests
import utils
from clients.azdo_client import AzdoClient
from repositories.git_repository import GitRepositoryInterface


PR_METADATA_KEY = "callback-task-id"


class AzdoGitRepository(GitRepositoryInterface):

    def __init__(self):
        self.gitops_repo_name = utils.getenv("AZDO_GITOPS_REPO_NAME")
        self.pr_repo_name = os.getenv("AZDO_PR_REPO_NAME", self.gitops_repo_name)
        self.azdo_client = AzdoClient()
        self.repository_api = f'{self.azdo_client.get_rest_api_url()}/_apis/git/repositories/{self.gitops_repo_name}'
        self.pr_repository_api = f'{self.azdo_client.get_rest_api_url()}/_apis/git/repositories/{self.pr_repo_name}'
        self.headers = self.azdo_client.get_rest_api_headers()

    def post_commit_status(self, commit_status):
        url = f'{self.repository_api}/commits/{commit_status.commit_id}/statuses?api-version=6.0'

        azdo_status = self._map_to_azdo_status(commit_status.state)

        # Context and targetUrl must be unique for multiple statuses to appear,
        # otherwise the previous context/targetUrl message will be replaced.
        data = {
            'state': azdo_status,
            'description': commit_status.status_name + ": " + commit_status.message,
            'targetUrl': commit_status.callback_url + "?noop=" + commit_status.status_name,
            # Shows up as "genre/name" underneath the message and status.
            'context': {
                'name': commit_status.status_name,
                'genre': commit_status.genre
            }
        }
        response = requests.post(url=url, headers=self.headers, json=data)

        # Throw appropriate exception if request failed
        response.raise_for_status()

    def get_pr_metadata(self, pr_num):
        # https://docs.microsoft.com/en-us/rest/api/azure/devops/git/pull%20request%20properties/list?view=azure-devops-rest-6.0
        url = f'{self.pr_repository_api}/pullRequests/{pr_num}/properties?api-version=6.0-preview'

        response = requests.get(url=url, headers=self.headers)
        # Throw appropriate exception if request failed
        response.raise_for_status()

        # Navigate the properties response structure
        result = response.json()
        if (result['count'] > 0):
            properties = result['value']
            entry = properties.get(PR_METADATA_KEY)
            if entry:
                # At this point, we have the original JSON string we stored.
                return json.loads(entry['$value'])
        return None

    # Returns an array of PR dictionaries with an optional status filter
    # pr_status values: https://docs.microsoft.com/en-us/rest/api/azure/devops/git/pull%20requests/get%20pull%20requests?view=azure-devops-rest-6.0#pullrequeststatus
    def get_prs(self, pr_status):
        pr_status_param = ''
        if pr_status:
            pr_status_param = f'searchCriteria.status={pr_status}&'
        url = f'{self.pr_repository_api}/pullRequests?{pr_status_param}api-version=6.0'
        response = requests.get(url=url, headers=self.headers)
        # Throw appropriate exception if request failed
        response.raise_for_status()

        pr_response = json.loads(response.content)
        if pr_response['count'] == 0:
            return None

        return pr_response['value']

    def _map_to_azdo_status(self, status):
        status_map = {
            "Succeeded": "succeeded",
            "Failed": "failed",
            "Error": "error",
            "Inconclusive": "pending",
            "Running": "pending",
            "OutOfSync": "pending",
            "Synced": "succeeded",
            "Unknown": "notApplicable",
            "Progressing": "pending",
            "Degraded": "error",
            "Healthy": "succeeded",
            "Missing": "failed",

            "Suspended": "error",
            "ReconciliationSucceeded": "succeeded",
            "ReconciliationFailed": "failed",
            "DependencyNotReady": "error",
            "PruneFailed": "failed",
            "ArtifactFailed": "failed",
            "BuildFailed": "failed",
            "HealthCheckFailed": "failed",
            "ValidationFailed": "failed",
            "NotApplicable": "notApplicable",
            "info": "pending",
            "error": "failed"
        }
        return status_map[status]

    def get_commit_message(self, commit_id):
        url = f'{self.repository_api}/commits/{commit_id}?api-version=6.0'

        response = requests.get(url=url, headers=self.headers)
        # Throw appropriate exception if request failed
        response.raise_for_status()

        commit = response.json()
        comment = commit['comment']

        return comment

    def get_pr_num(self, commit_id) -> str:
        comment = self.get_commit_message(commit_id)
        MERGED_PR = "Merged PR "
        pr_num = None
        if MERGED_PR in comment:
            merged_pr_index = comment.index(MERGED_PR)
            pr_num = comment[merged_pr_index + len(MERGED_PR): comment.index(":", merged_pr_index)]
        return pr_num

    def is_commit_finished(self, commit_id):
        return False

    def set_git_repository(self, repo_name) -> str:
        self.gitops_repo_name = repo_name
        self.pr_repo_name = repo_name
        self.azdo_client = AzdoClient()
        self.headers = self.azdo_client.get_rest_api_headers()
        self.repository_api = f'{self.azdo_client.get_rest_api_url()}/_apis/git/repositories/{self.gitops_repo_name}'
        self.pr_repository_api = f'{self.azdo_client.get_rest_api_url()}/_apis/git/repositories/{self.pr_repo_name}'
        app_url = f'{self.azdo_client.get_rest_api_url()}/{self.pr_repo_name}'
        return app_url
