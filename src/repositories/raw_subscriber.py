
import dataclasses
import json
import logging
import os
import requests


# An endpoint that handles unprocessed JSON forwarded from notifications.
class RawSubscriber:
    def __init__(self, url_endpoint):
        self._url_endpoint = url_endpoint

    def post_commit_status(self, commit_status):
        json_data = dataclasses.asdict(commit_status)
        logging.debug("Sending raw json to subscriber: " + json.dumps(json_data))
        response = requests.post(url=self._url_endpoint, json=json_data)
        response.raise_for_status()


class RawSubscriberFactory:
    @staticmethod
    def new_raw_subscribers() -> list[RawSubscriber]:
        subscribers = []

        logging.debug("Adding configured subscribers...")

        # TODO(tcare): Dynamically pick up subscribers via CRD or similar
        # Currently we only have one subscriber
        endpoint = os.getenv("RAW_SUBSCRIBER_ENDPOINT")
        if endpoint:
            subscriber = RawSubscriber(endpoint)
            subscribers.append(subscriber)

        logging.debug(f'{len(subscribers)} subscribers added.')

        return subscribers
