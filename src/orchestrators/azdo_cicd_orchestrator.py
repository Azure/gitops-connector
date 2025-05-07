# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import logging
import json
import requests
from datetime import datetime, timedelta
import dateutil.parser
from orchestrators.cicd_orchestrator import CicdOrchestratorInterface
from repositories.git_repository import GitRepositoryInterface
from clients.azdo_client import AzdoClient
from configuration.gitops_config import GitOpsConfig

# Callback task timeout in minutes. PRs abandoned before this time will not be processed.
MAX_TASK_TIMEOUT = 72 * 60
TASK_CUTOFF_DURATION = timedelta(minutes=MAX_TASK_TIMEOUT)


class AzdoCicdOrchestrator(CicdOrchestratorInterface):

    def __init__(self, git_repository: GitRepositoryInterface, gitops_config: GitOpsConfig):
        super().__init__(git_repository)
        self.azdo_client = AzdoClient(gitops_config)
        self.headers = self.azdo_client.get_rest_api_headers()

    def notify_on_deployment_completion(self, commit_id, is_successful):
        logging.debug(f'notify_on_deployment_completion called.  commit_id: {commit_id}, is_successful: {is_successful}')
        pr_num = self.git_repository.get_pr_num(commit_id)
        logging.debug(f'notify_on_deployment_completion:  pr_num: {pr_num}')
        if pr_num:
            self._update_pr_task(is_successful, pr_num)

    # Update the Azure Pipeline task waiting for the PR to complete.
    # is_alive: If true, the PR is active and absence of task data is an error.
    def _update_pr_task(self, is_successful, pr_num, is_alive=True):
        logging.debug(f'_update_pr_task called. is_successful: {is_successful}, pr_num: {pr_num}')
        pr_task = self._get_pr_task_data(pr_num, is_alive)
        if not pr_task:
            if is_alive:
                logging.error(f'PR {pr_num} has no metadata! Cannot complete task callback.')
            else:
                logging.error(f'PR {pr_num} has no metadata! Returning false as is_alive is False.')
            return False
        logging.info(f'PR {pr_num}: Rollout {is_successful}, attempting task completion callback...')

        if is_successful:
            state = 'succeeded'
        else:
            state = 'failed'

        # The build task may have been cancelled, timed out, etc.
        # Working with the plan in this state can cause 500 errors.
        # Finish gracefully so ArgoCD doesn't keep calling us.
        if self._plan_already_completed(pr_task):
            logging.debug(f'_plan_already_completed for pr_task :{pr_task} if True so exit early')
            return False

        planurl = pr_task['planurl']
        projectid = pr_task['projectid']
        planid = pr_task['planid']
        url = f'{planurl}{projectid}/_apis/distributedtask/hubs/build/plans/{planid}/events?api-version=2.0-preview.1'
        data = {
            'name': "TaskCompleted",
            'taskId': pr_task['taskid'],
            'jobId': pr_task['jobid'],
            'result': state
        }
        logging.debug(f'Update PR task request content: {url}, body: {json.dumps(data, indent=2)}')
        response = requests.post(url=url, headers=self.headers, json=data)
        logging.debug(f'Update PR task response content: {response.content}')
        # Throw appropriate exception if request failed
        response.raise_for_status()

        logging.info(f'PR {pr_num}: Successfully completed task {pr_task["taskid"]}')
        return True

    def _get_pr_task_data(self, pr_num, is_alive=True):
        logging.debug(f'_get_pr_task_data called.  pr_num: {pr_num}, is_alive: {is_alive}')
        return self.git_repository.get_pr_metadata(pr_num)
    
    # Given a PR task, check if it's parent plan has already completed.
    # Note: Completed does not necessarily mean it succeeded.
    def _plan_already_completed(self, pr_task):
        planurl = pr_task['planurl']
        projectid = pr_task['projectid']
        planid = pr_task['planid']
        url = f'{planurl}{projectid}/_apis/distributedtask/hubs/build/plans/{planid}'

        response = requests.get(url=url, headers=self.headers)
        # Throw appropriate exception if request failed
        response.raise_for_status()

        plan_info = response.json()
        state = plan_info['state']
        logging.debug(f'Check if plan {planid} already completed: state = {state}')
        plan_state = plan_info['state'] == 'completed'
        if plan_state:
            return True
        return self._build_job_already_completed(pr_task, plan_info)

    def _find_record_by_id(self, records, target_id):
        for record in records:
            if record['id'] == target_id:
                return record
        return None

    def _build_job_already_completed(self, pr_task, plan_info):
        urlBase = plan_info['owner']['_links']['self']['href']
        url = f'{urlBase}/timeline?api-version=7.1'

        response = requests.get(url=url, headers=self.headers)
        # Throw appropriate exception if request failed
        response.raise_for_status()

        timeline = response.json()
        records = timeline['records']
        job_id = pr_task['jobid']
        job = self._find_record_by_id(records, job_id)
        job_state = job['state']
        logging.debug(f'Check if job {job_id} already completed: state = {job_state}')
        job_state_completed = job_state == 'completed'
        return job_state_completed
    
    def notify_abandoned_pr_tasks(self):
        logging.debug('notify_abandoned_pr_tasks called')
        update_count = 0
        prs = self.git_repository.get_prs('abandoned')

        if prs:
            for pr in prs:
                if not self._should_update_abandoned_pr(pr):
                    continue

                pr_num = pr['pullRequestId']
                if not self._update_abandoned_pr(pr_num, pr_data=pr):
                    update_count += 1
                    logging.debug(f'Updated abandoned PR {pr_num}')

        if update_count > 0:
            logging.info(f'Processed {update_count} abandoned PRs via query')

    def _should_update_abandoned_pr(self, pr_data):
        logging.debug(f'_should_update_abandoned_pr called. pr_data: {json.dumps(pr_data, indent=2)}')
        closed_date = pr_data.get('closedDate')
        if not closed_date:
            logging.debug('_should_update_abandoned_pr.  closed_date not provided so should update')
            return True

        # Azure DevOps returns a ISO 8601 formatted datetime string.
        closed_datetime = dateutil.parser.isoparse(closed_date)

        # Azure DevOps returns a timezone, so make now() relative to that.
        now = datetime.now(closed_datetime.tzinfo)

        should_update = now - TASK_CUTOFF_DURATION <= closed_datetime
        logging.debug(f'_should_update_abandoned_pr.  should_update: {should_update}')
        return should_update

    # Returns False if the PR is no longer alive and we notified the task.
    def _update_abandoned_pr(self, pr_num, pr_data):
        pr_status = pr_data['status']
        logging.debug(f'_update_abandoned_pr called. pr_num: {pr_num}, pr_status: {pr_status}')
        if (pr_status == 'abandoned'):
            # update_pr_task returns True if the task was updated.
            return not self._update_pr_task(False, str(pr_num), is_alive=False)
        return True
