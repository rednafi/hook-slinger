from __future__ import annotations

from datetime import datetime
from enum import Enum
from http import HTTPStatus
from typing import Any, Optional

from fastapi import APIRouter, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette.exceptions import HTTPException

import config

from .services import send_webhook, validate_url


class JobStatus(str, Enum):
    """RQ job status, shamelessly copied from the RQ source."""

    QUEUED = "queued"
    FINISHED = "finished"
    FAILED = "failed"
    STARTED = "started"
    DEFERRED = "deferred"
    SCHEDULED = "scheduled"
    STOPPED = "stopped"


class SlingerRequestPayload(BaseModel):
    """Pydantic model to declare and validate webhook payload."""

    to_url: str  # Webhook callback url
    to_auth: Optional[str]  # Webhook callback auth
    tag: Optional[str]  # Add a type tag
    group: Optional[str]  # Which group/section/schema the webhook belongs to
    payload: dict[str, Any]  # The actual payload to be sent to 'to_url'

    class Config:
        schema_extra = {
            "example": {
                "to_url": "https://webhook.site/37ad9530-59c3-430d-9db6-e68317321a9f",
                "to_auth": "",
                "tag": "Dhaka",
                "group": "Bangladesh",
                "payload": {
                    "greetings": "Hello, world!",
                },
            }
        }


class SlingerResponsePayload(BaseModel):
    """Pydantic model to declare the response json shape of hook slinger API."""

    status: JobStatus
    ok: bool
    message: str
    job_id: Optional[str]
    queued_at: str = datetime.utcnow().isoformat()

    class Config:
        schema_extra = {
            "example": {
                "status": "registered",
                "ok": True,
                "message": "Webhook registration successful.",
                "job_id": "Bangladesh_Dhaka_0f8346f4-8b84-4dc1-9df3-a5c09024e45c",
                "queued_at": "2021-07-23T19:38:41.061838",
            },
        }


router = APIRouter()

SECRET_KEY_NAME = "Authorization"
secret_header = APIKeyHeader(
    name=SECRET_KEY_NAME,
    scheme_name="Secret header",
    auto_error=False,
)
SECRET = f"Token {config.API_TOKEN}"


async def secret_based_security(header_param: str = Security(secret_header)):
    """
    Args:
        header_param: parsed header field secret_header
    Returns:
        True if the authentication was successful
    Raises:
        HTTPException if the authentication failed
    """

    if header_param == SECRET:
        return True
    if not header_param:
        error = (
            "Did you forget to add 'Authorization' field to the request header? "
            "You can find the auth key in the '.env' file as 'API_KEY'. "
            "Also, you have to prepend the auth protocol before the token. "
            "For example: 'Authorization: Token <token_value>' "
        )
    else:
        error = (
            "Wrong API auth key. "
            "Did you forget to add 'Authorization' field to the request header? "
            "You can find the auth key in the '.env' file as 'API_KEY'. Also, you have to prepend the auth protocol before the token. "
            "For example: 'Authorization: Token <token_value>' "
        )

    raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=error)


@router.post(
    "/hook_slinger/",
    tags=["hook"],
    dependencies=[Depends(secret_based_security)],
    status_code=HTTPStatus.ACCEPTED,
    response_model=SlingerResponsePayload,
)
async def hook_slinger_view(
    webhook_payload: SlingerRequestPayload,
) -> SlingerResponsePayload:

    """
    # Hook Slinger Router API

    ## Description

    Send, retry, and manage webhooks with Redis Queue.

    Click the Authorize lock button and add the following API token from the `.env` file:

    ```
    Token $5$1O/inyTZhNvFt.GW$Zfckz9OL.lm2wh3IewTm8YJ914wjz5txFnXG5XW.wb4
    ```

    Make a `POST` request to the following endpoint:

    ```
    http://localhost:5000/hook_slinger/
    ```

    The API Payload should have the following schema:

    ```
    {
        "to_url": "https://webhook.site/37ad9530-59c3-430d-9db6-e68317321a9f",
        "to_auth": "",
        "tag": "Dhaka",
        "group": "Bangladesh",
        "payload": {
            "greetings": "Hello, world!"
        }
    }
    ```
    Here:
    * `to_url` is the destination URL where the webhook is intended to be sent.
    * `to_auth` is the auth token expected by the webhook destination server,
        can be an empty string if the server doesn't require any authentication.
    * `tag` is any identifier string, can be empty.
    * `group` is another identifier string, can be empty.
    * `payload` the payload that is intended to be sent to `to_url`, can be an empty dict.

    """

    try:
        validate_url(webhook_payload.to_url)
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Parameter 'to_url' is not a valid URL.",
        )

    try:
        job = send_webhook(webhook_payload=webhook_payload)
        return SlingerResponsePayload(
            status=job.get_status(),
            ok=True,
            message="Webhook registration successful.",
            job_id=job.get_id(),
        )

    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Webhook registration failed.",
        )
