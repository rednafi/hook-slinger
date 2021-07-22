from __future__ import annotations

import json
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

    from .views import WebhookPayload

__all__ = ("send_webhook",)

redis_conn = redis.Redis.from_url(config.REDIS_URL)
queue = Queue("wq", connection=redis_conn)


def validate_url(url: str) -> bool:
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

    return re.match(regex, url) is not None


def save_payload_to_db(webhook_payload: WebhookPayload) -> bool:
    webhook_payload = json.dumps(webhook_payload.dict())
    key = f"webhook_payload:{str(uuid.uuid4())}"
    return redis_conn.setex(key, config.PAYLOAD_TTL, webhook_payload)


def send_post_request(webhook_payload: WebhookPayload) -> bool | NoReturn:
    to_url = webhook_payload.to_url
    to_auth = webhook_payload.to_auth
    payload = webhook_payload.payload

    if not validate_url(to_url):
        raise ValueError("Value of 'to_url' is not a valid URL.")

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
        return response.status_code == HTTPStatus.OK


def send_webhook(*, webhook_payload: WebhookPayload):
    save_payload_to_db(webhook_payload)
    # Retry up to 3 times, with 60 seconds interval in between executions
    queue.enqueue(
        send_post_request,
        retry=Retry(max=config.MAX_RETRIES, interval=config.INTERVAL),
    )

    queue.enqueue(send_post_request, webhook_payload)
