# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
from repositories.git_repository import GitRepositoryInterface
from repositories.azdo_git_repository import AzdoGitRepository
from repositories.github_git_repository import GitHubGitRepository


AZDO_TYPE = "AZDO"
GITHUB_TYPE = "GITHUB"


class GitRepositoryFactory:

    @staticmethod
    def new_git_repository() -> GitRepositoryInterface:
        git_repository_type = os.getenv("GIT_REPOSITORY_TYPE", AZDO_TYPE)

        if git_repository_type == AZDO_TYPE:
            return AzdoGitRepository()
        elif git_repository_type == GITHUB_TYPE:
            return GitHubGitRepository()
        else:
            raise NotImplementedError(f'The Git repository {git_repository_type} is not supported')
