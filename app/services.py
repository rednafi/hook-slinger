from __future__ import annotations

import json
import re
import typing
import uuid
from http import HTTPStatus
from typing import Any

import httpx
import redis
import rq

import config

if typing.TYPE_CHECKING:
    from .views import WebhookPayload

redis_conn = redis.Redis.from_url(config.REDIS_DSN)
queue = rq.Queue("webhook_queue", connection=redis_conn)


def _validate_url(url: str) -> bool:
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


def _save_payload_to_db(webhook_payload: WebhookPayload) -> bool:
    webhook_payload = json.dumps(webhook_payload.dict())
    key = f"webhook_payload:{str(uuid.uuid4())}"
    return redis_conn.setex(key, config.PAYLOAD_TTL, webhook_payload)


def _send_post_request(webhook_payload: WebhookPayload) -> bool:
    to_url = webhook_payload.to_url
    to_auth = webhook_payload.to_auth
    payload = webhook_payload.payload

    if not _validate_url(to_url):
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
    _save_payload_to_db(webhook_payload)
    queue.enqueue(_send_post_request, webhook_payload)
