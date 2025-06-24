# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from flask import Flask, request
import logging
import kopf
from kubernetes import client, config
import atexit
import time
import utils
import os
from threading import Thread
from configuration.gitops_connector_manager import GitOpsConnectorManager
from configuration.gitops_config_operator import GitOpsConfigOperator
from configuration.gitops_config import GitOpsConfig

logging.basicConfig(level=logging.DEBUG)

application = Flask(__name__)

connector_manager = GitOpsConnectorManager()
gitops_config_operator = GitOpsConfigOperator(connector_manager)

git_repository_type = os.getenv('GIT_REPOSITORY_TYPE')
if git_repository_type:
    logging.debug('Detected ENV configuration data.  Running in single instance configuration mode.')
    singleInstanceConfig = GitOpsConfig(
        name='singleInstance',
        git_repository_type=utils.getenv('GIT_REPOSITORY_TYPE'),
        cicd_orchestrator_type=utils.getenv('CICD_ORCHESTRATOR_TYPE'),
        gitops_operator_type=utils.getenv('GITOPS_OPERATOR_TYPE'),
        gitops_app_url=utils.getenv('GITOPS_APP_URL'),
        azdo_gitops_repo_name=os.getenv('AZDO_GITOPS_REPO_NAME'),
        azdo_pr_repo_name=os.getenv('AZDO_PR_REPO_NAME'),
        azdo_org_url=os.getenv('AZDO_ORG_URL'),
        github_gitops_repo_name=os.getenv('GITHUB_GITOPS_REPO_NAME'),
        github_gitops_manifests_repo_name=os.getenv('GITHUB_GITOPS_MANIFEST_REPO_NAME'),
        github_org_url=os.getenv('GITHUB_ORG_URL')
    )
    connector_manager.add_or_update_configuration(singleInstanceConfig)
else:
    logging.debug('Detected no ENV configuration data.  Running in multiple instance configuration mode via gitopsconfig resources.')
    try:
        cluster_domain = utils.getenv('CLUSTER_DOMAIN')
        logging.debug(f"cluster domain: '{cluster_domain}'")
        config.load_incluster_config()  # In-cluster Kubernetes config
        api_instance = client.CustomObjectsApi()
        instances = api_instance.list_cluster_custom_object(cluster_domain, "v1", "gitopsconfigs")
        for instance in instances.get("items"):
            config_name = instance.get("metadata").get("name")
            config_namespace = instance.get("metadata").get("namespace")
            config_spec = instance.get("spec")
            gitops_config_operator.create(config_spec, config_name)
            logging.debug(f"Processing config: '{config_name}' in Namespace: '{config_namespace}'")
    except Exception as e:
        logging.error(f'Failed to load gitopsconfigs: {e}')

    @kopf.on.create('gitopsconfigs')
    def on_create(spec, name, **kwargs):
        gitops_config_operator.create(spec, name)

    @kopf.on.update('gitopsconfigs')
    def on_update(spec, name, **kwargs):
        gitops_config_operator.update(spec, name)

    @kopf.on.delete('gitopsconfigs')
    def on_delete(name, **kwargs):
        gitops_config_operator.delete(name)

    # Kopf operator task
    def run_kopf_operator():
        logging.info("Starting Kopf operator thread")
        gitops_config_operator.run()  # Start the operator

    kopf_thread = Thread(target=run_kopf_operator)
    kopf_thread.start()


@application.route("/gitopsphase", methods=['POST'])
def gitopsphase():
    # Use per process timer to stash the time we got the request
    req_time = time.monotonic_ns()

    raw_data = request.data.decode('utf-8')  # Decode byte data to string
    logging.debug(f'Raw request data: {raw_data}')

    # Ensure the request is JSON
    if not request.is_json:
        return "Invalid content type. Expected application/json.", 400

    try:
        payload = request.get_json()
    except Exception as e:
        logging.error(f'Failed to parse JSON. Error: {e}')
        return "Malformed JSON data", 400

    logging.debug(f'GitOps phase: {payload}')

    gitops_connector = connector_manager.get_supported_gitops_connector(payload)
    if gitops_connector is not None:
        gitops_connector.process_gitops_phase(payload, req_time)

    return f'GitOps phase: {payload}', 200


def interrupt():
    connector_manager.stop_all()


atexit.register(interrupt)


if __name__ == "__main__":
    application.run(host='0.0.0.0')
