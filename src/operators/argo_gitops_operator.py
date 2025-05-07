# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import logging
import json
from operators.gitops_operator import GitopsOperatorInterface
from operators.git_commit_status import GitCommitStatus
from configuration.gitops_config import GitOpsConfig

class ArgoGitopsOperator(GitopsOperatorInterface):

    def __init__(self, gitops_config: GitOpsConfig):
        super().__init__(gitops_config)

    def extract_commit_statuses(self, phase_data):
        logging.debug(f'extract_commit_statuses called.  phase_data: {json.dumps(phase_data, indent=2)}')
        commit_statuses = []

        commit_id = self.get_commit_id(phase_data)
        phase_status, sync_status, health_status = self._get_statuses(phase_data)

        phase_status = self._new_git_commit_status(
            commit_id=commit_id,
            status_name='Phase',
            state=phase_status,
            message=phase_data['phase'] + ": " + phase_data['message'])
        commit_statuses.append(phase_status)

        (health_summary, sync_summary) = self._get_deployment_status_summary(phase_data['resources'])

        sync_status = self._new_git_commit_status(
            commit_id=commit_id,
            status_name='Sync',
            state=sync_status,
            message=sync_summary)
        commit_statuses.append(sync_status)

        health_status = self._new_git_commit_status(
            commit_id=commit_id,
            status_name='Health',
            state=health_status,
            message=health_summary)
        commit_statuses.append(health_status)

        return commit_statuses

    def is_finished(self, phase_data):
        logging.debug(f'is_finished called.  phase_data: {json.dumps(phase_data, indent=2)}')
        phase_status, _, health_status = self._get_statuses(phase_data)
        logging.debug(f'is_finished: phase_status: {phase_status}, health_status: {health_status}')
        
        is_finished = \
            phase_status != 'Inconclusive' \
            and phase_status != 'Running' \
            and health_status != 'Progressing'

        is_successful = phase_status == 'Succeeded' and health_status == 'Healthy'

        logging.debug(f'is_finished: is_finished: {is_finished}, is_successful: {is_successful}')
        return is_finished, is_successful

    def get_commit_id(self, phase_data) -> str:
        return phase_data['commitid']

    def _get_statuses(self, phase_data):
        return phase_data['phase'], phase_data['sync_status'], phase_data['health']

    def _new_git_commit_status(self, commit_id, status_name, state, message: str):
        return GitCommitStatus(commit_id=commit_id,
            status_name=status_name,
            state=state,
            message=message,
            callback_url=self.callback_url,
            gitops_operator='ArgoCD',
            genre='ArgoCD')

    def is_supported_operator(self, phase_data) -> bool:
        return (self.gitops_config.name == 'singleInstance' or
                self.gitops_config.name != 'singleInstance' and phase_data.get('gitops_connector_config_name') == self.gitops_config.name)

    def is_supported_message(self, phase_data) -> bool:
        if ((not self.is_supported_operator(phase_data)) or
            phase_data['commitid'] == "<no value>" or 
            phase_data['resources'] == None):
            return False
        return True

    def _get_deployment_status_summary(self, resources):
        total = len(resources)
        health_count = {}
        sync_count = {}

        for resource in resources:
            if 'health' in resource:  # not every resource has health key
                health = resource['health']['status']
                health_count[health] = health_count.get(health, 0) + 1
            if 'status' in resource:  # not every resource has status key
                sync_count[resource['status']] = sync_count.get(resource['status'], 0) + 1

        def summarize(status_count):
            status_summary = ""
            first = True
            for status, count in status_count.items():
                if first is not True:
                    status_summary += ", "
                else:
                    first = False
                status_summary += "%d/%d %s" % (count, total, status)
            return status_summary

        return (summarize(health_count), summarize(sync_count))
