import os
import uuid

from dotenv import load_dotenv

load_dotenv(".env")


# Webhook post timeout in seconds.
HTTP_TIMEOUT: int = int(os.environ.get("HTTP_TIMEOUT", 30))

# Redis.
REDIS_URL: str = os.environ.get("REDIS_URL", "redis://redis:6380/1")

# API token, SHA-256 key.
API_TOKEN: str = os.environ.get(
    "API_TOKEN", "$5$1O/inyTZhNvFt.GW$Zfckz9OL.lm2wh3IewTm8YJ914wjz5txFnXG5XW.wb4"
)

# Retry parameters.
MAX_RETRIES: int = int(os.environ.get("MAX_RETRIES", 3))
INTERVAL: int = int(os.environ.get("INTERVAL", 5))

# Message queue configs.
QUEUE_NAME: str = os.environ.get("QUEUE_NAME", "webhook_queue")
WORKER_NAME_PREFIX: str = os.environ.get(
    "WORKER_NAME_PREFIX",
    "webhook_queue_consumer",
)
WORKER_NAME = f"{WORKER_NAME_PREFIX}_{str(uuid.uuid4())}"


# Log.
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
