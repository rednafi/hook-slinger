from __future__ import annotations

from http import HTTPStatus
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette.exceptions import HTTPException

import config

from .services import send_webhook, validate_url


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
                "to_url": "https://webhook.site/aa7e2e7e-a62d-4505-8879-13bd806da6d5",
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

    status: Literal["registered"]
    ok: bool
    message: str

    class Config:
        schema_extra = {
            "example": {
                "status": "registered",
                "ok": True,
                "message": "Webhook registration successful.",
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
        "to_url": "https://webhook.site/aa7e2e7e-a62d-4505-8879-13bd806da6d5",
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
        send_webhook(webhook_payload=webhook_payload)
        return SlingerResponsePayload(
            status="registered",
            ok=True,
            message="Webhook registration successful.",
        )

    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Webhook registration failed.",
        )
