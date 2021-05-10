import utils
from abc import ABC, abstractmethod

class GitopsOperatorInterface(ABC):

    def __init__(self):
        self.callback_url = utils.getenv("GITOPS_APP_URL")

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



