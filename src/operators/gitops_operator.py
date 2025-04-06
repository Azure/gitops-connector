# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import utils
from abc import ABC, abstractmethod
from configuration.gitops_config import GitOpsConfig

class GitopsOperatorInterface(ABC):

    def __init__(self, gitops_config: GitOpsConfig):
        self.gitops_config = gitops_config
        self.callback_url = gitops_config.gitops_app_url # utils.getenv("GITOPS_APP_URL")

    @abstractmethod
    def extract_commit_statuses(self, phase_data):
        pass

    @abstractmethod
    def is_finished(self, phase_data) -> bool:
        pass

    @abstractmethod
    def get_commit_id(self, phase_data) -> str:
        pass

    @abstractmethod
    def is_supported_message(self, phase_data) -> bool:
        pass
