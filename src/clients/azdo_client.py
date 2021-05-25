# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import base64
import utils


class AzdoClient:

    def __init__(self):
        # https://dev.azure.com/csedevops/GitOps
        self.org_url = utils.getenv("AZDO_ORG_URL")
        # token is supposed to be stored in a secret without any transformations
        token = base64.b64encode(f':{utils.getenv("PAT")}'.encode("ascii")).decode("ascii")
        self.headers = {'authorization': f'Basic {token}',
                        'Content-Type': 'application/json'}

    def get_rest_api_headers(self) -> dict:
        return self.headers

    def get_rest_api_url(self) -> str:
        return self.org_url
