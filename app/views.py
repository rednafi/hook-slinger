from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

import config

from .services import send_webhook


class WebhookPayload(BaseModel):
    """Pydantic model to declare and validate webhook payload."""

    to_url: str  # Webhook callback url
    to_auth: Optional[str]  # Webhook callback auth
    tag: Optional[str]  # Add a type tag
    group: Optional[str]  # Which group/section/schema the webhook belongs to
    payload: dict[str, Any]  # The actual payload to be sent to 'to_url'


class APIResponsePayload(BaseModel):
    """Pydantic model to declare the response json shape of hook slinger API."""


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
        error = "secret_key must be passed as a header field"
    else:
        error = "Wrong secret key. Did you forget to add the 'API_TOKEN' to the '.env'?"

    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=error)


@router.post(
    "/hook_slinger/",
    tags=["hook"],
    dependencies=[Depends(secret_based_security)],
)
async def hook_slinger_view(
    webhook_payload: WebhookPayload,
) -> WebhookPayload:

    send_webhook(webhook_payload=webhook_payload)
    return webhook_payload
