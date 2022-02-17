# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from flask import Flask, request
import logging
from timeloop import Timeloop
from datetime import timedelta
import atexit
import time
from threading import Thread
from gitops_connector import GitopsConnector

# Time in seconds between background PR cleanup jobs
PR_CLEANUP_INTERVAL = 1 * 30
DISABLE_POLLING_PR_TASK = False

logging.basicConfig(level=logging.DEBUG)

application = Flask(__name__)

gitops_connector = GitopsConnector()


@application.route("/gitopsphase", methods=['POST'])
def gitopsphase():
    # Use per process timer to stash the time we got the request
    req_time = time.monotonic_ns()

    payload = request.get_json()

    logging.debug(f'GitOps phase: {payload}')

    gitops_connector.process_gitops_phase(payload, req_time)

    return f'GitOps phase: {payload}', 200


# Periodic PR cleanup task
cleanup_task = Timeloop()


@cleanup_task.job(interval=timedelta(seconds=PR_CLEANUP_INTERVAL))
def pr_polling_thread_worker():
    logging.info("Starting periodic PR cleanup")
    gitops_connector.notify_abandoned_pr_tasks()
    logging.info(f'Finished PR cleanup, sleeping for {PR_CLEANUP_INTERVAL} seconds...')


# Git status queue drain task
def init_commit_status_thread():
    logging.info("Starting commit status thread")
    status_thread = Thread(target=gitops_connector.drain_commit_status_queue)
    status_thread.start()


def interrupt():
    if not DISABLE_POLLING_PR_TASK:
        cleanup_task.stop()


if not DISABLE_POLLING_PR_TASK:
    cleanup_task.start()
    init_commit_status_thread()
    atexit.register(interrupt)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
