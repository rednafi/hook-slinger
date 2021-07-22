from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from .services import send_webhook


class WebhookPayload(BaseModel):
    """Pydantic model to declare and validate webhook payload."""

    to_url: str  # Webhook callback url
    to_auth: Optional[str]  # Webhook callback auth
    tag: Optional[str]  # Add a type tag
    group: Optional[str]  # Which group/section/schema the webhook belongs to
    payload: dict[str, Any]  # The actual payload to be sent to 'to_url'


router = APIRouter()


@router.post("/hook_slinger/", tags=["hook"])
async def hook_slinger_view(webhook_payload: WebhookPayload) -> WebhookPayload:
    send_webhook(webhook_payload=webhook_payload)
    return webhook_payload
