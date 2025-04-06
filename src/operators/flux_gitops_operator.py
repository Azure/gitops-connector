# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from collections import defaultdict
import logging
from operators.gitops_operator import GitopsOperatorInterface
from operators.git_commit_status import GitCommitStatus
from configuration.gitops_config import GitOpsConfig

KUSTOMIZATION_PHASE = "Kustomization"
PROGRESSING_STATE = "Progressing"
HEALTH_CHECK_FAILED_STATE = "HealthCheckFailed"


class FluxGitopsOperator(GitopsOperatorInterface):

    def __init__(self, gitops_config: GitOpsConfig):
        super().__init__(gitops_config)

    def extract_commit_statuses(self, phase_data):
        commit_statuses = []

        commit_id = self.get_commit_id(phase_data)

        reason_state = phase_data['reason']
        reason_message = self._map_reason_to_description(
            reason_state,
            phase_data['message'])
        kind = self._get_message_kind(phase_data)

        # Generic status message regardless of kind.
        status = self._new_git_commit_status(
            commit_id=commit_id,
            status_name='Status',
            state=reason_state,
            message=reason_message,
            kind=kind)
        commit_statuses.append(status)

        # For Kustomization we have more detailed data to parse in addition to status.
        if self._get_message_kind(phase_data) == KUSTOMIZATION_PHASE:
            if phase_data['reason'] == PROGRESSING_STATE:
                self._add_progression_summary(phase_data, commit_id, commit_statuses, kind)
                # For Progressive state adding a generic message again so the overall Status will be "pending"
                # (Bug in AzDO)
                status = self._new_git_commit_status(
                    commit_id=commit_id,
                    status_name='Status',
                    state=reason_state,
                    message=reason_message,
                    kind=kind)
                commit_statuses.append(status)
            elif phase_data['reason'] == HEALTH_CHECK_FAILED_STATE:
                self._add_health_check_summary(phase_data, commit_id, commit_statuses, reason_message, kind)

        return commit_statuses

    def _add_progression_summary(self, phase_data, commit_id, commit_statuses, kind):
        progression_summary = self._parse_kustomization_progression_summary(phase_data)
        if progression_summary:
            for (resource_name, status_msg) in progression_summary.items():
                status = self._new_git_commit_status(
                    commit_id=commit_id,
                    status_name=resource_name,
                    # As far as the Kustomize controller is concerned, these are finished
                    # before reconciliation starts. We don't want this to affect the overall
                    # status, so map to the relevant N/A status in the Git repo provider.
                    state="NotApplicable",
                    message=status_msg,
                    kind=kind)
                commit_statuses.append(status)

    def _add_health_check_summary(self, phase_data, commit_id, commit_statuses, reason_message, kind):
        health_check_summary = self._parse_health_check_summary(phase_data)
        if health_check_summary:
            for resource_name in health_check_summary:
                status = self._new_git_commit_status(
                    commit_id=commit_id,
                    status_name=resource_name,
                    state=HEALTH_CHECK_FAILED_STATE,
                    message=reason_message,
                    kind=kind)
                commit_statuses.append(status)

    def _parse_health_check_summary(self, phase_data):
        raw_message = phase_data['message']
        resources = []
        resources_array_start = raw_message.index("[")
        resources_array_end = raw_message.index("]")
        if resources_array_start > 0 and resources_array_end > 0 and resources_array_end > resources_array_start:
            resources_string = raw_message[resources_array_start + 1: resources_array_end - 1]
            if resources_string:
                resources = [r.strip() for r in resources_string.split(", ")]

        if not resources:
            resources.append(raw_message)
        return resources

    def _new_git_commit_status(self, commit_id, status_name, state, message, kind):
        return GitCommitStatus(
            commit_id=commit_id,
            status_name=status_name,
            state=state,
            message=message,
            callback_url=self.callback_url,
            gitops_operator='Flux',
            genre=kind)

    def is_finished(self, phase_data):
        status = phase_data['reason']
        kind = self._get_message_kind(phase_data)

        is_finished = kind == "Kustomization" and status != 'Progressing'

        is_successful = status == 'ReconciliationSucceeded'

        return is_finished, is_successful

    def get_commit_id(self, phase_data) -> str:
        revision = ''
        if self._get_message_kind(phase_data) == "Kustomization":
            if 'revision' in phase_data['metadata']:
                revision = phase_data['metadata']['revision']
            else:
                revision = phase_data['metadata']['kustomize.toolkit.fluxcd.io/revision']
        elif self._get_message_kind(phase_data) == 'GitRepository':
            if 'revision' in phase_data['metadata']:
                revision = phase_data['metadata']['revision']
            elif 'message' in phase_data['metadata']:
                return parse_fetch_message(phase_data['metadata']['message'])
            else:
                revision = phase_data['metadata']['source.toolkit.fluxcd.io/revision']

        return parse_commit_id(revision)
    
    def is_supported_operator(self, phase_data) -> bool:
        return (self.gitops_config.name == 'singleInstance' or
               (self.gitops_config.name != 'singleInstance' and 
                'gitops_connector_config_name' in phase_data['metadata'] and 
                phase_data['metadata']['gitops_connector_config_name'] == self.gitops_config.name))

    def is_supported_message(self, phase_data) -> bool:
        kind = self._get_message_kind(phase_data)
        logging.debug(f'Kind: {kind}')

        reason = phase_data['reason']
        logging.debug(f'Reason: {reason}')

        return self.is_supported_operator(phase_data) and (kind == 'Kustomization' or kind == 'GitRepository' and reason != 'NewArtifact')

    def _get_message_kind(self, phase_data) -> str:
        return phase_data['involvedObject']['kind']

    def _map_reason_to_description(self, reason, original_message):
        # Explicitly handle all statuses so we make sure we don't silently miss any.
        reason_description_map = {
            "ReconciliationSucceeded": original_message,
            "ReconciliationFailed": original_message,
            "Progressing": "Reconciliation underway.",
            "DependencyNotReady": original_message,
            "PruneFailed": original_message,
            "ArtifactFailed": original_message,
            "BuildFailed": original_message,
            "HealthCheckFailed": "Health Check Failed",
            "ValidationFailed": "Manifests validation failed.",
            "info": original_message,
            "error": original_message,
            "NewArtifact": original_message
        }
        return reason_description_map[reason]

    # Build and return an array of progression summaries.
    # For example, ["service: 6 configured"]
    def _parse_kustomization_progression_summary(self, phase_data):
        if phase_data['reason'] != "Progressing":
            return []

        # The message contains kubectl output of newline separated
        # resources and states. May contain a trailing newline.
        raw_message = phase_data['message']
        entries = raw_message.rstrip().split("\n")

        if not entries or len(entries) == 0:
            return

        # Iterate on the entries and build our map.
        # Raw entry example:
        #   deployment.apps/abc configured
        #   deployment.apps/def configured
        status_map = defaultdict(lambda: defaultdict(int))
        warning_count = 0
        status_arr = {}
        try:
            for entry in entries:
                # Split into resource and status
                if entry.startswith("Warning"):
                    warning_count += 1
                    continue

                entry_tuple = entry.split(" ")
                if len(entry_tuple) != 2:
                    raise RuntimeError("Parsing error")
                (resource, status) = entry_tuple

                # Disregard the resource name
                (resource_type, _, _) = resource.partition("/")
                status_map[resource_type][status] += 1

            # Build the status string array
            for (resource_name, statuses) in status_map.items():
                # service:
                summary = ""
                first = True
                for (status_name, status_count) in statuses.items():
                    if not first:
                        summary += ", "
                        first = False
                    # E.g. "5 configured"
                    summary += f'{status_count} {status_name}'
                status_arr[resource_name] = summary

            if warning_count > 0:
                status_arr['warnings'] = f'Warnings: {warning_count}'
        except RuntimeError:
            status_arr['Info'] = raw_message

        return status_arr


# Based on the Flux source
# https://github.com/fluxcd/pkg/blob/c7d085624bfbbf426b83e5042e5614f85aac8b36/git/utils.go#L124
def parse_commit_id(revision):
    if revision == "":
        return ""

    i = revision.rfind(":")
    if i > 0:
        return revision[i + 1:]

    revisionArray = revision.split('/')
    return revisionArray[-1]


def parse_fetch_message(message):
    revisionArray = message.split('/')
    return revisionArray[-1]
