from __future__ import annotations

import re
import typing
import uuid
from http import HTTPStatus

import httpx
import redis
from rq import Queue, Retry

import config

if typing.TYPE_CHECKING:
    from typing import NoReturn

    from rq.job import Job

    from .views import SlingerRequestPayload

__all__ = ("send_webhook", "validate_url")


class WebhookPostFailedError(Exception):
    """Raises this when sending the webhook post request fails due to
    some HTTP error."""


def validate_url(url: str) -> str | NoReturn:
    # This was shamelessly copied from old Django source code.
    # https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if re.match(regex, url) is None:
        raise ValueError("Value of 'url' is not a valid URL.")

    return url


def send_post_request(webhook_payload: SlingerRequestPayload) -> NoReturn:
    to_url = webhook_payload.to_url
    to_auth = webhook_payload.to_auth
    payload = webhook_payload.payload

    if to_auth:
        headers = {
            "Content-Type": "application/json",
            "Authorization": to_auth,
        }

    else:
        headers = {
            "Content-Type": "application/json",
        }

    with httpx.Client(http2=True) as session:
        response = session.post(
            to_url,
            headers=headers,
            json=payload,
            timeout=config.HTTP_TIMEOUT,
        )

        if not response.status_code == HTTPStatus.OK:
            raise WebhookPostFailedError(
                f"Sending webhook failed.\n"
                f"to_url: {to_url}\n"
                f"payload: {payload}\n"
            )


redis_conn = redis.Redis.from_url(config.REDIS_URL)
queue = Queue(config.QUEUE_NAME, connection=redis_conn)


def send_webhook(*, webhook_payload: SlingerRequestPayload) -> Job:
    return queue.enqueue(
        send_post_request,
        webhook_payload,
        retry=Retry(max=config.MAX_RETRIES, interval=config.INTERVAL),
        job_id=f"{webhook_payload.group}_{webhook_payload.tag}_{str(uuid.uuid4())}",
    )
