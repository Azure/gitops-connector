
import dataclasses
import json
import logging
import os
import os.path
from urllib.parse import urlparse
import requests

SUBSCRIBERS_DIR = '/subscribers'


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
        logging.debug("Adding configured subscribers...")
        subscribers = RawSubscriberFactory._read_subscribers()
        logging.debug(f'{len(subscribers)} subscribers added.')

        return subscribers

    @staticmethod
    def _read_subscribers():
        subscribers = []

        try:
            subscriber_files = os.listdir(SUBSCRIBERS_DIR)
        except FileNotFoundError:
            logging.error("Subscriber config not found. Defaulting to no subscribers.")
            return subscribers
        if not subscriber_files:
            return subscribers

        for subscriber_file in subscriber_files:
            subscriber_file = os.path.join(SUBSCRIBERS_DIR, subscriber_file)
            if not os.path.isfile(subscriber_file):
                continue

            try:
                with open(subscriber_file, 'r') as subscriber_fh:
                    url = subscriber_fh.readline()

                    try:
                        urlparse(url)
                    except ValueError:
                        logging.error(f"URL is invalid, subscriber has not been added: {url}")
                        continue

                    subscriber = RawSubscriber(url)

                    subscribers.append(subscriber)
                    logging.info(f"Added subscriber {subscriber_file} with endpoint {url}")
            except OSError:
                logging.error(f"Error opening subscriber config at {subscriber_file}")
                continue

        return subscribers
