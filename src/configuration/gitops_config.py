class GitOpsConfig:
    def __init__(self,
                 name, 
                 git_repository_type, 
                 cicd_orchestrator_type, 
                 gitops_operator_type, 
                 gitops_app_url, 
                 azdo_gitops_repo_name=None, 
                 azdo_pr_repo_name=None, 
                 azdo_org_url=None,
                 github_gitops_repo_name=None,
                 github_gitops_manifests_repo_name=None,
                 github_org_url=None):
        self.name = name
        self.git_repository_type = git_repository_type
        self.cicd_orchestrator_type = cicd_orchestrator_type
        self.gitops_operator_type = gitops_operator_type
        self.gitops_app_url = gitops_app_url
        self.azdo_gitops_repo_name = azdo_gitops_repo_name
        self.azdo_pr_repo_name = azdo_pr_repo_name
        self.azdo_org_url = azdo_org_url
        self.github_gitops_repo_name = github_gitops_repo_name
        self.github_gitops_manifests_repo_name = github_gitops_manifests_repo_name
        self.github_org_url = github_org_url

    def __repr__(self):
        return f"<GitOpsConfig(name={self.name}, " \
               f"git_repository_type={self.git_repository_type}, " \
               f"cicd_orchestrator_type={self.cicd_orchestrator_type}, " \
               f"gitops_operator_type={self.gitops_operator_type}, " \
               f"gitops_app_url={self.gitops_app_url}, " \
               f"azdo_gitops_repo_name={self.azdo_gitops_repo_name}, " \
               f"azdo_pr_repo_name={self.azdo_pr_repo_name}, " \
               f"azdo_org_url={self.azdo_org_url}, " \
               f"github_gitops_repo_name={self.github_gitops_repo_name}, " \
               f"github_gitops_manifests_repo_name={self.github_gitops_manifests_repo_name}, " \
               f"github_org_url={self.github_org_url})>"
