"""
Integrations tests.
This is only expected to be run inside a docker container.
Run `make start_tests` to execute the tests.
"""

import logging
import time
from http import HTTPStatus
from pprint import pprint

import httpx
from redis import Redis
from rq.job import Job, JobStatus

import config

redis_conn = Redis.from_url(config.REDIS_URL)


def test_webhook_throw():
    # Payload that is sent from the sending service to Hook Slinger.
    # Here, the 'test_webhook_throw' function acts as the service that sends
    # the webhook payload to the Hook Slinger container.
    wh_payload = {
        "to_url": "https://webhook.site/37ad9530-59c3-430d-9db6-e68317321a9f",
        "to_auth": "",
        "tag": "Dhaka",
        "group": "Bangladesh",
        "payload": {"greetings": "Hello, world!"},
    }

    with httpx.Client(http2=True) as session:
        # In this case, we're using the default API token.
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {config.API_TOKEN}",
        }

        response = session.post(
            "http://app:5000/hook_slinger",
            headers=headers,
            json=wh_payload,
        )

        # Inspecting the HTTP response status code.
        assert response.status_code == HTTPStatus.ACCEPTED
        logging.info(f"Got the expected HTTP status code: {response.status_code}.")

        # Inspecting the HTTP response payload.
        result = response.json()
        logging.info(f"HTTP response payload: {pprint(result)}\n")

        # This section first looks for the 'job_id' in the response payload.
        # Using the 'job_id', it makes a query against the Redis server to get
        # the job status. The expected 'job_status' is 'queued'.
        job_id = result["job_id"]
        job = Job.fetch(job_id, connection=redis_conn)
        maybe_queued = job.get_status()

        assert maybe_queued == JobStatus.QUEUED
        logging.info(f"Got the expected Job Status: {maybe_queued}\n")

        # This section polls the Redis server 10 times with 1 second interval
        # between each requests. It waits to see if the 'job_status' has been
        # changed from 'queued' to 'finished'. The test passes if the transition
        # happens within 10 seconds.
        counter = 1
        logging.info("Started polling to see if the Job finishes...")
        while True:
            maybe_finished = job.get_status()
            if maybe_finished == JobStatus.FINISHED:
                logging.info(
                    f"Current Job Status: {maybe_finished} \n"
                    f"Expected Job Status: {JobStatus.FINISHED}\n"
                )
                logging.info("Successfully passed the integration test.")
                return None

            logging.info(
                f"Current Job Status: {maybe_finished} \n"
                f"Expected Job Status: {JobStatus.FINISHED}\n"
            )
            counter += 1
            time.sleep(1)
            if counter > 10:
                raise TimeoutError("HTTP response took too long.")
