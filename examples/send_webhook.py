# Requires python3.8 and up!

import asyncio
from http import HTTPStatus
from pprint import pprint

import httpx


async def send_webhook() -> None:

    wh_payload = {
        "to_url": "https://webhook.site/f864d28d-9162-4ad5-9205-458e2b561c07",
        "to_auth": "",
        "tag": "Dhaka",
        "group": "Bangladesh",
        "payload": {"greetings": "Hello, world!"},
    }

    async with httpx.AsyncClient(http2=True) as session:
        headers = {
            "Content-Type": "application/json",
            "Authorization": (
                "Token $5$1O/inyTZhNvFt.GW$Zfckz9OL.lm2wh3IewTm8YJ914wjz5txFnXG5XW.wb4"
            ),
        }

        response = await session.post(
            "http://localhost:5000/hook_slinger",
            headers=headers,
            json=wh_payload,
            follow_redirects=True,
        )

        # Hook Slinger returns http code 202, accepted, for a successful request.
        assert response.status_code == HTTPStatus.ACCEPTED
        result = response.json()
        pprint(result)


if __name__ == "__main__":
    asyncio.run(send_webhook())
