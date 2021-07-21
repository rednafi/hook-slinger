from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class WebhookPayload(BaseModel):
    to_url: str  # Webhook callback url
    to_auth: str  # Webhook callback auth
    tag: str  # Add a type tag
    group: str  # Which group/section/schema the webhook belongs to
    payload: dict[str, Any]  # The actual payload to be sent to 'to_url'


@router.post("/hook_slinger/", tags=["hook"])
async def hook_slinger_view(webhook_payload: WebhookPayload) -> WebhookPayload:
    return webhook_payload
