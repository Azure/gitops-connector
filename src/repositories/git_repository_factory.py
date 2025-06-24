# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from repositories.git_repository import GitRepositoryInterface
from repositories.azdo_git_repository import AzdoGitRepository
from repositories.github_git_repository import GitHubGitRepository
from configuration.gitops_config import GitOpsConfig


AZDO_TYPE = "AZDO"
GITHUB_TYPE = "GITHUB"


class GitRepositoryFactory:

    @staticmethod
    def new_git_repository(gitops_config: GitOpsConfig) -> GitRepositoryInterface:
        git_repository_type = gitops_config.git_repository_type

        if git_repository_type == AZDO_TYPE:
            return AzdoGitRepository(gitops_config)
        elif git_repository_type == GITHUB_TYPE:
            return GitHubGitRepository(gitops_config)
        else:
            raise NotImplementedError(f'The Git repository {git_repository_type} is not supported')
