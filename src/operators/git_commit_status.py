from dataclasses import dataclass

@dataclass
class GitCommitStatus:
    commit_id: str
    status_name: str
    state: str
    message: str
    callback_url: str
    gitops_operator: str
    genre: str

    def __lt__(self, other):
        # Status messages need to come last.
        return self.genre != "Status"
