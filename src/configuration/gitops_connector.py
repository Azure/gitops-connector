# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import threading
from timeloop import Timeloop
from datetime import timedelta
import logging
from queue import PriorityQueue

from operators.gitops_operator_factory import GitopsOperatorFactory
from repositories.git_repository_factory import GitRepositoryFactory
from repositories.raw_subscriber import RawSubscriberFactory
from orchestrators.cicd_orchestrator_factory import CicdOrchestratorFactory
from configuration.gitops_config import GitOpsConfig

# Time in seconds between background PR cleanup jobs
PR_CLEANUP_INTERVAL = 1 * 30
DISABLE_POLLING_PR_TASK = False

# Instance is shared across threads.
class GitopsConnector:

    def __init__(self, gitops_config: GitOpsConfig):
        logging.debug(f'Creating GitopsConnector for {gitops_config.name}')
        self._gitops_config = gitops_config
        self._gitops_operator = GitopsOperatorFactory.new_gitops_operator(gitops_config)
        self._git_repository = GitRepositoryFactory.new_git_repository(gitops_config)
        self._cicd_orchestrator = CicdOrchestratorFactory.new_cicd_orchestrator(self._git_repository, gitops_config)

        self.status_thread = None
        self.status_thread_running = False
        
        self.cleanup_task = Timeloop()
        self.cleanup_task_running = False

        @self.cleanup_task.job(interval=timedelta(seconds=PR_CLEANUP_INTERVAL))
        def pr_polling_thread_worker():
            logging.info("Starting periodic PR cleanup")
            self.notify_abandoned_pr_tasks()
            logging.info(f'Finished PR cleanup, sleeping for {PR_CLEANUP_INTERVAL} seconds...')

        # Subscribers that take unprocessed JSON, forwarded from the notifications
        self._raw_subscribers = RawSubscriberFactory.new_raw_subscribers()

        # Commit status notification queue
        self._global_message_queue = PriorityQueue()

    def is_supported_message(self, payload):
        return self._gitops_operator.is_supported_message(payload)
    
    def start_background_work(self):
        self._start_status_thread()
        self._start_cleanup_task()

    def stop_background_work(self):
        self._stop_status_thread()
        self._stop_cleanup_task()

    def _start_status_thread(self):
        if not self.status_thread_running:
            self.status_thread_running = True
            self.status_thread = threading.Thread(target=self.drain_commit_status_queue)
            self.status_thread.start()
            logging.debug('Started status thread')

    def _stop_status_thread(self):
        if self.status_thread_running:
            self.status_thread_running = False
            if self.status_thread:
                # Force the queue loop to break once it's processed remaining messages
                self._global_message_queue.put(None)
                self.status_thread.join()
                logging.debug('Stopped status thread')

    def _start_cleanup_task(self):
        if not self.cleanup_task_running:
            self.cleanup_task_running = True
            self.cleanup_task.start()
            logging.debug('Started cleanup task')

    def _stop_cleanup_task(self):
        if self.cleanup_task_running:
            self.cleanup_task_running = False
            if self.cleanup_task:
                self.cleanup_task.stop()
                logging.debug('Stopped cleanup task')

    def process_gitops_phase(self, phase_data, req_time):
        if self._gitops_operator.is_supported_message(phase_data):
            commit_id = self._gitops_operator.get_commit_id(phase_data)
            if not self._git_repository.is_commit_finished(commit_id):
                self._queue_commit_statuses(phase_data, req_time)
                self._notify_orchestrator(phase_data, commit_id)
        else:
            logging.debug(f'Message is not supported: {phase_data}')

    def _queue_commit_statuses(self, phase_data, req_time):
        logging.debug('_queue_commit_statuses called')
        commit_statuses = self._gitops_operator.extract_commit_statuses(phase_data)
        for commit_status in commit_statuses:
            self._global_message_queue.put(item=(req_time, commit_status))

    def _notify_orchestrator(self, phase_data, commit_id):
        logging.debug('_notify_orchestrator called')
        is_finished, is_successful = self._gitops_operator.is_finished(phase_data)
        logging.debug(f'_notify_orchestrator: is_finished: {is_finished}, is_successful: {is_successful}')

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

