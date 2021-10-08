from http import HTTPStatus
from unittest.mock import patch

import httpx
import pytest

from app import services, views


def test_public_methods():
    assert services.__all__ == ("send_webhook", "validate_url")


def test_webhook_post_failed_error():
    assert issubclass(services.WebhookPostFailedError, Exception)

    # Test docstring.
    expected_docstring = (
        "Raises this when sending the webhook post request fails "
        "due to some HTTP error."
    )
    expected_docstring = expected_docstring.lower()
    expected_docstring = " ".join(expected_docstring.split())
    expected_docstring = " ".join(expected_docstring.splitlines())

    current_docstring = services.WebhookPostFailedError.__doc__
    current_docstring = current_docstring.lower()
    current_docstring = " ".join(current_docstring.splitlines())
    current_docstring = " ".join(current_docstring.split())

    assert current_docstring == expected_docstring

    # Test traceback.
    assert services.WebhookPostFailedError("failed").__traceback__ is None

    # Test exception arguments.
    assert services.WebhookPostFailedError("failed").args == ("failed",)

    # Raise error.
    with pytest.raises(services.WebhookPostFailedError):
        raise services.WebhookPostFailedError("webhook failed")


def test_validate_url():
    with pytest.raises(ValueError):
        services.validate_url("https:sfsdfdsff")
        services.validate_url("http:google.com")
        services.validate_url("https://sfsdfdsff")

    assert services.validate_url("http://localhost:8000") == "http://localhost:8000"
    assert services.validate_url("https://google.com") == "https://google.com"


@patch("app.services.httpx.Client.post", autospec=True)
def test_send_post_request(mock_post):
    webhook_request = {
        "to_url": "https://webhook.site/37ad9530-59c3-430d-9db6-e68317321a9f",
        "to_auth": "",
        "tag": "Dhaka",
        "group": "Bangladesh",
        "payload": {
            "greetings": "Hello, world!",
        },
    }

    webhook_payload = views.SlingerRequestPayload(**webhook_request)
    mock_post.return_value = httpx.Response(
        status_code=HTTPStatus.OK,
        json=webhook_request,
    )
    mock_post.return_value.status_code = HTTPStatus.OK

    assert services.send_post_request(webhook_payload=webhook_payload) is None


@pytest.mark.dummy
@patch("app.services.redis_conn")
def test_redis_conn(mock_redis_conn):
    """Dummy testing Redis connection, this doesn't do anything."""

    mock_redis_conn.return_value = 42
    assert mock_redis_conn() == 42


@pytest.mark.dummy
@patch("app.services.queue")
def test_redis_queue(mock_redis_queue):
    """Dummy testing Redis queue, this doesn't do anything."""

    mock_redis_queue.return_value = 42
    assert mock_redis_queue() == 42


@patch("app.services.send_webhook", autospec=True)
def test_send_webhook(mock_send_webhook):
    webhook_request = {
        "to_url": "https://webhook.site/37ad9530-59c3-430d-9db6-e68317321a9f",
        "to_auth": "",
        "tag": "Dhaka",
        "group": "Bangladesh",
        "payload": {
            "greetings": "Hello, world!",
        },
    }

    webhook_payload = views.SlingerRequestPayload(**webhook_request)
    webhook_response = {
        "job_id": "Bangladesh_Dhaka_139fc35a-d2a5-4d01-a6af-e980c52f55bc",
        "message": "Webhook registration successful.",
        "ok": True,
        "queued_at": "2021-07-23T20:15:04.389690",
        "status": "queued",
    }

    mock_send_webhook.return_value = httpx.Response(
        status_code=HTTPStatus.OK, json=webhook_response
    )

    response = services.send_webhook(webhook_payload=webhook_payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == webhook_response
