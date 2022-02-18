# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import logging
from queue import PriorityQueue

from operators.gitops_operator_factory import GitopsOperatorFactory
from repositories.git_repository_factory import GitRepositoryFactory
from repositories.raw_subscriber import RawSubscriberFactory
from orchestrators.cicd_orchestrator_factory import CicdOrchestratorFactory


# Instance is shared across threads.
class GitopsConnector:

    def __init__(self):
        self._gitops_operator = GitopsOperatorFactory.new_gitops_operator()
        self._git_repository = GitRepositoryFactory.new_git_repository()
        self._cicd_orchestrator = CicdOrchestratorFactory.new_cicd_orchestrator(self._git_repository)

        # Subscribers that take unprocessed JSON, forwarded from the notifications
        self._raw_subscribers = RawSubscriberFactory.new_raw_subscribers()

        # Commit status notification queue
        self._global_message_queue = PriorityQueue()

    def process_gitops_phase(self, phase_data, req_time):
        if self._gitops_operator.is_supported_message(phase_data):
            commit_id = self._gitops_operator.get_commit_id(phase_data)
            if not self._git_repository.is_commit_finished(commit_id):
                self._queue_commit_statuses(phase_data, req_time)
                self._notify_orchestrator(phase_data, commit_id)
        else:
            logging.debug(f'Message is not supported: {phase_data}')

    def _queue_commit_statuses(self, phase_data, req_time):
        commit_statuses = self._gitops_operator.extract_commit_statuses(phase_data)
        for commit_status in commit_statuses:
            self._global_message_queue.put(item=(req_time, commit_status))

    def _notify_orchestrator(self, phase_data, commit_id):
        is_finished, is_successful = self._gitops_operator.is_finished(phase_data)
        if is_finished:
            self._cicd_orchestrator.notify_on_deployment_completion(commit_id, is_successful)

    # Entrypoint for the periodic task to search for abandoned PRs linked to
    # agentless tasks.
    def notify_abandoned_pr_tasks(self):
        try:
            self._cicd_orchestrator.notify_abandoned_pr_tasks()
        except Exception as e:
            logging.error(f'Failed to notify abandoned PRs: {e}')

    # Entrypoint for the commit status thread.
    # The thread waits for items in the priority queue and sends the messages
    # in the order of the request received time.
    def drain_commit_status_queue(self):
        while (True):
            try:
                # Blocking get
                commit_status = self._global_message_queue.get()

                if not commit_status:
                    break

                # Queue entry is (received time, commit_status)
                commit_status = commit_status[1]

                # Handling an exception as it crashes the draining thread
                try:
                    self._git_repository.post_commit_status(commit_status)

                    for subscriber in self._raw_subscribers:
                        subscriber.post_commit_status(commit_status)
                except Exception as e:
                    logging.error(f'Failed to update GitCommit Status: {e}')

            except Exception as e:
                logging.error(f'Unexpected exception in the message queue draining thread: {e}')


if __name__ == "__main__":
    git_ops_connector = GitopsConnector()
