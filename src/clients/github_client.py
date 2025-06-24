# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import utils
from configuration.gitops_config import GitOpsConfig


class GitHubClient:

    def __init__(self, gitops_config: GitOpsConfig):
        self.org_url = gitops_config.github_org_url
        # token is supposed to be stored in a secret without any transformations
        self.token = utils.getenv("PAT")
        self.headers = {'Authorization': f'token {self.token}'}

    def get_rest_api_headers(self) -> dict:
        return self.headers

    def get_rest_api_url(self) -> str:
        return self.org_url
