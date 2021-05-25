# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import utils


class GitHubClient:

    def __init__(self):
        self.org_url = utils.getenv("GITHUB_ORG_URL")  # https://api.github.com/repos/kaizentm
        # token is supposed to be stored in a secret without any transformations
        self.token = utils.getenv("PAT")
        self.headers = {'Authorization': f'token {self.token}'}

    def get_rest_api_headers(self) -> dict:
        return self.headers

    def get_rest_api_url(self) -> str:
        return self.org_url
