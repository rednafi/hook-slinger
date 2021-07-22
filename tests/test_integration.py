"""
Integrations tests.
This is only expected to be run inside a docker container.
Run `make start_tests` to execture the tests.
"""

import httpx
from redis import Redis
from rq.job import Job
from http import HTTPStatus
import time

import config

redis_conn = Redis.from_url(config.REDIS_URL)


def test_webhook_throw():
    wh_payload = {
        "to_url": "https://webhook.site/aa7e2e7e-a62d-4505-8879-13bd806da6d5",
        "to_auth": "",
        "tag": "Dhaka",
        "group": "Bangladesh",
        "payload": {"greetings": "Hello, world!"},
    }

    with httpx.Client(http2=True) as session:

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {config.API_TOKEN}"
        }

        response = session.post(
            "http://app:5000/hook_slinger",
            headers=headers,
            json=wh_payload,
        )

        assert response.status_code == HTTPStatus.ACCEPTED

        result = response.json()
        job_id = result['job_id']
        job = Job.fetch(job_id, connection=redis_conn)
        maybe_queued = job.get_status()

        assert maybe_queued == "queued"

        counter = 1
        while True:
            maybe_finished = job.get_status()
            time.sleep(1)
            if maybe_finished == "finished":
                return
            print(maybe_finished)
            counter += 1
            if counter == 10:
                break
        raise TimeoutError('HTTP response took too long.')
