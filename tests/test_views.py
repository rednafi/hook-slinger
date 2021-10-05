from http import HTTPStatus
from unittest.mock import patch

import httpx
import pytest
from rq.job import JobStatus
from starlette.exceptions import HTTPException

from app import views


def test_slinger_request_payload():
    webhook_request_payload = {
        "to_url": "https://webhook.site/37ad9530-59c3-430d-9db6-e68317321a9f",
        "to_auth": "",
        "tag": "Dhaka",
        "group": "Bangladesh",
        "payload": {
            "greetings": "Hello, world!",
        },
    }

    slinger_request_payload_obj = views.SlingerRequestPayload(
        **webhook_request_payload,
    )
    assert slinger_request_payload_obj.to_url == webhook_request_payload["to_url"]
    assert slinger_request_payload_obj.to_auth == webhook_request_payload["to_auth"]
    assert slinger_request_payload_obj.tag == webhook_request_payload["tag"]
    assert slinger_request_payload_obj.group == webhook_request_payload["group"]
    assert slinger_request_payload_obj.payload == webhook_request_payload["payload"]


def test_slinger_response_payload():
    webhook_response_payload = {
        "status": JobStatus.QUEUED,
        "ok": True,
        "message": "Webhook registration successful.",
        "job_id": "Bangladesh_Dhaka_0f8346f4-8b84-4dc1-9df3-a5c09024e45c",
        "queued_at": "2021-07-23T19:38:41.061838",
    }

    slinger_response_payload_obj = views.SlingerResponsePayload(
        **webhook_response_payload,
    )
    assert slinger_response_payload_obj.status == webhook_response_payload["status"]
    assert slinger_response_payload_obj.ok == webhook_response_payload["ok"]
    assert slinger_response_payload_obj.message == webhook_response_payload["message"]
    assert slinger_response_payload_obj.job_id == webhook_response_payload["job_id"]
    assert (
        slinger_response_payload_obj.queued_at == webhook_response_payload["queued_at"]
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "header_param, return_value",
    (
        ("Token $5$1O/inyTZhNvFt.GW$Zfckz9OL.lm2wh3IewTm8YJ914wjz5txFnXG5XW.wb4", True),
        ("abcd", pytest.raises(HTTPException)),
        ("dummy", pytest.raises(HTTPException)),
    ),
)
async def test_secret_based_security(header_param, return_value):
    if isinstance(return_value, bool):
        assert (
            await views.secret_based_security(header_param=header_param) == return_value
        )

    else:
        with return_value:
            assert (
                await views.secret_based_security(header_param=header_param)
                == return_value
            )


@pytest.mark.dummy
@patch("httpx.Client.post")
def test_hook_slinger_view(mock_post):

    # Define HTTP request attributes
    # -------------------------------
    webhook_request = {
        "to_url": "https://webhook.site/37ad9530-59c3-430d-9db6-e68317321a9f",
        "to_auth": "",
        "tag": "Dhaka",
        "group": "Bangladesh",
        "payload": {
            "greetings": "Hello, world!",
        },
    }

    webhook_response = {
        "job_id": "Bangladesh_Dhaka_139fc35a-d2a5-4d01-a6af-e980c52f55bc",
        "message": "Webhook registration successful.",
        "ok": True,
        "queued_at": "2021-07-23T20:15:04.389690",
        "status": "queued",
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token 1234",
    }

    # Mock client.post
    # ----------------
    mock_post.return_value = httpx.Response(
        status_code=HTTPStatus.OK, json=webhook_response
    )

    # Make HTTP request
    # -----------------
    with httpx.Client(http2=True) as session:
        response = session.post(
            url="hook_slinger/",
            headers=headers,
            json=webhook_request,
        )

    # Assert
    # ------
    assert response.status_code == HTTPStatus.OK
    assert response.json() == webhook_response
