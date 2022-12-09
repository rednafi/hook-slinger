<div align="center">


![logo][logo]

<strong>>> <i>A generic service to send, retry, and manage webhooks.</i> <<</strong>

[![forthebadge][black-magic-badge]][forthebadge]
[![forthebadge][build-with-love-badge]][forthebadge]
[![forthebadge][made-with-python-badge]][forthebadge]

</div>

## Description

### What?

Hook Slinger acts as a simple service that lets you send, retry, and manage
event-triggered POST requests, aka webhooks. It provides a fully self-contained docker
image that is easy to orchestrate, manage, and scale.

### Why?

Technically, a webhook is a mere POST request—triggered by a system—when a particular
event occurs. The following diagram shows how a simple POST request takes the webhook
nomenclature when invoked by an event trigger.

![Webhook Concept][webhook-concept]

However, there are a few factors that make it tricky to manage the life cycle of a
webhook, such as:

* Dealing with server failures on both the sending and the receiving end.
* Managing HTTP timeouts.
* Retrying the requests gracefully without overloading the recipients.
* Avoiding retry loop on the sending side.
* Monitoring and providing scope for manual interventions.
* Scaling them quickly; either vertically or horizontally.
* Decoupling webhook management logic from your primary application logic.

Properly dealing with these concerns can be cumbersome; especially when sending webhooks
is just another small part of your application and you just want it to work without you
having to deal with all the hairy details every time. Hook Slinger aims to alleviate
this pain point.

### How?

Hook Slinger exposes a single endpoint where you can post your webhook payload,
destination URL, auth details, and it'll make the POST request for you asynchronously in
the background. Under the hood, the service uses:

* [FastAPI][fastapi] to provide a [Uvicorn][uvicorn] driven [ASGI][asgi] server.

* [Redis][redis] and [RQ][rq] for implementing message queues that provide the
asynchrony and robust failure handling mechanism.

* [Rqmonitor][rqmonitor] to provide a dashboard for monitoring the status of the
webhooks and manually retrying the failed jobs.

* [Rich][rich] to make the container logs colorful and more human friendly.

The simplified app architecture looks something this:

![Topology][topology]

In the above image, the webhook payload is first sent to the `app` and the `app`
leverages the `worker` instance to make the POST request. Redis DB is used for fast
bookkeeping and async message queue implementation. The `monitor` instance provides a
GUI to monitor and manage the webhooks. Multiple `worker` instances can be spawned to
achieve linear horizontal scale-up.

## Installation

* Make sure you've got the latest version of [Docker][docker] and
[Docker Compose V2][docker-compose] installed in your system.

* Clone the repository and head over to the root directory.

* To start the orchestra, run:

    ```
    make start-servers
    ```

    This will:

    * Start an `app` server that can be accessed from port `5000`.

    * Start an Alpine-based Redis server that exposes port `6380`.

    * Start a single `worker` that will carry out the actual tasks.

    * Start a `rqmonitor` instance that opens port `8899`.

* To shut down everything, run:

    ```
    make stop-servers
    ```

*TODO: Generalize it more before making it installable with a `docker pull` command.*

## Usage

### Exploring the interactive API docs

To try out the entire workflow interactively, head over to the following URL on your
browser:

```
http://localhost:5000/docs
```

You should see a panel like this:

![API Docs][api-docs]

This app implements a rudimentary token-based authentication system where you're
expected to send an API token by adding `Authorization: Token <token_value>` field to
your request header. To do that here, click the `POST /hook_slinger/` ribbon and that
will reveal the API description like this:

![API Description][api-description]

Copy the default token value from the description corpus, then click the green button on
the top right that says **Authorize**, and paste the value in the prompt box. Click
the **Authorize** button again and that'll conclude the login step. In your production
application, you should implement a robust authentication system or at least change this
default token.

To send a webhook, you'll need a URL where you'll be able to make the POST request. For
this demonstration, let's pick this [webhook site][webhook-site-url] service to
monitor the received webhooks. It gives you a unique URL against which you'll be able to
make the post requests and monitor them in a dashboard like this:


![Webhook Site][webhook-site]

On the API docs page, click the **Try it out** button near the **request body** section:

![API Request][api-request]

This should reveal a panel like the following one where you can make your request:

![API Request][api-request-2]

Notice that the section is prefilled with an example request payload. You can use this
exact payload to make a request. Go ahead and click the execute button. If you scroll
down a little, you'll notice the HTTP response:


![API Response][api-response]

Now, if you head over to the [webhook site][webhook-site-url-detail] URL, you should be
able to see your API payload:


![API Response][api-response-2]

To monitor the webhook tasks, head over to the following URL:

```
http://localhost:8899/
```

You should be presented with a GUI like this:

![RQ Monitor][rq-monitor]

If you click **Workers** on the left panel, you'll be presented with a panel where you
can monitor all the workers:

![RQ Monitor][rq-monitor-2]


The **Jobs** panel lists all the tasks, and from there you'll be able to requeue a
failed job. By default, Hook Slinger retries a failed job 3 times with 5 seconds linear
backoff. However, this can be configured using environment variables in the `.env` file.

![RQ Monitor][rq-monitor-3]


### Sending a webhook via cURL

Run the following command on your terminal; this assumes that you haven't changed the
auth token (you should):

```sh
curl -X 'POST' \
  'http://localhost:5000/hook_slinger/' \
  -H 'accept: application/json' \
  -H 'Authorization: Token $5$1O/inyTZhNvFt.GW$Zfckz9OL.lm2wh3IewTm8YJ914wjz5txFnXG5XW.wb4' \
  -H 'Content-Type: application/json' \
  -d '{
  "to_url": "https://webhook.site/b30da7ce-c3cc-47e2-b2ae-68747b3d7789",
  "to_auth": "",
  "tag": "Dhaka",
  "group": "Bangladesh",
  "payload": {
    "greetings": "Hello, world!"
  }
}' | python -m json.tool
```

You should expect the following output:

```json
{
    "status": "queued",
    "ok": true,
    "message": "Webhook registration successful.",
    "job_id": "Bangladesh_Dhaka_a07ca786-0b7a-4029-bac0-9a7c6eb68a98",
    "queued_at": "2021-11-06T16:54:54.728999"
}
```

### Sending a webhook via Python

For this purpose, you can use an HTTP library like [httpx][httpx].

Make the request with the following script:

```python
import asyncio
from http import HTTPStatus
from pprint import pprint

import httpx


async def send_webhook() -> None:
    wh_payload = {
        "to_url": "https://webhook.site/b30da7ce-c3cc-47e2-b2ae-68747b3d7789",
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
```

This should return a similar response as before:

```
{
    'job_id': 'Bangladesh_Dhaka_139fc35a-d2a5-4d01-a6af-e980c52f55bc',
    'message': 'Webhook registration successful.',
    'ok': True,
    'queued_at': '2021-07-23T20:15:04.389690',
    'status': 'queued'
}
```

### Exploring the container logs

Hook Slinger overloads the Python root logger to give you a colorized and user-friendly
logging experience. To explore the logging messages of the application server, run:

```
make app-logs
```

Notice the colorful logs cascading down from the app server:

![App Logs][app-logs]

Now, to explore the worker instance logs, in a separate terminal, run:

```
make worker-logs
```

You should see something like this:

![Worker Logs][worker-logs]


### Scaling up the service

Hook Slinger offers easy horizontal scale-up, powered by the `docker-compose --scale`
command. In this case, scaling up means, spawning new workers in separate containers.
Let's spawn 3 worker containers this time. To do so, first shut down the orchestra by
running:

```
make stop-servers
```

Now, run:

```
make worker-scale n=3
```

This will start the **App server**, **Redis DB**, **RQmonitor**, and 3 **Worker**
instances. Spawning multiple worker instances are a great way to achieve job concurrency
with the least amount of hassle.

### Troubleshooting

On the Rqmonitor dashboard, if you see that your webhooks aren't reaching the
destination, make sure that the destination URL in the webhook payload can accept the
POST requests sent by the workers. Your webhook payload looks like this:

```
{
    "to_url": "https://webhook.site/f864d28d-9162-4ad5-9205-458e2b561c07",
    "to_auth": "",
    "tag": "Dhaka",
    "group": "Bangladesh",
    "payload": {"greetings": "Hello, world!"},
}

```

Here, `to_url` must be able to receive the payloads and return HTTP code 201.

## Philosophy & limitations

Hooks Slinger is designed to be simple, transparent, upgradable, and easily extensible
to cater to your specific needs. It's not built around AMQP compliant message queues
with all the niceties and complexities that come with them—this is intentional.

Also, if you scrutinize the end-to-end workflow, you'll notice that it requires making
HTTP requests from the sending service to the Hook Slinger. This inevitably adds another
point of failure. However, from the sending service's POV, it's sending the HTTP
requests to a single service, and the target service is responsible for fanning out the
webhooks to the destinations. The developers are expected to have control over both
services, which theoretically should mitigate the failures. The goal is to transfer
some of the code complexity around managing webhooks from the sending service over to
the Hook Slinger. Also, I'm playing around with some of the alternatives to using HTTP
POST requests to send the payloads from the sending end to the Hook Slinger. Suggestions
are always appreciated.


<div align="center">
<i> ✨ 🍰 ✨ </i>
</div>

[logo]: https://user-images.githubusercontent.com/30027932/126405827-8b859b4c-89cd-40c8-a7d3-fe6e9fc64770.png
[forthebadge]: https://forthebadge.com
[black-magic-badge]: https://forthebadge.com/images/badges/powered-by-black-magic.svg
[build-with-love-badge]: https://forthebadge.com/images/badges/built-with-love.svg
[made-with-python-badge]: https://forthebadge.com/images/badges/made-with-python.svg
[webhook-concept]: ./art/webhook_concept.png
[fastapi]: https://fastapi.tiangolo.com/
[uvicorn]: https://www.uvicorn.org/
[asgi]: https://asgi.readthedocs.io/en/latest/#
[redis]: https://redis.io/
[rq]: https://python-rq.org/docs/jobs/
[rqmonitor]: https://github.com/pranavgupta1234/rqmonitor
[rich]: https://github.com/willmcgugan/rich
[topology]: ./art/topology.png
[docker]: https://www.docker.com/
[docker-compose]: https://docs.docker.com/compose/cli-command/
[api-docs]: ./art/api_docs.png
[api-description]: ./art/api_descr.png
[webhook-site]: ./art/webhook_site.png
[webhook-site-url]: https://webhook.site/
[webhook-site-url-detail]: https://webhook.site/#!/f864d28d-9162-4ad5-9205-458e2b561c07
[api-request]: ./art/api_request.png
[api-request-2]: ./art/api_request_2.png
[api-response]: ./art/api_response.png
[api-response-2]: ./art/api_response_2.png
[rq-monitor]: ./art/rq_monitor.png
[rq-monitor-2]: ./art/rq_monitor_2.png
[rq-monitor-3]: ./art/rq_monitor_3.png
[app-logs]: ./art/app_logs.png
[worker-logs]: ./art/worker_logs.png
[httpx]: https://www.python-httpx.org
