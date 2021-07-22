import os
import uuid

from dotenv import load_dotenv

load_dotenv(".env")

# By default data lives in the db for 7 days.
PAYLOAD_TTL = int(os.environ["PAYLOAD_TTL"])

HTTP_TIMEOUT = int(os.environ["HTTP_READ_TIMEOUT"])

# SHA-256 simple token
API_TOKEN = os.environ["API_TOKEN"]

# Retries
MAX_RETRIES = int(os.environ["MAX_RETRIES"])
INTERVAL = int(os.environ["INTERVAL"])

# This block is picked up by RQ workers, don't change variable names.
REDIS_URL = os.environ["REDIS_URL"]

QUEUE_NAME = os.environ["QUEUE_NAME"]
WORKER_NAME = f"{os.environ['WORKER_NAME_PREFIX']}_{str(uuid.uuid4())}"
